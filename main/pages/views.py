from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware

from datetime import datetime
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

from functools import lru_cache

from dashBoardSettings.models import LeadSearchSetting, ApiKey, LocationPoints
from leads.models import Lead
from logs.models import Log



@lru_cache(maxsize=1)          # avoids a DB hit on every request
def get_api_key(key):
    """
    Return the single Google API key stored in the DB.
    Raises ApiKey.DoesNotExist if you haven't created it yet.
    """
    return ApiKey.objects.get(name=key).key 

# home pages.
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    google_api_key = get_api_key("Google API Key")
    return render(request, "pages/home.html", {"google_api_key": google_api_key})

def learnMore(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 
    
    google_api_key = get_api_key("Google API Key")
    return render(request, "pages/learnMore.html", {"google_api_key": google_api_key})  # Show home page if not logged in

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
    google_api_key = get_api_key("Google API Key")
    return render(request, "pages/aboutUs.html", {"google_api_key": google_api_key})  # Show home page if not logged in


def largeHotels(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    google_api_key = get_api_key("Google API Key")
    return render(request, "pages/largeHotels.html", {"google_api_key": google_api_key})  # Show home page if not logged in

def boutiqueHotels(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    google_api_key = get_api_key("Google API Key")
    return render(request, "pages/boutiqueHotels.html", {"google_api_key": google_api_key})  # Show home page if not logged in

def officeBuildings(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    google_api_key = get_api_key("Google API Key")
    return render(request, "pages/officeBuildings.html", {"google_api_key": google_api_key})  # Show home page if not logged in


def Get_Short_log(user):
    current_time = timezone.now()
    one_minute_ago = current_time - timedelta(minutes=1)
    recent_logs = Log.objects.filter(user=user, log_type='short', created_at__gte=one_minute_ago)
    return recent_logs



# Phone Pages 

def phoneBoutiqueHotels(request):
    return render(request, "phones/boutiqueHotels.html")

def phoneOfficeBuildings(request):
    return render(request, "phones/officeBuildings.html")

def phoneLargeHotels(request):
    return render(request, "phones/largeHotels.html")

def walkthrough(request):
    google_api_key = get_api_key("Google API Key")
    return render(request, "phones/walkthrough.html", {"google_api_key": google_api_key})

def phonePrivacy(request):
    return render(request, "phones/privacy.html")


# admin login 
@login_required
def dashboard(request):

    # Get the count of leads per source for today
    today = make_aware(datetime.now()).date()
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
        'recent_logs': Get_Short_log(request.user),
        'leads_count': leads_count,
        'is_website_new': is_website_new,
        'website_count' : leads_count['website'],
        'ai_count' : leads_count['ai'],
        "total_leads": Lead.objects.count(),
        'is_ai_new': is_ai_new,
        'leads_data': leads_data,
    }

    return render(request, "dashboard/dashboard.html", context) 



@login_required
def aiTools(request):

    context = {
        'recent_logs': Get_Short_log(request.user),
        "total_leads": Lead.objects.count(),
    }
    return render(request, "dashboard/aiTools.html", context)  # Show dashboard if logged in

@login_required
def leads(request):

    context = {
        'recent_logs': Get_Short_log(request.user),
        "total_leads": Lead.objects.count(),
        "leads" : Lead.objects.all().order_by('-created_at'),
        "api_keys" : ApiKey.objects.all()
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
       
        return render(request, 'dashboard/leads.html', context)

    # Full page render
    return render(request, 'dashboard/leads.html', context)


@login_required
def inventory(request):
    context = {
        'recent_logs': Get_Short_log(request.user),
        "total_leads": Lead.objects.count(),
    }

    return render(request, "dashboard/inventory.html", context)  # Show dashboard if logged in

@login_required
def reports(request):
    context = {
        'recent_logs': Get_Short_log(request.user),
        "total_leads": Lead.objects.count(),
    }
    return render(request, "dashboard/reports.html", context)  # Show dashboard if logged in

@login_required
def settings(request):

    setting, _ = LeadSearchSetting.objects.get_or_create(user=request.user)

    context = {
        'recent_logs': Get_Short_log(request.user),
        'setting': setting,
        "total_leads": Lead.objects.count(),
        'api_keys': ApiKey.objects.all(),
        'locations': LocationPoints.objects.filter(user=request.user)
    }
    return render(request, 'dashboard/settings.html', context)
