# ai_engine/utils.py

import time
import json
import re
import ast
import openai
from dashBoardSettings.models import ApiKey
from logs.views import add_log

def openaiKey():
    api_key_obj = ApiKey.objects.filter(name="OpenAI Key").first()
    if not api_key_obj or not api_key_obj.key:
         raise ValueError("OpenAI API key not found")
    return api_key_obj.key

def call_openai(prompt, system_message="You are a helpful assistant.",
                model="gpt-4", temperature=0.3, max_tokens=500):
    openai.api_key = openaiKey()

    for attempt in range(3):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user",   "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            wait = 10 + attempt*5
            time.sleep(wait)
        except Exception:
            break
    return ""


# --- Helpers to get keywords & coords from AI ---
def call_openai_to_get_keywords(desc):
    prompt = f"""You're an expert lead gen AI. Given: "{desc}"
Return a Python list of search terms matching this need. Only the list."""
    out = call_openai(prompt, model="gpt-3.5-turbo", max_tokens=100)
    try:
        lst = ast.literal_eval(out)
        return lst if isinstance(lst, list) else []
    except Exception:
        return []


def extract_json_array(text):
    m = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except Exception:
        return []



def is_good_lead_ai(user, job_id, linked_log,biz):
    add_log(job_id, "Gold", f"🚀 Starting AI analysis for business: {biz.get('name')}.", "long", user, linked_log)
    clean_text = (
        f"Business Name: {biz.get('name')}\n"
        f"Business Types: {', '.join(biz.get('types', []))}"
    )
    
    prompt = f"""
You are a business analyst.

Based only on the business name and types below, determine:
1. If this business would be a good candidate for placing vending machines.
2. How easy it would be to contact the decision-maker (e.g., owner, manager) without going through a large organization or committee.

Give your assessment strictly in this JSON format:

{{
  "recommendation": "Yes" or "No",
  "reasons": [
    "reason 1",
    "reason 2",
    "reason 3"
  ],
  "contactability": "Easy" or "Difficult" or "Unknown"
}}

Business Information:
\"\"\" 
{clean_text}
\"\"\"
"""
    add_log(job_id, "Gold", f"🔍 Sending prompt to AI for business '{biz.get('name')}'.", "long", user, linked_log)
    
    response = call_openai(prompt, temperature=0, max_tokens=500)

    if not response:
        add_log(job_id, "Bronze", f"[AI] No response received for business '{biz.get('name')}'.", "long", user, linked_log)
        return {
            "recommendation": "No",
            "reasons": ["AI returned no response."],
            "contactability": "Unknown"
        }    
    try:
        parsed = json.loads(response)
        # Log successful response parsing
        add_log(job_id, "Gold", f"✅ AI response parsed successfully for business '{biz.get('name')}'.", "long", user, linked_log)
    except json.JSONDecodeError:
        # Handle parsing errors and log them
        add_log(job_id, "Bronze", f"[AI] Error parsing AI response for business '{biz.get('name')}'. Response: {response}", "long", user, linked_log)

        match = re.search(r'\{.*\}', response, re.DOTALL)

        if match:
            parsed = json.loads(match.group(0))
            add_log(job_id, "Gold", f"✅ Extracted valid JSON from AI response for business '{biz.get('name')}'.", "long", user, linked_log)
        else:
            parsed = {
                "recommendation": "No",
                "reasons": ["Could not parse AI response."],
                "contactability": "Unknown"
            }
    # Log the final decision from AI
    recommendation = parsed.get("recommendation", "No")
    contactability = parsed.get("contactability", "Unknown")
    reasons = ', '.join(parsed.get("reasons", []))     
     
    add_log(job_id, "Gold", f"📊 AI analysis for business '{biz.get('name')}' completed. Recommendation: {recommendation}, Contactability: {contactability}. Reasons: {reasons}.", "long", user, linked_log)

    return parsed


def chunk_html(html, size=15000):
    for i in range(0, len(html), size):
        yield html[i:i+size]

def build_chunk_prompt(chunk):
    return f"""
Analyze this HTML chunk and extract any of the following if found:

- Email addresses
- Phone numbers
- Contact page URL
- About page URL

Return JSON with any info you find in this chunk. If none found, return empty lists/strings.

{{
  "emails": [...],
  "phone_numbers": [...],
  "contact_url": "...",
  "about_url": "..."
}}

HTML chunk:
{chunk}
"""

def filter_url(url, domain):
    if not url:
        return ''
    url_lower = url.lower()
    # Filter out Google Maps or external map URLs
    if 'google.com/maps' in url_lower or 'maps.google.com' in url_lower:
        return ''
    # Filter URLs not belonging to the domain (optional)
    if domain and domain not in url_lower:
        return ''
    return url

def extract_info_chunked(html, domain=None):
    emails = set()
    phones = set()
    contact_url = None
    about_url = None

    for chunk in chunk_html(html):
        prompt = build_chunk_prompt(chunk)
        response_json = extract_info_with_openai(prompt)  # Your GPT wrapper function

        if not response_json:
            continue

        emails.update(response_json.get('emails', []))
        phones.update(response_json.get('phone_numbers', []))

        # Filter contact URL to avoid unwanted URLs
        candidate_contact_url = filter_url(response_json.get('contact_url'), domain)
        if not contact_url and candidate_contact_url:
            contact_url = candidate_contact_url

        # Filter about URL to avoid unwanted URLs
        candidate_about_url = filter_url(response_json.get('about_url'), domain)
        if not about_url and candidate_about_url:
            about_url = candidate_about_url

        # Break early if all info found
        if emails and phones and contact_url and about_url:
            break

    return {
        'emails': list(emails),
        'phone_numbers': list(phones),
        'contact_url': contact_url or '',
        'about_url': about_url or ''
    }


def extract_info_with_openai(prompt):
    # call_openai is your wrapper from before
    content = call_openai(prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=500)

    if not content:
        return {}

    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}
    except json.JSONDecodeError:
        return {}
    


def analyze_company_for_vending(clean_text):
    prompt = f"""
You are a business analyst.

Based on the following company description, analyze if this company would be a good candidate for vending machines on their premises.

Please respond ONLY in JSON with these fields:

{{
  "recommendation": "Yes" or "No",
  "reasons": [
    "reason 1",
    "reason 2",
    "reason 3"
  ]
}}

Company description:
\"\"\"
{clean_text}
\"\"\"
"""
    response = call_openai(prompt, temperature=0, max_tokens=400)
    return response


def get_high_traffic_points(lat, lng):
    api_key = openaiKey()  # Get your OpenAI API key from DB
    openai.api_key = api_key

    prompt = f"""
You are a city data analyst.

Given the geographic coordinates latitude={lat}, longitude={lng}, and the neighborhood or area name corresponding to these coordinates, provide a JSON array of 3 to 5 points strictly within that neighborhood or area that represent locations with high foot traffic or popular public areas suitable for placing vending machines.

Do NOT include points outside the specified neighborhood.

Return ONLY a JSON array like this:

[
  {{
    "latitude": 36.11,
    "longitude": -115.17
  }},
  {{
    "latitude": 36.12,
    "longitude": -115.18
  }}
]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or your preferred model
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )

        text = response['choices'][0]['message']['content'].strip()

        # Try to parse JSON from response
        high_traffic_points = json.loads(text)
        # Basic validation: make sure it is a list of dicts with lat/lng keys
        valid_points = []
        for pt in high_traffic_points:
            if (
                isinstance(pt, dict)
                and "latitude" in pt
                and "longitude" in pt
                and isinstance(pt["latitude"], (int, float))
                and isinstance(pt["longitude"], (int, float))
            ):
                valid_points.append(pt)

        return valid_points

    except Exception:
        # Fallback: return a few simple points near original lat/lng
        return [
            {"latitude": lat + 0.001, "longitude": lng + 0.001},
            {"latitude": lat - 0.001, "longitude": lng - 0.001},
            {"latitude": lat + 0.002, "longitude": lng - 0.0015},
        ]