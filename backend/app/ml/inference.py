import joblib
import pandas as pd
from . import config as cfg
from .data_processing import clean_url, check_https, extract_features, normalise_url

def load_model(path=cfg.MODEL_PATH):
    """
    loads saved model from path
    """
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at {path}")
    return joblib.load(path)

def predict(model, df):
    """
    adds prediction, probability and trust score columns to a copy of df
    """
    features = df[cfg.FEATURE_COLUMNS]
    # probability of class 1 (malicious)
    probabilities = model.predict_proba(features)[:, 1]
    labels = model.predict(features)
    # trust score is the chance the url is not malicious, as a percentage
    trust = ((1 - probabilities) * 100).round()
    results = df.copy()
    results[cfg.PREDICTION_COLUMN] = labels
    results[cfg.PROBABILITY_COLUMN] = probabilities
    results[cfg.TRUST_COLUMN] = trust
    
    return results

def predict_url(model, url):
    """
    In: raw url
    Out: one row dataframe with prediction and trust score
    """
    # look-alike and invisible characters become plain ones first (2.8 defence)
    url = normalise_url(url)
    # same cleaning steps as data_processing
    cleaned = clean_url(url)
    # https is read from the raw url because clean_url removes the protocol
    has_https = check_https(url)
    features = extract_features(cleaned, has_https)
    row = pd.DataFrame([features])
    row[cfg.URL_COLUMN] = cleaned

    return predict(model, row)