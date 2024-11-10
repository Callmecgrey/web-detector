import requests
from bs4 import BeautifulSoup
import re

def detect_web_technologies(url):
    try:
        # Check if HTTPS is used
        is_https = url.startswith("https://")

        # Fetch the website HTML content and headers
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize a dictionary to store detected technologies
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
            'HTTPS': "Enabled" if is_https else "Not Enabled",
            'Deployment Platform': None
        }

        # HTTP Headers Inspection
        headers = response.headers
        if 'X-Powered-By' in headers:
            powered_by = headers['X-Powered-By'].lower()
            if 'php' in powered_by:
                technologies['Programming Languages'].add('PHP')
            if 'asp.net' in powered_by:
                technologies['Programming Languages'].add('ASP.NET')
            technologies['Other Technologies'].add(headers['X-Powered-By'])
        if 'X-Drupal-Cache' in headers:
            technologies['CMS'] = 'Drupal'
        if 'X-Shopify-Stage' in headers:
            technologies['CMS'] = 'Shopify'
        
        # CMS Detection
        if re.search(r'wp-content|wp-includes', html_content):
            technologies['CMS'] = 'WordPress'
        elif re.search(r'Joomla', html_content):
            technologies['CMS'] = 'Joomla'
        elif re.search(r'Drupal', html_content):
            technologies['CMS'] = 'Drupal'
        elif re.search(r'cdn\.shopify\.com', html_content):
            technologies['CMS'] = 'Shopify'
        elif re.search(r'wix\.static', html_content):
            technologies['CMS'] = 'Wix'
        elif re.search(r'squarespace', html_content):
            technologies['CMS'] = 'Squarespace'

        # JavaScript Frameworks Detection via Script Tags
        for script in soup.find_all('script', src=True):
            src = script['src'].lower()
            if 'jquery' in src:
                technologies['JavaScript Frameworks'].add('jQuery')
            elif 'angular' in src:
                technologies['JavaScript Frameworks'].add('Angular')
            elif 'react' in src:
                technologies['JavaScript Frameworks'].add('React')
            elif 'vue' in src:
                technologies['JavaScript Frameworks'].add('Vue.js')
            elif 'ember' in src:
                technologies['JavaScript Frameworks'].add('Ember.js')

        # JavaScript Variable Detection
        inline_scripts = soup.find_all('script', src=False)
        for script in inline_scripts:
            if re.search(r'window\.React', script.string or ''):
                technologies['JavaScript Frameworks'].add('React')
            if re.search(r'window\.angular', script.string or ''):
                technologies['JavaScript Frameworks'].add('Angular')
            if re.search(r'var\s+\$', script.string or '') and 'jQuery' not in technologies['JavaScript Frameworks']:
                technologies['JavaScript Frameworks'].add('jQuery')

        # CSS Frameworks Detection
        for link in soup.find_all('link', href=True):
            href = link['href'].lower()
            if 'bootstrap' in href:
                technologies['CSS Frameworks'].add('Bootstrap')
            elif 'tailwind' in href:
                technologies['CSS Frameworks'].add('Tailwind CSS')
            elif 'bulma' in href:
                technologies['CSS Frameworks'].add('Bulma')
            elif 'foundation' in href:
                technologies['CSS Frameworks'].add('Foundation')

        # Analytics Detection
        if re.search(r'gtag\(|ga\(|google-analytics\.com', html_content):
            technologies['Analytics'].add('Google Analytics')
        if re.search(r'fbq\(|facebook-pixel', html_content):
            technologies['Analytics'].add('Facebook Pixel')
        if re.search(r'hotjar', html_content):
            technologies['Analytics'].add('Hotjar')

        # Tag Managers Detection
        if re.search(r'googletagmanager', html_content):
            technologies['Tag Managers'].add('Google Tag Manager')
        
        # Real User Monitoring (RUM) Tools Detection
        if re.search(r'newrelic', html_content):
            technologies['RUM (Real User Monitoring)'].add('New Relic')
        if re.search(r'datadog', html_content):
            technologies['RUM (Real User Monitoring)'].add('Datadog')

        # Meta Tags Analysis
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if 'property' in tag.attrs and tag['property'].startswith('og:'):
                technologies['Other Technologies'].add('Open Graph (Facebook)')
            if 'name' in tag.attrs:
                name = tag['name'].lower()
                if 'generator' in name and 'wordpress' in tag.get('content', '').lower():
                    technologies['CMS'] = 'WordPress'
        
        # Web Server Detection
        server_header = headers.get('Server', '').lower()
        if 'apache' in server_header:
            technologies['Web Servers'] = 'Apache'
        elif 'nginx' in server_header:
            technologies['Web Servers'] = 'Nginx'
        elif 'cloudflare' in server_header:
            technologies['Web Servers'] = 'Cloudflare'
            technologies['CDN'] = 'Cloudflare'
        elif 'microsoft-iis' in server_header:
            technologies['Web Servers'] = 'Microsoft-IIS'
        
        # Programming Language Detection via Headers
        if 'php' in headers.get('X-Powered-By', '').lower() or re.search(r'\.php', html_content):
            technologies['Programming Languages'].add('PHP')

        # Cookies Detection
        cookies = response.cookies
        for cookie in cookies:
            if 'google' in cookie.name.lower():
                technologies['Analytics'].add('Google Analytics')
            if 'hotjar' in cookie.name.lower():
                technologies['Analytics'].add('Hotjar')
            if 'wordpress' in cookie.name.lower():
                technologies['CMS'] = 'WordPress'

        # Font Detection
        for link in soup.find_all('link', href=True):
            if 'fonts.googleapis' in link['href']:
                technologies['Fonts'].add('Google Fonts')
            elif 'use.typekit.net' in link['href']:
                technologies['Fonts'].add('Adobe Fonts (Typekit)')

        # Deployment Platform Detection
        if 'vercel' in headers.get('server', '').lower():
            technologies['Deployment Platform'] = 'Vercel'
        elif 'netlify' in headers.get('server', '').lower():
            technologies['Deployment Platform'] = 'Netlify'
        elif 'heroku' in headers.get('server', '').lower():
            technologies['Deployment Platform'] = 'Heroku'
        elif 'firebase' in headers.get('server', '').lower():
            technologies['Deployment Platform'] = 'Firebase'

        # Output detected technologies
        print("\nDetected Technologies on", url)
        for tech, values in technologies.items():
            if isinstance(values, set) and values:
                print(f"{tech}: {', '.join(sorted(values))}")
            elif values:
                print(f"{tech}: {values}")
            else:
                print(f"{tech}: Not detected")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")

# ask user for input 
if __name__ == "__main__":
    url = input("Enter the website URL (including http:// or https://): ").strip()
    detect_web_technologies(url)
