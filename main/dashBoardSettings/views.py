from django.contrib.auth.decorators import login_required
from .models import LeadSearchSetting, ApiKey, LocationPoints
from google_engine.utils import search_google_places
from ai_engine.utils import get_high_traffic_points
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from logs.views import add_log
import uuid
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse


@login_required
def update_lead_settings(request):
    if request.method == 'POST':
        setting, _ = LeadSearchSetting.objects.get_or_create(user=request.user)
        setting.numbLeads = request.POST.get('numbLeads', setting.numbLeads)
        setting.save()
        messages.success(request, "Lead search settings updated successfully.")
        job_id = str(uuid.uuid4())
        add_log(job_id, "Gold", "Updated lead search settings", "short", request.user)
    return redirect('settings')

@login_required
def update_ApiKey_settings(request):
    if request.method == 'POST' and request.user.is_superuser:
        updated = False
        for key_id_str, key_value in request.POST.items():
            if key_id_str.startswith('api_key_'):
                try:
                    key_id = int(key_id_str.split('_')[2])
                    api_key_obj = ApiKey.objects.get(id=key_id, user=request.user)
                    api_key_obj.key = key_value
                    api_key_obj.save()
                    updated = True
                except (ValueError, ApiKey.DoesNotExist):
                    continue
        if updated:
            messages.success(request, "API keys updated successfully.")
            job_id = str(uuid.uuid4())
            add_log(job_id, "Gold", "Updated API keys", "short", request.user)
    return redirect('settings')
    
@login_required
def add_api_key(request):
    if request.method == 'POST' and request.user.is_superuser:
        name = request.POST.get('name')
        key = request.POST.get('key')
        if name and key:
            ApiKey.objects.create(user=request.user, name=name, key=key)
            messages.success(request, f"API key '{name}' added successfully.")
            job_id = str(uuid.uuid4())
            add_log(job_id, "Gold", f"Added API key {name}", "short", request.user)
        else:
            messages.error(request, "Please provide both a name and an API key.")
    return redirect('settings')


@login_required
def add_keywords(request):
    if request.method == 'POST':
        new_keywords_raw = request.POST.get('keywords', '')
        # Split keywords by comma, strip whitespace, ignore empty strings
        new_keywords = [k.strip() for k in new_keywords_raw.split(',') if k.strip()]

        if not new_keywords:
            messages.error(request, "Please enter at least one keyword.")
            return redirect('settings')

        # Get or create LeadSearchSetting for user
        lead_settings, created = LeadSearchSetting.objects.get_or_create(user=request.user)

        # Combine existing keywords and new keywords, avoiding duplicates
        existing = set(lead_settings.keywords or [])
        updated = list(existing.union(new_keywords))

        lead_settings.keywords = updated
        lead_settings.save()

        messages.success(request, f"Added keywords: {', '.join(new_keywords)}")
        job_id = str(uuid.uuid4())
        add_log(job_id, "Gold", f"Added keywords: {', '.join(new_keywords)}", "short", request.user)
        return redirect('settings')

    # For GET, show a simple form or redirect
    return redirect('settings')


@login_required
def get_location(request):
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        loc_input = request.POST.get('location_name', '').strip()
        if not loc_input:
            return JsonResponse({'error': 'Please enter a location.'}, status=400)

        geo_data = search_google_places(loc_input)
        if geo_data.get('status') != 'OK':
            return JsonResponse({'error': 'Could not geocode the location.'}, status=400)

        loc = geo_data['results'][0]['geometry']['location']
        lat, lng = loc['lat'], loc['lng']

        high_traffic_points = get_high_traffic_points(lat, lng)

        # Return points as JSON
        return JsonResponse({'points': high_traffic_points})

    # Non-AJAX fallback or GET can redirect or error
    return JsonResponse({'error': 'Invalid request.'}, status=400)


@login_required
@csrf_exempt
@require_POST
def save_updated_points(request):
    location_name = request.POST.get('location_name', '').title()
    points_raw = request.POST.get('points', '[]')

    try:
        points_data = json.loads(points_raw)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid points data'}, status=400)

    if not location_name or not points_data:
        return JsonResponse({'error': 'Location name and points are required.'}, status=400)

    # Check if user already has a location with the same name
    if LocationPoints.objects.filter(user=request.user, location_name=location_name).exists():
        return JsonResponse({'error': f'You already have a location named "{location_name}".'}, status=400)

    # Save to database
    location = LocationPoints.objects.create(
        user=request.user,
        location_name=location_name,
        points=points_data
    )

    messages.success(request, f"Added Location: {location_name}")
    job_id = str(uuid.uuid4())
    short_log = add_log(job_id, "Gold", f"Added location {location_name}", "short", request.user)
    add_log(job_id, "Gold", f"Saved points: {points_data}", "long", request.user, short_log.id)
    return JsonResponse({'message': 'Points saved successfully.', 'id': location.id})



@login_required
def get_location_points(request, location_id):
    location = get_object_or_404(LocationPoints, id=location_id, user=request.user)
    return JsonResponse({'points': location.points})

@login_required
@csrf_exempt
@require_POST
def save_updated_location(request, location_id):
    location = get_object_or_404(LocationPoints, id=location_id, user=request.user)
    points_raw = request.POST.get('points', '[]')

    try:
        points_data = json.loads(points_raw)
    except json.JSONDecodeError:
        messages.error(request, "Invalid points data.")
        return redirect('settings')  # Or wherever you want to go

    if not points_data:
        messages.error(request, "Points are required.")
        return redirect('settings')

    location.points = points_data
    location.save()

    messages.success(request, "Points updated successfully.")
    job_id = str(uuid.uuid4())
    short_log = add_log(job_id, "Gold", f"Updated location {location.location_name}", "short", request.user)
    add_log(job_id, "Gold", f"New points: {points_data}", "long", request.user, short_log.id)
    return JsonResponse({'message': 'Points edite successfully.', 'id': location.id})

@login_required
@csrf_exempt
@require_POST
def delete_location(request, location_id):
    location = get_object_or_404(LocationPoints, id=location_id, user=request.user)
    location_name = location.location_name
    location.delete()
    messages.success(request, f'Location "{location_name}" has been deleted.')
    job_id = str(uuid.uuid4())
    add_log(job_id, "Gold", f"Deleted location {location_name}", "short", request.user)
    return JsonResponse({'message': 'Location deleted successfully.'})


