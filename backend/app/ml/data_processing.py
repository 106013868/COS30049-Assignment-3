"""
data_processing.py
cleans raw url dataset, extracts features and saves processed csv files
"""
import pandas as pd
import ipaddress

from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


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

    # suspicious keyword
    suspicious_keywords = [
        "login",
        "signin",
        "verify",
        "verification",
        "account",
        "secure",
        "update",
        "password",
        "bank"
    ]

    features["suspicious_keyword_count"] = sum(
        keyword in original_url
        for keyword in suspicious_keywords
    )


    return {
        column: features[column]
        for column in FEATURE_COLUMNS
    }


if __name__ == "__main__":
    # load database
    df = pd.read_csv("malicious_phish.csv")

    print("Original dataset:")
    print(df.head())
    print("\nColumns:")
    print(df.columns)


    df = df.rename(columns={
        "type": "label"
    })

    # removes missing data
    df = df.dropna(subset=["url", "label"])


    # url formatting
    df["url"] = (
        df["url"]
        .astype(str)
        .str.strip()
        .str.lower()
    )


    df["has_https"] = df["url"].apply(
        check_https
    )


    df["url"] = df["url"].apply(
        clean_url
    )


    # removes duplicates
    df = df.drop_duplicates(subset=["url"])

    df = df.reset_index(drop=True)


    # standardise labels
    label_mapping = {
        "benign": "legitimate",
        "phishing": "malicious",
        "defacement": "malicious",
        "malware": "malicious"
    }


    df["label"] = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["label"] = df["label"].map(label_mapping)


    # Remove any rows with labels that were not recognised
    df = df.dropna(subset=["label"])


    # Convert labels to numerical values
    df["label"] = df["label"].map({
        "legitimate": 0,
        "malicious": 1
    })


    # applying feature transformation
    feature_data = []

    for url, has_https in zip(
        df["url"],
        df["has_https"]
    ):

        feature_data.append(
            extract_features(
                url,
                has_https
            )
        )


    features_df = pd.DataFrame(
        feature_data
    )


    # enforce fixed feature schema
    features_df = features_df[
        FEATURE_COLUMNS
    ]

    # add label
    features_df["label"] = df["label"].values


    # separate features and label
    X = features_df.drop(columns=["label"])
    y = features_df["label"]

    # train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )


    # normalise features
    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)

    X_test = scaler.transform(X_test)


    print("\nDataset size:")
    print(f"Total URLs: {len(df)}")

    print("\nClass distribution:")
    print(
        df["label"]
        .map({
            0: "legitimate",
            1: "malicious"
        })
        .value_counts()
    )

    print("\nFixed feature schema:")

    for i, feature in enumerate(
        FEATURE_COLUMNS,
        start=1
    ):

        print(
            f"{i}. {feature}"
        )

    print("\nTraining data:")
    print(f"X_train: {X_train.shape}")
    print(f"y_train: {y_train.shape}")

    print("\nTesting data:")
    print(f"X_test: {X_test.shape}")

    print("\nFeatures:")
    print(list(X.columns))


    # Cleaned raw URL dataset
    df.to_csv("processed_dataset.csv", index=False)

    # Feature dataset for machine learning
    features_df.to_csv("processed_features.csv", index=False)