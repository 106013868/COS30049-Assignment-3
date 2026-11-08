"""
data_processing.py
cleans raw url dataset, extracts features and saves processed csv files
"""
#import pandas as pd
import ipaddress

from urllib.parse import urlparse
from .config import SUSPICIOUS_KEYWORDS
#from sklearn.model_selection import train_test_split
#from sklearn.preprocessing import StandardScaler


# fixed feature schema
FEATURE_COLUMNS = [
    "url_length",
    "domain_length",
    "path_length",
    "digit_count",
    "special_character_count",
    "dot_count",
    "subdomain_count",
    "has_ip",
    "has_https",
    "suspicious_keyword_count"
]


# checks for https before removing protocol
def check_https(url):
    """
    returns 1 if url starts with https, otherwise 0
    """
    url = str(url).strip().lower()

    return int(
        url.startswith("https://")
    )


# removes url prefixes
def clean_url(url):
    """
    lowercases url and removes protocol, www and trailing slashes
    """
    url = str(url).strip().lower()

    # Remove HTTP
    if url.startswith("http://"):
        url = url[7:]

    # Remove HTTPS
    elif url.startswith("https://"):
        url = url[8:]

    # Remove WWW
    if url.startswith("www."):
        url = url[4:]

    # Remove all trailing slashes
    url = url.rstrip("/")

    return url


# feature extraction
def extract_features(url, has_https):
    """
    In: cleaned url, has_https flag
    Out: dict of features in fixed schema order
    """
    # url is already cleaned, so protocol and www are gone
    original_url = str(url)

    # Default values in case URL parsing fails
    domain = ""
    path = ""

    # Add protocol temporarily so urlparse() can identify domain
    parse_url = "http://" + original_url

    # Try to parse the URL
    try:
        parsed = urlparse(parse_url)

        domain = parsed.netloc.split(":")[0]
        path = parsed.path

    except ValueError:
        # URL is malformed, so use empty
        # domain/path values instead
        domain = ""
        path = ""


    # creating features
    features = {

        # 1. URL length
        "url_length": len(original_url),

        # 2. Domain length
        "domain_length": len(domain),

        # 3. Path length
        "path_length": len(path),

        # 4. Number of digits
        "digit_count": sum(
            character.isdigit()
            for character in original_url
        ),

        # 5. Number of special characters
        "special_character_count": sum(
            not character.isalnum()
            for character in original_url
        ),

        # 6. Number of dots
        "dot_count": original_url.count("."),

        # 7. Number of subdomains
        "subdomain_count": max(
            0,
            len(domain.split(".")) - 2
        ),

        # 8. Is the domain an IP address?
        "has_ip": 0,

        # 9. Was the original URL HTTPS?
        "has_https": has_https,

        # 10. Number of suspicious keywords
        "suspicious_keyword_count": 0
    }


    # ip address check
    try:
        ipaddress.ip_address(domain)
        features["has_ip"] = 1

    except ValueError:
        features["has_ip"] = 0


    features["suspicious_keyword_count"] = sum(
        keyword in original_url
        for keyword in SUSPICIOUS_KEYWORDS
    )


    return {
        column: features[column]
        for column in FEATURE_COLUMNS
    }