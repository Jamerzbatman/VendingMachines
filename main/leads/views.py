from ai_engine.utils import call_openai_to_get_keywords, is_good_lead_ai, extract_info_chunked, analyze_company_for_vending
from scrap.utils import get_rendered_html, extract_clean_text, extract_emails_from_html, extract_phone_numbers_from_html, find_contact_page_url, find_about_page_url
from google_engine.utils import search_google_places
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.cache import cache
from django.urls import reverse
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import Lead, LeadPhone, LeadEmail
from dashBoardSettings.models import LeadSearchSetting, LocationPoints,ApiKey
import threading
import uuid
import json
import time

def add_log(job_id, message):
    key = {job_id}
    logs = cache.get(key, [])
    logs.append(message)
    cache.set(key, logs, timeout=3600)


@csrf_exempt  # only if you're not using the CSRF token — otherwise omit this
def submitWebSiteLead(request):
    if request.method == 'POST':
        try:
            setup_time_raw = request.POST.get('setupTime')
            setup_time = datetime.strptime(setup_time_raw, '%Y-%m-%dT%H:%M')

            lead = Lead.objects.create(
                first_name=request.POST.get('firstName'),
                last_name=request.POST.get('lastName'),
                phone=request.POST.get('phone'),
                company_name=request.POST.get('companyName'),
                address=request.POST.get('address'),
                company_phone=request.POST.get('companyPhone'),
                num_machines=request.POST.get('numMachines'),
                setup_time=setup_time,
                source='website'
            )

            return JsonResponse({'success': True, 'redirect_url': reverse('thankYou')})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def saveLead(biz, goodOrBad_result):
    goodOrBad_reasons = goodOrBad_result.get("reasons", [])
    goodOrBad_recommendation = goodOrBad_result.get("recommendation", "No")  # Default to "No" if missing
    
    lead = Lead.objects.create(
        first_name="",
        last_name="",
        logo=biz.get('icon', ''),
        company_name=biz.get('name', ''),
        address=biz.get('vicinity', ''),
        location=f"{biz['geometry']['location']['lat']},{biz['geometry']['location']['lng']}",
        company_website=biz.get('website', ''),
        types=", ".join(biz.get('types', [])),
        source='ai',
        ai_recommendation=goodOrBad_recommendation,
        ai_reasons="\n".join(goodOrBad_reasons) if isinstance(goodOrBad_reasons, list) else str(goodOrBad_reasons)
    )
    return lead

def lead_generation_task(job_id, user):
    add_log(job_id, "🚀 Starting Lead Agent...")
    
    setting = LeadSearchSetting.objects.filter(user=user).first()
    numbLeads = setting.numbLeads
    keywords = setting.keywords
    locations = LocationPoints.objects.filter(user=user)

    qualified = 0
    checked = 0

    for location in locations:
        for loc in location.points:
            add_log(job_id, f"📍 Searching around location {loc}...")
            location_str = f"{loc['latitude']},{loc['longitude']}"
            places = search_google_places(location_str, keywords)
            existing_addresses = set(Lead.objects.values_list('address', flat=True))
            places = [place for place in places if place.get('vicinity', '') not in existing_addresses]
            add_log(job_id, f"🛡️ Filtered places — {len(places)} new leads remain after removing duplicates.")

            for biz in places:
                try:
                    checked += 1
                    goodOrBad = is_good_lead_ai(biz)
                    if isinstance(goodOrBad, str):
                        goodOrBad_result = json.loads(goodOrBad)
                    else:
                        goodOrBad_result = goodOrBad

                    if goodOrBad_result.get("recommendation", "").strip().lower() == "no":
                        add_log(job_id, f"❌ {biz.get('name', 'Unknown Business')} was not recommended.")
                        saveLead(biz, goodOrBad_result)
                        continue

                    if not biz.get('website'):
                        add_log(job_id, f"⚠️ {biz.get('name', 'Unknown Business')} has no website; saving basic info.")
                        saveLead(biz, goodOrBad_result)
                        continue

                    add_log(job_id, f"🌐 Fetching website content for {biz.get('name', 'Unknown Business')}...")
                    homeHtml = get_rendered_html(biz.get('website'))
                    emails = set(extract_emails_from_html(homeHtml))
                    phoneNumbers = set(extract_phone_numbers_from_html(homeHtml))

                    storyPage = find_about_page_url(biz.get('website'), homeHtml)
                    contactPage = find_contact_page_url(biz.get('website'), homeHtml)

                    if contactPage:
                        add_log(job_id, f"📄 Found Contact Page. Extracting contact info...")
                        contactHtml = get_rendered_html(contactPage)
                        emails.update(extract_emails_from_html(contactHtml))
                        phoneNumbers.update(extract_phone_numbers_from_html(contactHtml))

                    if storyPage:
                        add_log(job_id, f"📖 Found About Page. Analyzing for vending opportunity...")
                        storyHtml = get_rendered_html(storyPage)
                        clean_text = extract_clean_text(storyHtml, max_chars=15000)
                        analyze = analyze_company_for_vending(clean_text)
                        try:
                            result = json.loads(analyze)
                            recommendation = result.get("recommendation", "")
                            reasons = result.get("reasons", [])
                            add_log(job_id, f"🤖 AI Analysis for {biz['name']}: {recommendation.upper()} — {', '.join(reasons)}")
                            if "yes" in recommendation.lower():
                                qualified += 1
                        except json.JSONDecodeError:
                            result = goodOrBad_result  # fallback to the first AI result if second one fails

                        lead = saveLead(biz, result)

                        for phone in phoneNumbers:
                            LeadPhone.objects.create(lead=lead, phone_number=phone)

                        for email in emails:
                            LeadEmail.objects.create(lead=lead, email=email)

                        add_log(job_id, f"✅ Lead saved: {biz['name']}.")
                    else:

                        lead = saveLead(biz, goodOrBad_result)
                        for phone in phoneNumbers:
                             LeadPhone.objects.create(lead=lead, phone_number=phone)
                        for email in emails:
                             LeadEmail.objects.create(lead=lead, email=email)
                        add_log(job_id, f"✅ Lead saved: {biz['name']}.")

                    # Sleep a small amount to avoid hammering servers
                    time.sleep(5)

                    if qualified >= int(numbLeads):
                        break
                except Exception as e:
                    add_log(job_id, f"🔥 Error processing {biz.get('name', 'Unknown Business')}: {str(e)}")

            if qualified >= int(numbLeads):
                break
        if qualified >= int(numbLeads):
            break

    add_log(job_id, f"🎯 Finished — {qualified} qualified leads found after checking {checked} businesses.")
    cache.set({job_id}, "STOP")


@csrf_exempt
def lead_results(request, job_id):
    leads = cache.get(f"lead_results_{job_id}", [])
    html = render_to_string("partials/leadResults.html", {"leads":leads})
    return JsonResponse({"html":html})



# Endpoints
@csrf_exempt
def generate_leads(request):
    if request.method != "POST":
        return JsonResponse({"error":"Invalid request"}, status=400)

    job_id = str(uuid.uuid4())  # <-- Create a fresh job ID here

    threading.Thread(target=lead_generation_task, args=(job_id, request.user)).start()

    return JsonResponse({"job_id": job_id})


def lead_detail(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    data = {
        'id': lead.id,
        'first_name': lead.first_name,
        'last_name': lead.last_name,
        'company_name': lead.company_name,
        'address': lead.address,
        'location': lead.location,
        'company_website': lead.company_website,
        'num_machines': lead.num_machines,
        'types': lead.types,
        'setup_time': lead.setup_time.isoformat() if lead.setup_time else None,
        'source': lead.source,
        'ai_recommendation': lead.ai_recommendation,
        'ai_reasons': lead.ai_reasons,
        'created_at': lead.created_at.isoformat(),
        'phones': [phone.phone_number for phone in lead.phones.all()],
        'emails': [email.email for email in lead.emails.all()],
    }
    return JsonResponse(data)