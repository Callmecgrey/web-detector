import logging
from bs4 import BeautifulSoup

def parse_html_content(html_content):
    """
    Parses the HTML content using BeautifulSoup and returns a soup object.
    If parsing fails, logs the error and returns None.
    """
    try:
        return BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        logging.error(f"Error parsing HTML content: {e}")
        return None
