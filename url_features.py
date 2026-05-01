import re
from urllib.parse import urlparse

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly"}

WHITELIST = {
    "paypal.com", "bankofamerica.com", "amazon.com", "google.com",
    "microsoft.com", "apple.com", "netflix.com", "instagram.com"
}

CHAR_SUBSTITUTIONS = {
    '0': 'o',
    '1': 'l',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '6': 'g',
    '8': 'b',
    '@': 'a',
    'rn': 'm',
    'vv': 'w',
    'cl': 'd',
    'ii': 'n',
}

def normalize_domain(domain):
    result = domain
    for fake, real in CHAR_SUBSTITUTIONS.items():
        result = result.replace(fake, real)
    return result

def extract_urls(text):
    return re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)

def analyze_url(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        flags = []

        if parsed.scheme == "http":
            flags.append("no HTTPS")

        if domain in SHORTENERS:
            flags.append("shortened link")

        if any(domain.endswith("." + w) or domain == w for w in WHITELIST):
            flags.append("trusted domain")
            return {"url": url, "domain": domain, "flags": flags}

        normalized_check = normalize_domain(domain)
        for w in WHITELIST:
            if normalized_check == w and domain != w:
                flags.append(f"impersonating {w}")
                return {"url": url, "domain": domain, "flags": flags}

        if re.search(r'\d{4,}', domain):
            flags.append("suspicious numbers in domain")

        if domain.count(".") > 3:
            flags.append("too many subdomains")

        if re.search(r'(verify|secure|login|account|update|confirm)', domain):
            flags.append("suspicious word in domain")

        normalized = normalize_domain(domain)
        normalized_no_tld = normalized.split(".")[0]
        for trusted in WHITELIST:
            trusted_name = trusted.split(".")[0]
            if trusted_name == normalized_no_tld and domain != trusted:
                flags.append(f"impersonating {trusted}")
                break
            elif trusted_name in normalized and domain != trusted:
                flags.append(f"impersonating {trusted}")
                break

        subdomains = domain.split(".")
        for trusted in WHITELIST:
            trusted_name = trusted.split(".")[0]
            if trusted_name in subdomains[:-2]:
                if f"impersonating {trusted}" not in flags:
                    flags.append(f"impersonating {trusted}")

        return {"url": url, "domain": domain, "flags": flags}
    except:
        return {"url": url, "domain": "", "flags": ["error analyzing URL"]}

def analyze_email_urls(text):
    urls = extract_urls(text)
    if not urls:
        return []
    return [analyze_url(url) for url in urls]