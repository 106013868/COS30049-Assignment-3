"""
config.py
holds constants used throughout all modules
i.e. paths, data column names
"""
from pathlib import Path

# Constant definitions
ROOT_DIR = Path(__file__).resolve().parents[2]   # parents[2] is backend/

# folder paths
MODELS_DIR = ROOT_DIR / "models"

MODEL_PATH = MODELS_DIR / "hist_gradient_boosting.joblib"
FINAL_MODEL = "HistGradientBoosting" # chosen model after evaluation

# dataset column names
URL_COLUMN = "url"
LABEL_COLUMN = "label"
DOMAIN_COLUMN = "domain"
# features the model trains on
FEATURE_COLUMNS = [
    "url_length",
    "domain_length",
    "path_length",
    "digit_count",
    "special_character_count",
    "dot_count",
    "subdomain_count",
    "has_ip",
    "suspicious_keyword_count"
]
# column names added during clustering and prediction
CLUSTER_COLUMN = "cluster"
PREDICTION_COLUMN = "prediction"
PROBABILITY_COLUMN = "probability"
TRUST_COLUMN = "trust_score"

# words often used in phishing urls (shared by feature extraction and signals)
SUSPICIOUS_KEYWORDS = [
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