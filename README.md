# PhishLens

Web application that checks whether a URL is phishing or legitimate, using a machine learning model trained on URL features. The URL is analysed as text only and is never visited.

- **Backend**: FastAPI 0.162.0, scikit-learn 1.9.1, Python 3.13
- **Frontend**: React (TODO)
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
- Python 3.13
- TODO: Node.js and npm versions

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
TODO

### Configuration
| Variable | File | Purpose | Default |
|---|---|---|---|
| `FRONTEND_ORIGIN` | `backend/.env` | The only origin allowed by CORS | `http://localhost:5173` |
| `LOG_LEVEL` | `backend/.env` | TODO | `info` |

## Usage

### Checking a URL in the app
TODO (front end)

### Checking a URL through the API
1. Start the backend
2. Open `http://127.0.0.1:8000/docs`
3. Open **POST /api/predict**, click **Try it out**
4. Enter a URL in the request body and click **Execute**
5. View the verdict, confidence, trust score and signals in the response

## Model Performance

Assignment 2 results on the grouped test split (no website appears in both training and test data). The brief states model accuracy is not marked in this assignment.

| Task | Model | Accuracy | Precision | Recall | F1-Score |
|------|-------|----------|-----------|--------|----------|
| Phishing URL detection | HistGradientBoosting (balanced) | 0.724 | 0.570 | 0.690 | 0.624 |

## API Documentation

<!-- Brief, 3 Deliverables: "API documentation. Use the /docs page that FastAPI generates for you. Make sure every endpoint has a description and an example request and response." -->

Interactive API docs available at `http://127.0.0.1:8000/docs` when backend is running. The second docs page FastAPI provides by default (`/redoc`) is switched off.

### Endpoints

**GET /api/health**

Server and model status. Returns `200` when the model is loaded, `503` when it is not.
```json
{"status": "ok", "model_loaded": true}
```

**POST /api/predict**

Scores one URL. Returns `200`, `422` for invalid input, `503` if the model is not loaded.

Request:
```json
{
  "url": "http://secure-login.verify-account.xyz/signin"
}
```

Response:
```json
{
  "url": "secure-login.verify-account.xyz/signin",
  "verdict": "phishing",
  "confidence": 0.81,
  "trust_score": 19,
  "features": {
    "url_length": 38, "domain_length": 31, "path_length": 7,
    "digit_count": 0, "special_character_count": 5, "dot_count": 2,
    "subdomain_count": 1, "has_ip": 0, "suspicious_keyword_count": 4
  },
  "signals": [
    {"id": "keywords", "title": "Suspicious wording",
     "description": "Contains: login, signin, verify, secure",
     "status": "warn", "used_by_model": true}
  ],
  "model_version": "hgb-a2-1.0"
}
```

### Error format
<!-- Rubric, Back end 2) Error handling (2 pts): "Invalid input receives a clear message with the right status code. Every error, including unexpected ones such as a failing model call, is returned in the same JSON format, without stack traces or other internal details." -->
TODO

## Project Structure
```
COS30049-Assignment-3/
├── README.md
├── .gitignore
├── backend/                       # FastAPI backend
│   ├── app/
│   │   ├── main.py                # API endpoints, CORS and security headers
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
    └── TODO
```

## Architecture
<!-- Brief, 3 Deliverables: "an architecture diagram" -->
TODO: architecture diagram

## Dependencies
<!-- Brief, 2.4 Running the application: "Dependency versions are pinned, so the application runs the same way for the marker as it does for you" -->
- **Backend:** `backend/requirements.txt`
- **Frontend:** TODO

## Security

### Threat model
**Who would want to attack PhishLens?** Any malicious user who would want their phishing URL to pass as legitimate, or to learn what the model keys on so they can craft their URLs to slip past it. Anyone flooding an API in an attempt to take it down, or sending many queries, or someone who scans the web app for weaknesses, such as a misconfigured header or a secret left in the code.

**What are they trying to achieve?** The phisher wants a wrong answer (a phishing URL scored as legitimate) or knowledge of the model's decision boundary. The abuser wants the service to become unavailable for real users, or wants to extract value from it. The opportunist wants a foothold: anything that leaks information or lets them run code, such as the model file being swapped for a malicious one.

**What can they actually do to it?** Not much, by design, but the little that remains is where we focus. An attacker bypasses the front end and sends requests straight to the API with a tool such as curl, so every real defence is enforced on the back end. The only input they control is a URL string, capped at 2,048 characters. Because PhishLens never visits the submitted URL, makes no outbound requests, stores nothing in a database, and has no user accounts, several whole classes of attack (SSRF, command injection, SQL injection, unsafe file upload, broken access control) do not apply. What an attacker can still do is flood the API, probe or evade the model through repeated queries, and exploit any misconfiguration or vulnerable dependency. The table below maps each risk from section 2.7 to whether our design exposes it. Our defences target the two risks that remain open to a direct attacker.

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
| User input is never rendered as HTML | TODO (front end) | TODO |
| Size limits enforced on the back end | URL must be 1 to 2,048 characters, checked by Pydantic before the endpoint runs. 2,048 is the common practical URL limit; in the training data 99.99% of URLs are 645 characters or shorter and only 2 of 632,907 exceed 2,048 | `backend/app/schemas.py` |
| CORS allows only our front end | One exact origin from `FRONTEND_ORIGIN`; methods GET and POST and header `Content-Type` only; no credentials | `backend/app/main.py` |
| Secrets kept out of source code | The app needs no secrets. Configuration is read from environment variables; `.env` is git-ignored and `.env.example` is the template. TODO: gitleaks result | `backend/app/config.py` |

CORS is enforced by browsers, so it stops other websites from using visitors' browsers to call the API. It does not stop direct requests (for example with curl), which is why the defences below are enforced on the server.

### Defences (section 2.7)

#### Defence 1: Misconfiguration and vulnerable dependencies (Intermediate)

**Attack:** Default settings leave weaknesses an attacker can use, such as missing security headers that allow clickjacking or content-type sniffing, and libraries with publicly known vulnerabilities.

**Defence and where in the code:**
- Security headers middleware added to every response (`backend/app/main.py`):
  - `X-Content-Type-Options: nosniff`: browsers must trust the declared content type
  - `X-Frame-Options: DENY`: no other site may show our pages inside a frame
  - `Referrer-Policy: no-referrer`: our URLs are not leaked to other sites
  - Content Security Policy for the API: `default-src 'none'; form-action 'none'; frame-ancestors 'none'` (JSON responses load nothing and may not be framed)
  - Content Security Policy for `/docs`: allows only the Swagger UI files from `cdn.jsdelivr.net`, the FastAPI favicon, and one inline start-up script identified by its SHA-256 hash; requests only to our own server
- `/redoc` switched off, as it is not needed (less attack surface)

**Results:**

| Check | Before | After |
|---|---|---|
| `pip-audit -r requirements.txt` (4 Nov 2026) | No known vulnerabilities found | TODO: re-run before submission |
| `npm audit` | TODO (front end) | TODO |
| OWASP ZAP scan of the running API and `/docs` | 6 alerts (4 Nov 2026): 3 Medium, 2 Low, 1 Informational | 4 alerts (7 Nov 2026): 2 Medium, 1 Low, 1 Informational, all justified below |

| ZAP alert | Risk | Before | After |
|---|---|---|---|
| Content Security Policy (CSP) Header Not Set | Medium | Found on `/docs` | Fixed |
| Missing Anti-clickjacking Header | Medium | Found on `/docs` | Fixed |
| X-Content-Type-Options Header Missing | Low | Found on 4 URLs | Fixed |
| CSP: Failure to Define Directive with No Fallback (`form-action`) | Medium | Not tested (no CSP yet) | Found, then fixed by adding `form-action 'none'` |
| CSP: style-src unsafe-inline | Medium | Not tested (no CSP yet) | Justified |
| Sub Resource Integrity Attribute Missing | Medium | Found on `/docs` | Justified |
| Cross-Domain JavaScript Source File Inclusion | Low | Found on `/docs` | Justified |
| Modern Web Application | Informational | Found on `/docs` | Justified |

**Justifications for remaining alerts:**
- **CSP: style-src unsafe-inline:** Swagger UI sets styles directly on its page elements and does not work without this. Inline styles cannot run code, and scripts stay locked down to the CDN plus one script fixed by its hash. It applies to `/docs` only; the API's own policy has no exceptions.
- **Sub Resource Integrity Attribute Missing:** FastAPI's built-in docs page does not add integrity hashes to the Swagger UI files. The risk is a compromised CDN. It is accepted because `/docs` is a developer page required by the brief, it loads from one named CDN, and the CSP blocks every other source. Self-hosting the files would remove this finding; we chose to keep the CDN so we do not have to maintain our own copies of Swagger UI.
- **Cross-Domain JavaScript Source File Inclusion:** Same cause and reasoning as above.
- **Modern Web Application:** Informational only; ZAP's own solution states no changes are required.
- **Browser console:** one CSP report remains for Swagger's CSS source map (`swagger-ui.css.map`). It is requested only by browser developer tools, not by the page, so `connect-src` is kept to `'self'`.

**Cost:**
- The `/docs` script hash must be updated if a FastAPI upgrade changes its docs page, otherwise `/docs` loads blank
- `pip-audit` and the ZAP scan only reflect known issues at the time they are run, so they must be repeated after any dependency change

#### Defence 2: Denial of service (Advanced)
TODO

### Advanced security (section 2.8)
<!-- Brief, 2.8: "Choose one, name it in your README, and do it properly. Only one is marked." -->
TODO

## References
<!-- Brief, 3 Deliverables: "references in Harvard style" -->
- TODO
