from scrap.scrapers.google_maps_scraper import GoogleMapsScraper
from leads.models import Lead
from dashBoardSettings.models import LeadSearchSetting

def run_scraper_task(user):
    try:
        setting = LeadSearchSetting.objects.get(user=user)
    except LeadSearchSetting.DoesNotExist:
        # fallback defaults if no settings found
        location = "Las Vegas"
        keywords = "office, gym, warehouse"
    else:
        location = setting.location
        keywords = setting.keywords

    scraper = GoogleMapsScraper(keywords=keywords, location=location)
    results = scraper.scrape()

    for r in results:
        Lead.objects.create(**r)
