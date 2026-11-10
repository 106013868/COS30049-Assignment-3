# PhishLens

Web application that checks whether a URL is phishing or legitimate, using a machine learning model trained on URL features. The URL is analysed as text only and is never visited.

- **Backend**: FastAPI 0.162.0, scikit-learn 1.9.1, Python 3.15
- **Frontend**: React 19.3.1 with Vite 8.3.6, React Router 8.5.1 and Recharts 3.10.1
- **ML Model**: HistGradientBoosting classifier (from Assignment 2)

**Group:** TODO: group name

| Name | Student ID | Role |
|---|---|---|
| Tim Johnson | 106013868 | Security |
| Raza Syed | 104041595 | Back end, front end |
| Anthony Duero | 104561608 | Video |

## Quick Start

<!-- Rubric, Source code 1) Runs from the README (2 pts): "Following the README alone on a clean machine starts both the front end and the back end, with no fixes needed. Dependency versions are pinned." -->

### Prerequisites
- Python 3.15
- Node.js 22 or later (with npm)

### Backend Setup
```bash
cd backend
python -m venv .venv               # macOS: python3 -m venv .venv
.venv\Scripts\activate             # macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env             # macOS: cp .env.example .env
uvicorn app.main:app
```

### Backend running
```bash
cd backend
.venv\Scripts\activate             # macOS: source .venv/bin/activate
uvicorn app.main:app
```

Backend runs on `http://127.0.0.1:8000`

### Frontend Setup / running
In a second terminal, from the project root:
```
cd frontend
npm ci
copy .env.example .env             # macOS: cp .env.example .env
npm run build
npm run preview
```
Open http://localhost:5173. The back end must be running first.

### Configuration
| Variable | File | Purpose | Default |
|---|---|---|---|
| `VITE_API_BASE_URL` | `frontend/.env` | Address of the back end | `http://localhost:8000` |
| `FRONTEND_ORIGIN` | `backend/.env` | The only origin allowed by CORS | `http://localhost:5173` |
| `LOG_LEVEL` | `backend/.env` | TODO | `info` |

## Usage

### Checking a URL in the app
Open http://localhost:5173, paste a URL into URL to Inspect and press Submit. The result shows the verdict, confidence, trust score and signal cards, with two charts below

### Checking a URL through the API
1. Start the backend
2. Open `http://127.0.0.1:8000/docs`
3. Open **POST /api/predict**, click **Try it out**
4. Enter a URL in the request body and click **Execute**
5. View the verdict, confidence, trust score and signals in the response

## Model Performance

Assignment 2 results on the grouped test split (no website appears in both training and test data).

| Task | Model | Accuracy | Precision | Recall | F1-Score |
|------|-------|----------|-----------|--------|----------|
| Phishing URL detection | HistGradientBoosting (balanced) | 0.724 | 0.570 | 0.690 | 0.624 |

## API Documentation

Interactive docs with full examples at `http://127.0.0.1:8000/docs` while the backend is running.

**GET /api/health**: server and model status. Returns `200` when the model is loaded, `503` when it is not.
```json
{"status": "ok", "model_loaded": true}
```

**POST /api/predict**: scores one URL. Returns `200`, `422` for invalid input, `411` or `413` for a body with no declared size or over 32 KB, and `503` if the model is not loaded or the server is busy.

Request:
```json
{"url": "http://secure-login.verify-account.xyz/signin"}
```

Response (shortened):
```json
{
  "url": "http://secure-login.verify-account.xyz/signin",
  "verdict": "phishing",
  "confidence": 0.7351,
  "trust_score": 26,
  "features": {"url_length": 38.0, "suspicious_keyword_count": 5.0},
  "signals": [{"id": "keywords", "title": "Suspicious wording", "status": "warn"}],
  "model_version": "hgb-a2-1.0"
}
```
`features` holds the 9 URL features the model uses, and `signals` holds the explanation cards shown with each result.

**GET /api/model-info**: the model version, its 9 features, and the average value of each feature for legitimate and phishing URLs in the training data. Used by the comparison chart. Returns `200`, or `503` if the reference data did not load.

### Error format
<!-- Rubric, Back end 2) Error handling (2 pts): "Invalid input receives a clear message with the right status code. Every error, including unexpected ones such as a failing model call, is returned in the same JSON format, without stack traces or other internal details." -->
Every error uses the same JSON shape: `{"error": {"code": "VALIDATION_ERROR", "message": "URL must not contain spaces."}}`. 
Codes: `NOT_FOUND` (404), `METHOD_NOT_ALLOWED` (405), `LENGTH_REQUIRED` (411), `PAYLOAD_TOO_LARGE` (413), `VALIDATION_ERROR` (422), `INTERNAL_ERROR` (500), `SERVICE_UNAVAILABLE` (503). 
Unexpected errors are logged on the server only; the client gets a generic message with no stack trace.

## Project Structure
```
COS30049-Assignment-3/
├── README.md
├── .gitignore
├── backend/                       # FastAPI backend
│   ├── app/
│   │   ├── main.py                # API endpoints, CORS, security headers, DoS limits
│   │   ├── errors.py              # one JSON format for every error
│   │   ├── schemas.py             # Pydantic request and response models
│   │   ├── config.py              # settings read from environment variables
│   │   ├── signals.py             # signal cards shown with each result
│   │   └── ml/                    # Assignment 2 model code
│   │       ├── config.py          # paths, column names, feature list
│   │       ├── data_processing.py # URL cleaning and feature extraction
│   │       └── inference.py       # model loading and prediction
│   ├── models/
│   │   ├── hist_gradient_boosting.joblib   # trained model
│   │   └── feature_reference.json          # average feature values per class
│   ├── scripts/
│   │   └── make_reference.py      # builds feature_reference.json
│   ├── data/
│   │   └── processed_features.csv
│   ├── requirements.txt           # pinned back-end dependencies
│   └── .env.example               # configuration template
└── frontend/                      # React frontend
    ├── .env.example               # configuration template
    ├── package.json               # pinned front-end dependencies
    ├── package-lock.json          # exact versions of every package
    └── src/
        ├── App.jsx                # routes, session history, health check
        ├── api/client.js          # every call to the back end
        ├── components/            # form, result card, gauge, signals, charts, error boundary
        ├── pages/                 # Home, How it works, 404
        ├── styles/                # design tokens and styles
        └── utils/                 # URL validation, feature names
```

## Architecture
<!-- Brief, 3 Deliverables: "an architecture diagram" -->
  ```
   Browser (React, http://localhost:5173)
   ┌──────────────────────────────────────────────┐
   │ InspectForm ── validates the URL first       │
   │      │                                       │
   │ api/client.js ── fetch, reads JSON errors    │
   └──────┼───────────────────────────────────────┘
          │  POST /api/predict  {"url": "..."}
          │  GET  /api/model-info, /api/health
          ▼
   FastAPI (http://localhost:8000)
   ┌──────────────────────────────────────────────┐
   │ security headers → CORS → error catcher      │
   │   → body size limit (32 KB)                  │
   │ prediction slots (max 4 at once)             │
   │ Pydantic PredictRequest (1 to 2,048 chars)   │
   │      │                                       │
   │ predict_url: clean URL → 9 features → model  │  model loaded once at startup
   │      │                         (joblib file) │
   │ build_signals → PredictResponse (JSON)       │
   └──────────────────────────────────────────────┘
          │  verdict, confidence, trust score, features, signals
          ▼
   ResultCard, TrustGauge, SignalCards, FeatureChart, HistoryChart
  ```

## Dependencies
<!-- Brief, 2.4 Running the application: "Dependency versions are pinned, so the application runs the same way for the marker as it does for you" -->
- **Backend:** `backend/requirements.txt`
- **Frontend:** `frontend/package.json` (exact versions), locked in `frontend/package-lock.json`

## Security

### Threat model
**Who would want to attack PhishLens?** Any malicious user who would want their phishing URL to pass as legitimate, or to learn what the model keys on so they can craft their URLs to slip past it. Anyone flooding an API in an attempt to take it down, or sending many queries, or someone who scans the web app for weaknesses, such as a misconfigured header or a secret left in the code.

**What are they trying to achieve?** The phisher wants a wrong answer (a phishing URL scored as legitimate) or knowledge of the model's decision boundary. The abuser wants the service to become unavailable for real users, or wants to extract value from it. The opportunist wants a foothold: anything that leaks information or lets them run code, such as the model file being swapped for a malicious one.

**What can they actually do to it?** They can skip the front end and send requests straight to the API with a tool such as curl, so every defence is enforced on the back end. The only input they control is a URL of up to 2,048 characters. PhishLens never visits the URL, runs no system commands, and has no database, file uploads or user accounts, so most risks in section 2.7 do not apply (see the table). What remains is flooding the API, probing or evading the model with repeated queries, and exploiting misconfiguration or vulnerable dependencies. Our two defences target misconfiguration and denial of service.

| Risk (section 2.7) | Applies? | Why |
|---|---|---|
| Unsafe model loading | Yes | The model is loaded with `joblib`, which can run code hidden in the file |
| Command injection | No | The back end runs no system commands |
| Missing rate limiting | Yes | FastAPI sets no limit; anyone can send unlimited requests |
| SQL injection | No | No database |
| Unsafe file upload | No | No file uploads |
| Misconfiguration and vulnerable dependencies | Yes | Applies to every application |
| Denial of service | Yes | Running the model costs more than sending a request |
| Server-side request forgery (SSRF) | No | The back end never visits or looks up the submitted URL |
| Broken access control | No | No user accounts |

### Security hygiene
| Requirement | How PhishLens meets it | Where |
|---|---|---|
| User input is never rendered as HTML | React escapes all text. The checked URL is shown as plain text only, never in `href`, `window.open` or `dangerouslySetInnerHTML` | `frontend/src/components/ResultCard.jsx` |
| Size limits enforced on the back end | URL: 1 to 2,048 characters, checked by Pydantic (only 2 of 632,907 training URLs are longer). Request body: 32 KB, checked before it is read | `backend/app/schemas.py`, `backend/app/main.py` |
| CORS allows only our front end | One exact origin from `FRONTEND_ORIGIN`; methods GET and POST and header `Content-Type` only; no credentials | `backend/app/main.py` |
| Secrets kept out of source code | The app needs no secrets. Settings come from environment variables; `.env` is git-ignored and `.env.example` is the template. TODO: gitleaks result | `backend/app/config.py` |

CORS only stops other websites from calling the API through a visitor's browser. It does not stop direct requests such as curl, so the defences below are enforced on the server.

### Defences (section 2.7)

#### Defence 1: Misconfiguration and vulnerable dependencies (Intermediate)

**Attack:** Default settings leave weaknesses, such as missing security headers that allow clickjacking or content-type sniffing, and any library can carry a publicly known vulnerability.

**Defence** (`backend/app/main.py`):
- Security headers on every response: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`
- Content Security Policy: API responses load nothing and may not be framed (`default-src 'none'; form-action 'none'; frame-ancestors 'none'`). `/docs` may load only Swagger UI from `cdn.jsdelivr.net` and one start-up script fixed by its hash
- `/redoc` switched off, as it is not needed

**Results:**

| Check | Before | After |
|---|---|---|
| `pip-audit -r requirements.txt` | No known vulnerabilities (4 Nov 2026) | TODO: re-run before submission |
| `npm audit` | Not run (no front end yet) | 0 vulnerabilities (8 Nov 2026) |
| OWASP ZAP scan of the API and `/docs` | 6 alerts (4 Nov 2026) | 4 alerts (7 Nov 2026), all accepted below |

| ZAP alert | Risk | Result |
|---|---|---|
| Content Security Policy (CSP) Header Not Set | Medium | Fixed |
| Missing Anti-clickjacking Header | Medium | Fixed |
| X-Content-Type-Options Header Missing | Low | Fixed |
| CSP: Failure to Define Directive with No Fallback | Medium | Fixed with `form-action 'none'` |
| CSP: style-src unsafe-inline | Medium | Accepted: Swagger UI needs inline styles, which cannot run code. Applies to `/docs` only |
| Sub Resource Integrity Attribute Missing | Medium | Accepted: FastAPI's docs page loads Swagger UI from a CDN without integrity hashes. The CSP allows only that one CDN |
| Cross-Domain JavaScript Source File Inclusion | Low | Accepted: same cause as above |
| Modern Web Application | Informational | No change needed (ZAP's own advice) |

**Cost:**
- If a FastAPI upgrade changes the docs page, the script hash must be updated or `/docs` loads blank
- `pip-audit` and ZAP only find issues known when they run, so they must be repeated after any dependency change

#### Defence 2: Denial of service (Advanced)

**Attack:**
- **One expensive request:** FastAPI reads and parses the whole body before checking the 2,048-character limit, then echoes the input back in its `422` error. A 200 MB request is read, parsed and sent back in full, and every other user waits meanwhile.
- **Many requests at once:** every prediction is accepted and queued in the same 40 worker threads that `/api/health` uses, so real users wait behind the attacker.

**Defence** (`backend/app/main.py`):
- **Body size limit** (`limit_body_size` middleware): a request that declares more than 32 KB gets `413`, decided from its headers before any of the body is read. A `POST` that does not declare its size (a chunked upload) gets `411`. The largest valid request is about 24 KB, so no valid URL is refused.
- **Prediction slots** (`take_prediction_slot` on `POST /api/predict`): at most 4 predictions run at once, and any extra request gets `503` with `Retry-After: 1` straight away instead of queueing. A slot is taken only after the body has arrived, so slow senders cannot hold one. `/api/health` and `/docs` do not use slots, so they stay responsive.
- **Why 4:** a prediction takes a few milliseconds, and Python runs only one thread of Python code at a time, so more predictions side by side do not finish sooner.
- **Already in the design:** `predict` is a plain `def`, so slow inference runs in a worker thread instead of blocking the server, and feature extraction uses no regular expressions that a crafted URL could make backtrack.

**Results** ("before" is git tag `before-dos`; during each test a real user checks `/api/health` 10 times a second):

| Test 1: one 200 MB request | Before | After |
|---|---|---|
| Response | `422` after 1.12 s, with all 200 MB sent back | `413` after 0.003 s |
| Real user, slowest answer | 0.94 s | 0.05 s |

| Test 2: 100 users nonstop for 15 s | Before | After |
|---|---|---|
| Served (`200`) / refused (`503`) | 380 / 0 | 251 / 30,133 |
| Average response time | 4.2 s | 0.05 s |
| Real user, answers in 20 s | 52 | 200 |
| Real user, slowest answer | 3.71 s | 0.08 s |

**Variations** (with the defence):
- Large body with no declared size: `411`, and none of the body is sent
- Large body that declares a small size: only the declared bytes are read, then the connection is closed
- Large body sent without waiting for the server's go-ahead: `413`, and the connection is closed after a few MB

**Cost:**
- During a flood, some real users also get `503` and must retry. One attacker sending flat out can still crowd others out; a per-client rate limit or a CDN in front of the server would fix that.
- Turning requests away still uses CPU. With instant `503`s the attacker sent 80 times more requests, so fewer predictions completed (251 vs 380).
- Uploads without a declared size are refused, though browsers always declare it.

### Advanced security (section 2.8)
<!-- Brief, 2.8: "Choose one, name it in your README, and do it properly. Only one is marked." -->
TODO

## References
<!-- Brief, 3 Deliverables: "references in Harvard style" -->
- TODO
