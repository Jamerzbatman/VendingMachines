from django.shortcuts import render, redirect
from django.shortcuts import render
from leads.models import Lead
from django.shortcuts import render, redirect
from dashBoardSettings.models import LeadSearchSetting, ApiKey, LocationPoints
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models import Count





# home pages.
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, "pages/home.html")  # Show home page if not logged in

def learnMore(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, "pages/learnMore.html")  # Show home page if not logged in

def terms(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, "pages/terms.html")  # Show home page if not logged in

def thankYou(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, "pages/thankYou.html")  # Show home page if not logged in

def privacy(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, "pages/privacy.html")  # Show home page if not logged in

def sellToUs(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, "pages/sellToUs.html")  # Show home page if not logged in

def aboutUs(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return render(request, "pages/aboutUs.html")  # Show home page if not logged in



# admin login 
@login_required
def dashboard(request):
    # Get today's date
    today = make_aware(datetime.now()).date()

    # Get the count of leads per source for today
    leads_by_source = Lead.objects.filter(created_at__date=today).values('source').annotate(count=Count('id'))

    # Create a dictionary to store the counts for each source
    leads_count = {
        'website': 0,
        'ai': 0,
    }

    # Collect the leads for each source
    leads_data = {
        'website': Lead.objects.filter(created_at__date=today, source='website'),
        'ai': Lead.objects.filter(created_at__date=today, source='ai'),
    }

    # Populate the dictionary with the counts
    for lead in leads_by_source:
        leads_count[lead['source']] = lead['count']

    # Check if any source has new leads
    is_website_new = leads_count['website'] > 0
    is_ai_new = leads_count['ai'] > 0

    # Pass total_leads, "new" flags, and leads_data to the template
    context = {
        'leads_count': leads_count,
        'is_website_new': is_website_new,
        'website_count' : leads_count['website'],
        'ai_count' : leads_count['ai'],
        'is_ai_new': is_ai_new,
        'leads_data': leads_data,  # Pass the data for the modal
    }

    return render(request, "dashboard/dashboard.html", context) 



@login_required
def aiTools(request):
    return render(request, "dashboard/aiTools.html")  # Show dashboard if logged in

@login_required
def leads(request):
    leads = Lead.objects.all().order_by('-created_at')
    api_keys = ApiKey.objects.all()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # ⬇️ Return only the table part
        return render(request, 'dashboard/leads.html', {'leads': leads, 'api_keys': api_keys})

    # Full page render
    return render(request, 'dashboard/leads.html', {'leads': leads, 'api_keys': api_keys})


@login_required
def inventory(request):
    return render(request, "dashboard/inventory.html")  # Show dashboard if logged in

@login_required
def reports(request):
    return render(request, "dashboard/reports.html")  # Show dashboard if logged in

@login_required
def settings(request):
    setting, _ = LeadSearchSetting.objects.get_or_create(user=request.user)

    context = {
        'setting': setting,
        'api_keys': ApiKey.objects.all(),
        'locations': LocationPoints.objects.filter(user=request.user)
    }
    return render(request, 'dashboard/settings.html', context)
