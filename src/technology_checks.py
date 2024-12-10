import re

# Compile regexes once for performance and maintainability
CMS_PATTERNS = {
    'WordPress': re.compile(r'wp-content|wp-includes', re.IGNORECASE),
    'Joomla': re.compile(r'Joomla', re.IGNORECASE),
    'Drupal': re.compile(r'Drupal', re.IGNORECASE),
    'Shopify': re.compile(r'cdn\.shopify\.com', re.IGNORECASE),
    'Wix': re.compile(r'wix\.static', re.IGNORECASE),
    'Squarespace': re.compile(r'squarespace', re.IGNORECASE)
}

ANALYTICS_PATTERNS = {
    'Google Analytics': re.compile(r'(gtag\( | ga\(|google-analytics\.com)', re.IGNORECASE),
    'Facebook Pixel': re.compile(r'(fbq\(|facebook-pixel)', re.IGNORECASE),
    'Hotjar': re.compile(r'hotjar', re.IGNORECASE)
}

TAG_MANAGER_PATTERN = re.compile(r'googletagmanager', re.IGNORECASE)
RUM_PATTERNS = {
    'New Relic': re.compile(r'newrelic', re.IGNORECASE),
    'Datadog': re.compile(r'datadog', re.IGNORECASE)
}

def detect_cms(html_content, headers, cookies, technologies):
    # Check headers
    if 'X-Drupal-Cache' in headers:
        technologies['CMS'] = 'Drupal'
    if 'X-Shopify-Stage' in headers:
        technologies['CMS'] = 'Shopify'

    # HTML content patterns
    for cms, pattern in CMS_PATTERNS.items():
        if pattern.search(html_content):
            technologies['CMS'] = cms
            break

    # Cookies
    for cookie in cookies:
        if 'wordpress' in cookie.name.lower():
            technologies['CMS'] = 'WordPress'

def detect_js_frameworks(soup, technologies):
    if soup is None:
        return
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

    # Inline scripts detection
    for script in soup.find_all('script', src=False):
        text = script.string or ''
        if 'window.React' in text:
            technologies['JavaScript Frameworks'].add('React')
        if 'window.angular' in text:
            technologies['JavaScript Frameworks'].add('Angular')
        if re.search(r'var\s+\$', text) and 'jQuery' not in technologies['JavaScript Frameworks']:
            technologies['JavaScript Frameworks'].add('jQuery')

def detect_css_frameworks(soup, technologies):
    if soup is None:
        return
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

def detect_analytics(html_content, cookies, technologies):
    for name, pattern in ANALYTICS_PATTERNS.items():
        if pattern.search(html_content):
            technologies['Analytics'].add(name)

    # Analytics from cookies
    for cookie in cookies:
        if 'google' in cookie.name.lower():
            technologies['Analytics'].add('Google Analytics')
        if 'hotjar' in cookie.name.lower():
            technologies['Analytics'].add('Hotjar')

def detect_tag_managers(html_content, technologies):
    if TAG_MANAGER_PATTERN.search(html_content):
        technologies['Tag Managers'].add('Google Tag Manager')

def detect_rum_tools(html_content, technologies):
    for name, pattern in RUM_PATTERNS.items():
        if pattern.search(html_content):
            technologies['RUM (Real User Monitoring)'].add(name)

def detect_meta_tags(soup, technologies):
    if soup is None:
        return
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        if 'property' in tag.attrs and tag['property'].startswith('og:'):
            technologies['Other Technologies'].add('Open Graph (Facebook)')
        if 'name' in tag.attrs:
            name = tag['name'].lower()
            content = (tag.get('content') or '').lower()
            if 'generator' in name and 'wordpress' in content:
                technologies['CMS'] = 'WordPress'

def detect_server(headers, technologies):
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

def detect_programming_languages(html_content, headers, technologies):
    powered_by = headers.get('X-Powered-By', '').lower()
    if 'php' in powered_by:
        technologies['Programming Languages'].add('PHP')
    if 'asp.net' in powered_by:
        technologies['Programming Languages'].add('ASP.NET')

    if re.search(r'\.php', html_content):
        technologies['Programming Languages'].add('PHP')

def detect_cdn(headers, technologies):
    # Placeholder for detecting other CDNs
    pass

def detect_fonts(soup, technologies):
    if soup is None:
        return
    for link in soup.find_all('link', href=True):
        href = link['href'].lower()
        if 'fonts.googleapis' in href:
            technologies['Fonts'].add('Google Fonts')
        elif 'use.typekit.net' in href:
            technologies['Fonts'].add('Adobe Fonts (Typekit)')

def detect_deployment_platform(headers, technologies):
    server = headers.get('Server', '').lower()
    if 'vercel' in server:
        technologies['Deployment Platform'] = 'Vercel'
    elif 'netlify' in server:
        technologies['Deployment Platform'] = 'Netlify'
    elif 'heroku' in server:
        technologies['Deployment Platform'] = 'Heroku'
    elif 'firebase' in server:
        technologies['Deployment Platform'] = 'Firebase'
