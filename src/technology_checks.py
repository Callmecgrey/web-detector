import re

# Existing patterns
CMS_PATTERNS = {
    'WordPress': re.compile(r'wp-content|wp-includes', re.IGNORECASE),
    'Joomla': re.compile(r'Joomla', re.IGNORECASE),
    'Drupal': re.compile(r'Drupal', re.IGNORECASE),
    'Shopify': re.compile(r'cdn\.shopify\.com', re.IGNORECASE),
    'Wix': re.compile(r'wix\.static', re.IGNORECASE),
    'Squarespace': re.compile(r'squarespace', re.IGNORECASE),
    # Additional CMS
    'Magento': re.compile(r'Mage.Cookies|skin/frontend|Magento', re.IGNORECASE),
    'Ghost': re.compile(r'<meta name="generator" content="Ghost', re.IGNORECASE),
    'Webflow': re.compile(r'<!-- This is Webflow\.com --!>', re.IGNORECASE),
    'Weebly': re.compile(r'weebly\.com', re.IGNORECASE)
}

ANALYTICS_PATTERNS = {
    'Google Analytics': re.compile(r'(gtag\( | ga\(|google-analytics\.com)', re.IGNORECASE),
    'Facebook Pixel': re.compile(r'(fbq\(|facebook-pixel)', re.IGNORECASE),
    'Hotjar': re.compile(r'hotjar', re.IGNORECASE),
    # Additional analytics
    'Mixpanel': re.compile(r'mixpanel\.com', re.IGNORECASE),
    'Amplitude': re.compile(r'amplitude\.com', re.IGNORECASE),
    'Segment': re.compile(r'cdn\.segment\.com', re.IGNORECASE)
}

TAG_MANAGER_PATTERN = re.compile(r'googletagmanager', re.IGNORECASE)

# Additional Tag Managers
ADDITIONAL_TAG_MANAGERS = {
    'Segment': re.compile(r'cdn\.segment\.com', re.IGNORECASE),
    'Tealium': re.compile(r'//tags\.tiqcdn\.com/utag/', re.IGNORECASE)
}

RUM_PATTERNS = {
    'New Relic': re.compile(r'newrelic', re.IGNORECASE),
    'Datadog': re.compile(r'datadog', re.IGNORECASE),
    # Additional RUM
    'AppDynamics': re.compile(r'cdn\.appdynamics\.com', re.IGNORECASE),
    'Dynatrace': re.compile(r'dynatrace', re.IGNORECASE)
}

# Additional JavaScript frameworks
JS_FRAMEWORK_INDICATORS = [
    ('Next.js', re.compile(r'/_next/', re.IGNORECASE)),
    ('Nuxt.js', re.compile(r'/_nuxt/|nuxt\.config', re.IGNORECASE)),
    ('Svelte', re.compile(r'svelte', re.IGNORECASE))
]

# Additional CDNs
CDN_INDICATORS = [
    ('Akamai', re.compile(r'akamai\.net', re.IGNORECASE)),
    ('Amazon CloudFront', re.compile(r'cloudfront\.net', re.IGNORECASE)),
    ('Fastly', re.compile(r'fastly\.net', re.IGNORECASE))
]

# Advertising & tracking
AD_PATTERNS = {
    'Google Ads': re.compile(r'ads\.google\.com|adservice\.google\.', re.IGNORECASE),
    'Bing Ads': re.compile(r'bat\.bing\.com', re.IGNORECASE),
    'DoubleClick': re.compile(r'doubleclick\.net', re.IGNORECASE)
}

# Payment integrations
PAYMENT_PATTERNS = {
    'Stripe': re.compile(r'stripe\.com', re.IGNORECASE),
    'PayPal': re.compile(r'paypal\.com', re.IGNORECASE)
}

def detect_cms(html_content, headers, cookies, technologies):
    # Existing CMS detection via headers
    if 'X-Drupal-Cache' in headers:
        technologies['CMS'] = 'Drupal'
    if 'X-Shopify-Stage' in headers:
        technologies['CMS'] = 'Shopify'

    # CMS detection via HTML content
    for cms, pattern in CMS_PATTERNS.items():
        if pattern.search(html_content):
            technologies['CMS'] = cms
            break

    # Cookies detection for WordPress
    for cookie in cookies:
        if 'wordpress' in cookie.name.lower():
            technologies['CMS'] = 'WordPress'

def detect_js_frameworks(soup, technologies):
    if soup is None:
        return

    # Existing JS frameworks detection
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

    inline_scripts = soup.find_all('script', src=False)
    for script in inline_scripts:
        text = script.string or ''
        if 'window.React' in text:
            technologies['JavaScript Frameworks'].add('React')
        if 'window.angular' in text:
            technologies['JavaScript Frameworks'].add('Angular')
        if re.search(r'var\s+\$', text) and 'jQuery' not in technologies['JavaScript Frameworks']:
            technologies['JavaScript Frameworks'].add('jQuery')

    # Additional frameworks via HTML patterns
    html_content = soup.get_text()  # Get text from the page to find indicators
    for framework, pattern in JS_FRAMEWORK_INDICATORS:
        if pattern.search(html_content):
            technologies['JavaScript Frameworks'].add(framework)

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
        cname = cookie.name.lower()
        if 'google' in cname:
            technologies['Analytics'].add('Google Analytics')
        if 'hotjar' in cname:
            technologies['Analytics'].add('Hotjar')
        if 'mixpanel' in cname:
            technologies['Analytics'].add('Mixpanel')
        # Other analytics can be detected via cookies if known patterns exist

def detect_tag_managers(html_content, technologies):
    if TAG_MANAGER_PATTERN.search(html_content):
        technologies['Tag Managers'].add('Google Tag Manager')

    for name, pattern in ADDITIONAL_TAG_MANAGERS.items():
        if pattern.search(html_content):
            technologies['Tag Managers'].add(name)

def detect_rum_tools(html_content, technologies):
    for name, pattern in RUM_PATTERNS.items():
        if pattern.search(html_content):
            technologies['RUM (Real User Monitoring)'].add(name)

def detect_meta_tags(soup, technologies):
    if soup is None:
        return
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        if 'property' in tag.attrs:
            prop = tag['property'].lower()
            # Detect Open Graph
            if prop.startswith('og:'):
                technologies['Other Technologies'].add('Open Graph (Facebook)')
            # Detect Twitter Cards
            if prop.startswith('twitter:'):
                technologies['Other Technologies'].add('Twitter Cards')

        if 'name' in tag.attrs:
            name = tag['name'].lower()
            content = (tag.get('content') or '').lower()
            if 'generator' in name and 'wordpress' in content:
                technologies['CMS'] = 'WordPress'
            # LinkedIn Insights might appear as meta tags (rare)
            if 'linkedin' in name:
                technologies['Other Technologies'].add('LinkedIn Insights')

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
    # Existing CDN detection handled by server (Cloudflare)
    # Additional CDN detection
    cdn_candidates = headers.get('CDN-Cache-Status', '') + headers.get('Via', '')
    for cdn_name, pattern in CDN_INDICATORS:
        if pattern.search(cdn_candidates):
            technologies['CDN'] = cdn_name
            break

    # We can also inspect HTML if needed
    # If HTML needed: check in detect_js_frameworks or meta tags for CDN hints if any.

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

def detect_ads_and_tracking(html_content, technologies):
    # Advertising & Tracking scripts
    for ad_name, pattern in AD_PATTERNS.items():
        if pattern.search(html_content):
            technologies['Other Technologies'].add(ad_name)

def detect_payment_integrations(html_content, technologies):
    for payment_name, pattern in PAYMENT_PATTERNS.items():
        if pattern.search(html_content):
            technologies['Other Technologies'].add(payment_name)
