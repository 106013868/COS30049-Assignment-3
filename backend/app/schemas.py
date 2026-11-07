from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_URL_LENGTH = 2048


class PredictRequest(BaseModel):
    url: str = Field(
        min_length=1,
        max_length=MAX_URL_LENGTH,
        description="The URL or domain to inspect. It is never visited.",
        examples=["http://secure-login.verify-account.xyz/signin"],
    )

    @field_validator("url")
    @classmethod
    def clean_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Please enter a URL.")
        if any(ch.isspace() for ch in value):
            raise ValueError("URL must not contain spaces.")
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
            raise ValueError("URL contains invalid control characters.")
        return value


class Signal(BaseModel):
    id: str
    title: str
    description: str
    status: Literal["pass", "warn", "info"]
    used_by_model: bool


class PredictResponse(BaseModel):
    url: str
    verdict: Literal["phishing", "legitimate"]
    confidence: float = Field(ge=0, le=1)
    trust_score: int = Field(ge=0, le=100)
    features: dict[str, float]
    signals: list[Signal]
    model_version: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "url": "secure-login.verify-account.xyz/signin",
                "verdict": "phishing",
                "confidence": 0.81,
                "trust_score": 19,
                "features": {
                    "url_length": 38, "domain_length": 31, "path_length": 7,
                    "digit_count": 0, "special_character_count": 5, "dot_count": 2,
                    "subdomain_count": 1, "has_ip": 0, "suspicious_keyword_count": 4,
                },
                "signals": [{
                    "id": "keywords",
                    "title": "Suspicious wording",
                    "description": "Contains: login, signin, verify, secure",
                    "status": "warn",
                    "used_by_model": True,
                }],
                "model_version": "hgb-a2-1.0",
            }]
        }
    }


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_loaded: bool

    model_config = {
        "json_schema_extra": {"examples": [{"status": "ok", "model_loaded": True}]}
    }


class ModelInfoResponse(BaseModel):
    model_version: str
    features: list[str]
    reference: dict[str, dict[str, float]]

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "model_version": "hgb-a2-1.0",
                "features": ["url_length", "domain_length", "path_length", "digit_count",
                             "special_character_count", "dot_count", "subdomain_count",
                             "has_ip", "suspicious_keyword_count"],
                "reference": {
                    "legitimate": {"url_length": 56.52, "subdomain_count": 0.38,
                                   "has_ip": 0.0, "suspicious_keyword_count": 0.07},
                    "phishing": {"url_length": 57.2, "subdomain_count": 0.48,
                                 "has_ip": 0.06, "suspicious_keyword_count": 0.06},
                },
            }]
        }
    }


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail

    model_config = {
        "json_schema_extra": {
            "examples": [{"error": {"code": "VALIDATION_ERROR",
                                    "message": "URL must not contain spaces."}}]
        }
    }