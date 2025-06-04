from dashBoardSettings.models import ApiKey
from logs.views import add_log
import requests
import time

GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GOOGLE_PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

def get_google_api_key():
    api_key_obj = ApiKey.objects.filter(name="Google API Key").first()
    if not api_key_obj:
        raise Exception("Google API key not found in database")
    return api_key_obj.key

def get_place_details(place_id, api_key):
    params = {
        "place_id": place_id,
        "fields": "name,website",
        "key": api_key
    }

    response = requests.get(GOOGLE_PLACE_DETAILS_URL, params=params)
    if response.status_code != 200:
        return {}

    data = response.json()
    if 'error_message' in data:
        return {}

    return data.get('result', {})

def search_google_places(user, job_id, linked_log, location, keywords, radius_meters=1500):
    if not keywords:
        add_log(job_id, "Bronze", "No keywords provided for Google Places search.", "long", user, linked_log)
        return []

    api_key = get_google_api_key()
    all_results = []

    # Log the start of the search process
    add_log(job_id, "Gold", f"🚀 Starting search for {len(keywords)} keywords around location {location}.", "long", user, linked_log)

    for keyword in keywords:
        # Log each keyword being searched
        add_log(job_id, "Gold", f"🔍 Searching with keyword: {keyword}...", "long", user, linked_log)

        params = {
            "location": location,  # must be a string "lat,lng"
            "radius": radius_meters,
            "keyword": keyword,
            "key": api_key,
        }

        response = requests.get(GOOGLE_PLACES_BASE_URL, params=params)

        if response.status_code != 200:
            add_log(job_id, "Bronze", f"[PlacesAPI] Error: {response.status_code} - {response.text}", "long", user, linked_log)
            continue

        data = response.json()

        if 'error_message' in data:
            add_log(job_id, "Bronze", f"[PlacesAPI] API error: {data['error_message']}", "long", user, linked_log)
            continue

        # Log successful response for the keyword
        add_log(job_id, "Gold", f"✅ API response for keyword '{keyword}' received. Found {len(data.get('results', []))} places.", "long", user, linked_log)

        all_results.extend(data.get('results', []))

    # Deduplicate by place_id
    unique = {place['place_id']: place for place in all_results}
    enriched_results = []

    # Log deduplication process
    add_log(job_id, "Gold", f"🔄 Deduplicating {len(all_results)} places by place_id.", "long", user, linked_log)

    for place_id, place in unique.items():
        # Enrich with place details
        details = get_place_details(place_id, api_key)

        website = details.get('website', None)
        if website:
            place['website'] = website
            # Log when a website is found for a place
            add_log(job_id, "Gold", f"🌐 Found website for {place.get('name', 'Unknown')} at {website}.", "long", user, linked_log)

        enriched_results.append(place)

        # Optional: avoid hitting API rate limits
        time.sleep(0.2)

    # Log the completion of the search
    add_log(job_id, "Gold", f"🎯 Finished processing {len(enriched_results)} unique places.", "long", user, linked_log)

    return enriched_results

def search_google_geo_places(loc_input):
    api_key = get_google_api_key()
    geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': loc_input, 'key': api_key}
    geo_resp = requests.get(geo_url, params=params)
    geo_data = geo_resp.json()
    return geo_data