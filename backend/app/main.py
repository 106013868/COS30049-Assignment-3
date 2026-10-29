import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.ml import config as cfg
from app.ml.inference import load_model, predict_url
from app.schemas import PredictRequest, PredictResponse
from app.signals import build_signals

logger = logging.getLogger("phishlens")

REFERENCE_PATH = cfg.MODELS_DIR / "feature_reference.json"
MODEL_VERSION = "hgb-a2-1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts
    try:
        app.state.model = load_model()
        app.state.reference = json.loads(REFERENCE_PATH.read_text())
        logger.info("Model loaded from %s", cfg.MODEL_PATH)
    except Exception:
        # Keep the server running so endpoints can answer 503
        logger.exception("Could not load the model")
        app.state.model = None
        app.state.reference = None
    yield
    # Runs once when the server stops (nothing to clean up)


app = FastAPI(title="PhishLens API", lifespan=lifespan)


@app.get("/api/health")
def health(request: Request):
    if request.app.state.model is None:
        return JSONResponse(status_code=503,
                            content={"status": "unavailable", "model_loaded": False})
    return {"status": "ok", "model_loaded": True}

@app.post("/api/predict", response_model=PredictResponse)
def predict(body: PredictRequest, request: Request):
    model = request.app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not available")

    # Same cleaning and feature extraction as training (from A2)
    row = predict_url(model, body.url).iloc[0]

    probability = float(row[cfg.PROBABILITY_COLUMN])   # chance it is phishing
    is_phishing = int(row[cfg.PREDICTION_COLUMN]) == 1
    verdict = "phishing" if is_phishing else "legitimate"
    confidence = probability if is_phishing else 1 - probability

    features = {name: float(row[name]) for name in cfg.FEATURE_COLUMNS}

    return PredictResponse(
        url=body.url,
        verdict=verdict,
        confidence=round(confidence, 4),
        trust_score=int(row[cfg.TRUST_COLUMN]),
        features=features,
        signals=build_signals(body.url, features),   # filled in by Step 13
        model_version=MODEL_VERSION,
    )