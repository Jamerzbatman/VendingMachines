# scrap/utils.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

def get_rendered_html(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale="en-US",
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True  # <-- ADD THIS
            )
            page = context.new_page()
            page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br"
            })
            page.goto(url, wait_until="domcontentloaded", timeout=30000)  # <-- safer wait
            page.wait_for_timeout(7000)  # wait 7 seconds for any async JS
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"[Playwright Error] {e}")
        return ""
    


def extract_emails_from_html(html):
    if not html:
        return []

    # Basic regex to find emails
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, html)

    # Remove duplicates
    unique_emails = list(set(emails))
    
    return unique_emails

def extract_phone_numbers_from_html(html):
    if not html:
        return []

    # Find numbers
    phone_pattern = r'(\+?1\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}'
    phones = re.findall(phone_pattern, html)

    flat_phones = []
    for match in phones:
        phone = ''.join(match)  # Join the capture groups
        phone = re.sub(r'[^\d]', '', phone)  # Keep only digits
        
        # Validate US phone numbers: 10 or 11 digits (with leading 1)
        if len(phone) == 10 or (len(phone) == 11 and phone.startswith('1')):
            flat_phones.append(phone)

    unique_phones = list(set(flat_phones))
    
    return unique_phones


def find_contact_page_url(base_url, html):
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    contact_links = []

    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        text = (link.get_text() or '').lower()

        if 'contact' in href or 'contact' in text:
            contact_links.append(href)

    if not contact_links:
        return None

    # Prefer a link that starts with '/' or is relative
    contact_links = sorted(contact_links, key=lambda x: 0 if x.startswith('/') else 1)

    # Take the first reasonable contact link
    contact_url = contact_links[0]

    # If it's a relative URL, combine it with the base
    if contact_url.startswith('/'):
        from urllib.parse import urljoin
        contact_url = urljoin(base_url, contact_url)

    return contact_url


def find_about_page_url(base_url, html):
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    about_links = []

    # Keywords we are looking for in about pages
    about_keywords = ['about', 'our-story', 'who-we-are', 'company', 'mission']

    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        text = (link.get_text() or '').lower()

        if any(keyword in href for keyword in about_keywords) or any(keyword in text for keyword in about_keywords):
            about_links.append(href)

    if not about_links:
        return None

    # Prefer a link that starts with '/' or is relative
    about_links = sorted(about_links, key=lambda x: 0 if x.startswith('/') else 1)

    # Take the first reasonable about link
    about_url = about_links[0]

    # If it's a relative URL, combine it with the base
    if about_url.startswith('/'):
        from urllib.parse import urljoin
        about_url = urljoin(base_url, about_url)

    return about_url




def extract_clean_text(html, max_chars=15000):
    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style tags
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Truncate if needed
    if len(text) > max_chars:
        text = text[:max_chars]

    return text