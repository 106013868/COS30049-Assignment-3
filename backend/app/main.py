import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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


app = FastAPI(title="PhishLens API", lifespan=lifespan,
              redoc_url=None) # switch off second docs page, we only want /docs

# Browsers may only read API responses from our own front end
# Least privilege
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["GET", "POST"],             # the only methods the API uses
    allow_headers=["Content-Type"],            # the only header the front end sends
    allow_credentials=False,                   # no cookies or logins in this app
)

# Security headers added to every response
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",   # browser must trust our Content-Type, never guess
    "X-Frame-Options": "DENY",             # no other site may show our pages inside a frame
    "Referrer-Policy": "no-referrer",      # don't leak our URLs to other sites
}
# The API only returns JSON, so it needs to load nothing and may never be framed
API_CSP = "default-src 'none'; form-action 'none'; frame-ancestors 'none'"

# /docs loads its files from a CDN, so its policy allows only what it needs
DOCS_CSP = (
    "default-src 'none'; "
    "script-src https://cdn.jsdelivr.net 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='; "
    "style-src https://cdn.jsdelivr.net 'unsafe-inline'; "
    "img-src https://fastapi.tiangolo.com data:; "
    "connect-src 'self'; "
    "form-action 'none'; "
    "frame-ancestors 'none'; "
    "base-uri 'none'"
)


# Denial of service defence, part 1: refuse huge requests before reading them
# The largest valid request is a 2,048-character URL, about 24 KB at most
MAX_BODY_BYTES = 32 * 1024

@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    length = request.headers.get("content-length")
    # A body with no declared size could be any size, so it is refused
    if request.method == "POST" and (length is None or "transfer-encoding" in request.headers):
        return JSONResponse(status_code=411, content={"detail": "Content-Length header is required"})
    # The declared size is checked from the headers alone, before any of the body is read
    if length is not None and int(length) > MAX_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Request body is too large"})
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)          # let the endpoint build its response first
    response.headers.update(SECURITY_HEADERS)
    if request.url.path != "/docs":
        response.headers["Content-Security-Policy"] = API_CSP
    else:
        response.headers["Content-Security-Policy"] = DOCS_CSP
    return response

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