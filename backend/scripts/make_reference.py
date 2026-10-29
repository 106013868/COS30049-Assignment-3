import json
import pandas as pd
from pathlib import Path

# data set paths
CSV_PATH = Path("data/processed_features.csv")
OUT_PATH = Path("models/feature_reference.json")

FEATURES = ["url_length", "domain_length", "path_length", "digit_count",
            "special_character_count", "dot_count", "subdomain_count",
            "has_ip", "suspicious_keyword_count"]

df = pd.read_csv(CSV_PATH)
means = df.groupby("label")[FEATURES].mean().round(2)
reference = {"legitimate": means.loc[0].to_dict(),
             "phishing": means.loc[1].to_dict()}
OUT_PATH.write_text(json.dumps(reference, indent=2))
print(reference)