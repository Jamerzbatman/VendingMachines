from dashBoardSettings.models import ApiKey
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
        print(f"[PlaceDetailsAPI] Error: {response.status_code} - {response.text}")
        return {}

    data = response.json()
    if 'error_message' in data:
        print(f"[PlaceDetailsAPI] API error: {data['error_message']}")
        return {}

    return data.get('result', {})

def search_google_places(location, keywords, radius_meters=1500):
    if not keywords:
        return []

    api_key = get_google_api_key()
    all_results = []

    for keyword in keywords:
        params = {
            "location": location,  # must be a string "lat,lng"
            "radius": radius_meters,
            "keyword": keyword,
            "key": api_key,
        }

        response = requests.get(GOOGLE_PLACES_BASE_URL, params=params)

        if response.status_code != 200:
            print(f"[PlacesAPI] Error: {response.status_code} - {response.text}")
            continue

        data = response.json()

        if 'error_message' in data:
            print(f"[PlacesAPI] API error: {data['error_message']}")
            continue

        all_results.extend(data.get('results', []))

    # Deduplicate by place_id
    unique = {place['place_id']: place for place in all_results}
    enriched_results = []

    for place_id, place in unique.items():
        details = get_place_details(place_id, api_key)

        website = details.get('website', None)
        if website:
            place['website'] = website
        enriched_results.append(place)
        # Optional: avoid hitting API rate limits
        time.sleep(0.2)

    return enriched_results


def search_google_geo_places(loc_input):
    api_key = get_google_api_key()
    geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': loc_input, 'key': api_key}
    geo_resp = requests.get(geo_url, params=params)
    geo_data = geo_resp.json()
    return geo_data