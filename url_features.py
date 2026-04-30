import re
from urllib.parse import urlparse

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly"}

WHITELIST = {
    "paypal.com", "bankofamerica.com", "amazon.com", "google.com",
    "microsoft.com", "apple.com", "netflix.com", "instagram.com"
}

CHAR_SUBSTITUTIONS = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '@': 'a'
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
            flags.append("sem HTTPS")

        if domain in SHORTENERS:
            flags.append("link encurtado")

        if any(domain.endswith("." + w) or domain == w for w in WHITELIST):
            flags.append("domínio confiável")
            return {"url": url, "domain": domain, "flags": flags}

        if re.search(r'\d{4,}', domain):
            flags.append("números suspeitos no domínio")

        if domain.count(".") > 3:
            flags.append("muitos subdomínios")

        if re.search(r'(verify|secure|login|account|update|confirm)', domain):
            flags.append("palavra suspeita no domínio")

        normalized = normalize_domain(domain)
        for trusted in WHITELIST:
            trusted_name = trusted.split(".")[0]
            if trusted_name in normalized and domain != trusted:
                flags.append(f"imitando {trusted}")
                break

        subdomains = domain.split(".")
        for trusted in WHITELIST:
            trusted_name = trusted.split(".")[0]
            if trusted_name in subdomains[:-2]:
                if f"imitando {trusted}" not in flags:
                    flags.append(f"imitando {trusted}")

        return {"url": url, "domain": domain, "flags": flags}
    except:
        return {"url": url, "domain": "", "flags": ["erro ao analisar"]}

def analyze_email_urls(text):
    urls = extract_urls(text)
    if not urls:
        return []
    return [analyze_url(url) for url in urls]