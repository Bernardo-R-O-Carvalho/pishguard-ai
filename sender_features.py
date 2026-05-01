import re

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

FREE_PROVIDERS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"}

def normalize_domain(domain):
    result = domain
    for fake, real in CHAR_SUBSTITUTIONS.items():
        result = result.replace(fake, real)
    return result

def extract_domain(email):
    match = re.search(r'@([\w\.\-]+)', email.lower())
    return match.group(1) if match else None

def analyze_sender(sender):
    if not sender or "@" not in sender:
        return []

    flags = []
    domain = extract_domain(sender)
    if not domain:
        return []

    if domain in FREE_PROVIDERS:
        for trusted in WHITELIST:
            trusted_name = trusted.split(".")[0]
            if trusted_name in sender.lower():
                flags.append(f"impersonating {trusted} via free email provider")

    if not any(domain == w for w in WHITELIST):
        normalized = normalize_domain(domain)
        for w in WHITELIST:
            if normalized == w and domain != w:
                flags.append(f"domain impersonating {w}")
                break

        normalized_no_tld = normalized.split(".")[0]
        for trusted in WHITELIST:
            trusted_name = trusted.split(".")[0]
            if trusted_name == normalized_no_tld and domain != trusted:
                if f"domain impersonating {trusted}" not in flags:
                    flags.append(f"domain impersonating {trusted}")
                break
            elif trusted_name in normalized and domain != trusted:
                if f"domain impersonating {trusted}" not in flags:
                    flags.append(f"domain impersonating {trusted}")
                break

    if re.search(r'(verify|secure|login|account|update|support|helpdesk)', domain):
        flags.append("suspicious word in sender domain")

    if re.search(r'\d', domain.split(".")[0]):
        flags.append("numbers in sender domain")

    if domain.count(".") > 3:
        flags.append("too many subdomains in sender")

    return flags