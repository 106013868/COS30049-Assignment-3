# PhishLens

Web application that checks whether a URL is phishing or legitimate, using a machine learning model trained on URL features. The URL is analysed as text only and is never visited.

- **Backend**: FastAPI 0.162.0, scikit-learn 1.9.1, Python 3.13
- **Frontend**: React 19.3.1 with Vite 8.3.6, React Router 8.5.1 and Recharts 3.10.1
- **ML Model**: HistGradientBoosting classifier (Pedregosa et al. 2011) (from Assignment 2)

**Group:**

| Name | Student ID | Role |
|---|---|---|
| Tim Johnson | 106013868 | Security |
| Raza Syed | 104041595 | Back end, front end |
| Anthony Duero | 104561608 | Video |

## Quick Start

### Prerequisites
- Python 3.13
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
| Misconfiguration and vulnerable dependencies | Yes | Applies to every application (OWASP Foundation 2025) |
| Denial of service | Yes | Running the model costs more than sending a request |
| Server-side request forgery (SSRF) | No | The back end never visits or looks up the submitted URL |
| Broken access control | No | No user accounts |

### Security hygiene
| Requirement | How PhishLens meets it | Where |
|---|---|---|
| User input is never rendered as HTML | React escapes all text. The checked URL is shown as plain text only, never in `href`, `window.open` or `dangerouslySetInnerHTML` | `frontend/src/components/ResultCard.jsx` |
| Size limits enforced on the back end | URL: 1 to 2,048 characters, checked by Pydantic (only 2 of 632,907 training URLs are longer). Request body: 32 KB, checked before it is read | `backend/app/schemas.py`, `backend/app/main.py` |
| CORS allows only our front end | One exact origin from `FRONTEND_ORIGIN`; methods GET and POST and header `Content-Type` only; no credentials | `backend/app/main.py` |
| Secrets kept out of source code | The app needs no secrets. Settings come from environment variables; `.env` is git-ignored and `.env.example` is the template. | `backend/app/config.py` |

CORS only stops other websites from calling the API through a visitor's browser. It does not stop direct requests such as curl, so the defences below are enforced on the server.

### Defences (section 2.7)

#### Defence 1: Misconfiguration and vulnerable dependencies (Intermediate)

**Attack:** Default settings leave weaknesses, like missing headers that allow clickjacking, and libraries can carry known vulnerabilities.

**Defence:**
- Back end (`backend/app/main.py`): `nosniff`, `X-Frame-Options: DENY` and `Referrer-Policy` headers on every response, a Content Security Policy that lets API responses load nothing, and `/redoc` switched off
- Front end (`frontend/vite.config.js`): the same headers, a Content Security Policy limited to our own files, Google Fonts and our API, and the app served as a built version instead of the development server

**Results** (reports in `docs/`):

`pip-audit` - No known vulnerabilities (10 Nov)
`npm audit` - 0 vulnerabilities (10 Nov)

| Check | Before | After |
|---|---|---|
| ZAP (ZAP n.d.), API and `/docs` | 6 alerts | 4, all accepted and justified below |
| ZAP (ZAP n.d.), front end | 9 alerts | 2, both accepted and justified below |

Fixed: the missing Content Security Policy, anti-clickjacking and nosniff headers on both, the API's missing `form-action` rule, and the front end's Path Traversal.

| Still open | Risk | Why it's accepted |
|---|---|---|
| Sub Resource Integrity Attribute Missing | Medium | Swagger UI (on `/docs`) and Google Fonts load from outside servers without integrity hashes: FastAPI adds none, and Google Fonts changes its CSS per browser. The CSP allows only those servers |
| Cross-Domain JavaScript Source File Inclusion | Low | Same cause, `/docs` only |
| CSP: style-src unsafe-inline | Medium | Swagger UI needs inline styles, which can't run code. `/docs` only |
| Modern Web Application | Info | ZAP says no change is needed |

**Cost:**
- The `/docs` CSP pins one script by its hash, so a FastAPI upgrade can break `/docs` until the hash is updated
- The built front end must be rebuilt after every change
- Audits and scans only find known issues, so they must be repeated after any dependency change

#### Defence 2: Denial of service (Advanced)

***Attack:** One huge request (FastAPI read and parsed the whole body before checking the URL length, so a 200 MB request froze other users), or many requests at once (every prediction was queued, so real users waited behind the attacker).

**Defence** (`backend/app/main.py`):
- `limit_body_size`: bodies declared over 32 KB get `413` before any of the body is read, and `POST`s with no declared size get `411`. The largest valid request is about 24 KB
- `take_prediction_slot`: at most 4 predictions run at once, and extra requests get `503` with `Retry-After: 1` instead of queueing. `/api/health` and `/docs` don't need a slot

**Results**:

| | Before | After |
|---|---|---|
| One 200 MB request | `422` after 1.12 s, all 200 MB sent back | `413` after 0.003 s |
| Real user's slowest answer during it | 0.94 s | 0.05 s |
| 100 users for 15 s: served / refused | 380 / 0, 4.2 s each | 251 / 30,133, 0.05 s each |
| Real user's slowest answer during it | 3.71 s | 0.08 s |

**Cost:**
- During a flood some real users get `503` and must retry. One attacker can still crowd others out
- Turning requests away uses CPU, so fewer predictions completed during the flood (251 vs 380)

### Advanced security (section 2.8)
**Chosen attack: Detection evasion (Machine learning)**

**Attack:** A phisher swaps a letter in the words our model looks for with a Cyrillic look-alike. The word no longer matches, so the URL looks safer to the model but identical to a person. `backend/scripts/evasion/evasion_test.py` attacks our own API with 100 phishing URLs the model only just catches (trust 40 to 50%), trying every combination of words to disguise and keeping the version the model trusts most.

**Defence:** `normalise_url` in `backend/app/ml/data_processing.py` runs before the features are extracted. It turns full-width and maths letters into plain ones, removes accents and invisible characters, and swaps Cyrillic, Greek and other look-alikes for Latin letters (Whistler 2024).

**Results** (`docs/evasion-before.txt`, `docs/evasion-after.txt`):

| | Before | After |
|---|---|---|
| Look-alikes that got past | 47 of 100 | 0 of 100 |

Without the defence, the disguise worked on about half the URLs. With it, every look-alike scores exactly like its original, and Greek, full-width and zero-width-space disguises are caught too.

**Cost:**
- The table only covers the look-alikes we listed; Unicode's full confusables list (Davis and Suignard 2025) would cover the rest
- The model was trained without this step, so 0.01% of real URLs in our data get slightly different features
- Look-alikes alone don't lower the score

## References

- Anthropic (2026). *Claude* [Large language model]. Available at: https://claude.ai [Accessed 11 Nov. 2026].
- Davis, M. and Suignard, M. (2025). *Unicode Technical Standard #39: Unicode Security Mechanisms*, Revision 31. [online] Unicode Consortium. Available at: https://www.unicode.org/reports/tr39/tr39-31.html [Accessed 11 Nov. 2026].
- OWASP Foundation (2025). *A02:2025 Security Misconfiguration*. [online] OWASP Top 10:2025. Available at: https://top10.owasp.org/2025/A02_2025-Security_Misconfiguration/ [Accessed 11 Nov. 2026].
- Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, pp. 2825–2830.
- Siddhartha, M. (2021). *Malicious URLs dataset*. [online] www.kaggle.com. Available at: https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset [Accessed 7 Oct. 2026].
- Whistler, K. (2024). *Unicode Standard Annex #15: Unicode Normalization Forms*, Revision 56. [online] Unicode Consortium. Available at: https://www.unicode.org/reports/tr15/tr15-56.html [Accessed 11 Nov. 2026].
- www.kaggle.com (n.d.). *Phishing Site URLs*. [online] Available at: https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls [Accessed 7 Oct. 2026].
- ZAP (n.d.). *ZAP by Checkmarx*. [online] Available at: https://www.zaproxy.org/ [Accessed 11 Nov. 2026].

### Use of generative AI
We used Claude (Anthropic 2026) to help with planning the implementation and debugging of various parts of the project. The tool was used to help explore potential approaches, clarify technical concepts, and suggest solutions to challenges. The source code was written, reviewed and implemented by the team.
