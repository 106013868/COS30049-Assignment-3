"""
signals.py
turns a URL and its features into the signal cards shown on the results screen
"""
from app.ml.config import SUSPICIOUS_KEYWORDS
from app.schemas import Signal

# cut-offs for the cards (the average legitimate URL is about 57 characters,
# with about 6 digits and 8 special characters)
LONG_URL = 75
MANY_DIGITS = 10
MANY_SYMBOLS = 15
REDIRECT_PARAMS = ("url=", "redirect=", "next=", "return=", "dest=")


def build_signals(url: str, features: dict[str, float]) -> list[Signal]:
    lowered = url.lower()
    signals = []

    # signals the model actually uses
    if features["has_ip"]:
        signals.append(Signal(id="ip", title="IP address as domain",
            description="Uses a raw IP address instead of a domain name, a strong phishing sign.",
            status="warn", used_by_model=True))
    else:
        signals.append(Signal(id="ip", title="IP address as domain",
            description="Uses a normal domain name, not a raw IP address.",
            status="pass", used_by_model=True))

    subdomains = int(features["subdomain_count"])
    if features["has_ip"]:
        # the dots in an IP address are counted as subdomains, so skip this card
        signals.append(Signal(id="subdomains", title="Excessive subdomains",
            description="Not applicable, the address is an IP address.",
            status="info", used_by_model=True))
    elif subdomains >= 2:
        signals.append(Signal(id="subdomains", title="Excessive subdomains",
            description=f"Has {subdomains} subdomains stacked before the main domain.",
            status="warn", used_by_model=True))
    else:
        signals.append(Signal(id="subdomains", title="Excessive subdomains",
            description="No stack of extra subdomains.",
            status="pass", used_by_model=True))

    found = [word for word in SUSPICIOUS_KEYWORDS if word in lowered]
    if found:
        signals.append(Signal(id="keywords", title="Suspicious wording",
            description="Contains: " + ", ".join(found),
            status="warn", used_by_model=True))
    else:
        signals.append(Signal(id="keywords", title="Suspicious wording",
            description="No words commonly used in phishing links.",
            status="pass", used_by_model=True))

    length = int(features["url_length"])
    if length > LONG_URL:
        signals.append(Signal(id="length", title="URL length",
            description=f"{length} characters. Long URLs can hide the real destination.",
            status="warn", used_by_model=True))
    else:
        signals.append(Signal(id="length", title="URL length",
            description=f"{length} characters, within the normal range.",
            status="pass", used_by_model=True))

    digits = int(features["digit_count"])
    symbols = int(features["special_character_count"])
    if digits >= MANY_DIGITS or symbols >= MANY_SYMBOLS:
        signals.append(Signal(id="characters", title="Digits and symbols",
            description=f"{digits} digits and {symbols} symbols, more than usual.",
            status="warn", used_by_model=True))
    else:
        signals.append(Signal(id="characters", title="Digits and symbols",
            description=f"{digits} digits and {symbols} symbols, a normal amount.",
            status="pass", used_by_model=True))

    # extra checks shown to the user but not used by the model
    if lowered.startswith("https://"):
        signals.append(Signal(id="https", title="HTTPS protocol",
            description="The address uses encrypted HTTPS.",
            status="pass", used_by_model=False))
    else:
        signals.append(Signal(id="https", title="HTTPS protocol",
            description="No https:// at the start. Encrypted sites use HTTPS.",
            status="info", used_by_model=False))

    query = lowered.split("?", 1)[1] if "?" in lowered else ""
    if any(param in query for param in REDIRECT_PARAMS):
        signals.append(Signal(id="redirect", title="Redirect parameter detected",
            description="A parameter like ?url= or ?redirect= may send you somewhere else.",
            status="warn", used_by_model=False))
    else:
        signals.append(Signal(id="redirect", title="Redirect parameter",
            description="No parameter that redirects to another site.",
            status="pass", used_by_model=False))

    if any(ord(ch) > 127 for ch in url) or "xn--" in lowered:
        signals.append(Signal(id="lookalike", title="Look-alike characters",
            description="Contains non-standard characters that can imitate real letters.",
            status="warn", used_by_model=False))
    else:
        signals.append(Signal(id="lookalike", title="Look-alike characters",
            description="Only standard characters.",
            status="pass", used_by_model=False))

    return signals