import logging
from urllib.parse import urlparse
import tldextract

def validate_and_normalize_url(url):
    """
    Validates that the URL starts with http:// or https:// and that the domain is valid.
    Returns the normalized URL if valid, or None otherwise.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return None

    # Use tldextract to verify domain structure
    ext = tldextract.extract(parsed.netloc)
    if not ext.domain or not ext.suffix:
        logging.warning(f"URL seems to have an invalid domain: {url}")
        return None

    return url

def safe_get_attr(obj, attr, default=None):
    """
    Safely get attribute from a BeautifulSoup tag or return default if not present.
    """
    return obj.attrs.get(attr, default)
