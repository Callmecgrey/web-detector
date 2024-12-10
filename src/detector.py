import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore

from .parser import parse_html_content
from .technology_checks import (
    detect_cms,
    detect_js_frameworks,
    detect_css_frameworks,
    detect_analytics,
    detect_tag_managers,
    detect_rum_tools,
    detect_meta_tags,
    detect_server,
    detect_programming_languages,
    detect_cdn,
    detect_fonts,
    detect_deployment_platform,
    detect_ads_and_tracking,
    detect_payment_integrations
)
from .exceptions import DetectionError
from .config import REQUEST_TIMEOUT, MAX_RETRIES, BACKOFF_FACTOR

def get_session():
    session = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def detect_web_technologies(url):
    """
    Main function to detect web technologies from a given URL.
    Returns a dictionary of detected technologies or None if an error occurs.
    """
    logging.info(f"Starting detection for {url}")
    session = get_session()

    # Initialize results dictionary
    technologies = {
        'CMS': None,
        'JavaScript Frameworks': set(),
        'CSS Frameworks': set(),
        'Analytics': set(),
        'Tag Managers': set(),
        'RUM (Real User Monitoring)': set(),
        'Web Servers': None,
        'Programming Languages': set(),
        'Other Technologies': set(),
        'CDN': None,
        'Fonts': set(),
        'HTTPS': "Enabled" if url.startswith("https://") else "Not Enabled",
        'Deployment Platform': None
    }

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "WebDetector/1.0"})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the URL: {e}")
        return None

    html_content = response.text
    headers = response.headers
    cookies = response.cookies

    soup = parse_html_content(html_content)

    try:
        # Existing detections
        detect_cms(html_content, headers, cookies, technologies)
        detect_js_frameworks(soup, technologies)
        detect_css_frameworks(soup, technologies)
        detect_analytics(html_content, cookies, technologies)
        detect_tag_managers(html_content, technologies)
        detect_rum_tools(html_content, technologies)
        detect_meta_tags(soup, technologies)
        detect_server(headers, technologies)
        detect_programming_languages(html_content, headers, technologies)
        detect_cdn(headers, technologies)
        detect_fonts(soup, technologies)
        detect_deployment_platform(headers, technologies)

        # New detection functions added:
        detect_ads_and_tracking(html_content, technologies)
        detect_payment_integrations(html_content, technologies)

    except Exception as e:
        # Log exception but return partial results
        logging.exception("An unexpected error occurred during detection:")

    return technologies
