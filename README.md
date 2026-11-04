# PhishLens

<!-- Brief, 3 Deliverables: "README. Setup and run instructions, an architecture diagram, your pinned dependency versions, your threat model, references in Harvard style, and the defences and advanced attack you want marked."
     Rubric, Source code 2) Code quality and README (2 pts): "The README covers everything Section 3 asks for, including the architecture diagram, threat model, Harvard references, and the defences to be marked." -->

TODO: summary

**Group:** TODO: group name

| Name | Student ID | Role |
|---|---|---|
| Tim Johnson | 106013868 | Security |
| Raza Syed | 104041595 | Back end, front end |
| Anthony Duero | 104561608 | Video |

---

## 1. Setup and run

<!-- Brief, 2.4 Running the application: "The whole application starts from your README on a clean machine"
     Rubric, Source code 1) Runs from the README (2 pts): "Following the README alone on a clean machine starts both the front end and the back end, with no fixes needed. Dependency versions are pinned." -->

### Requirements
- Python TODO: version
- TODO: front end requirements

### Back end
```bash
cd backend
python -m venv .venv               # macOS: python3 -m venv .venv
.venv\Scripts\activate             # macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env             # macOS: cp .env.example .env
uvicorn app.main:app
```
API: http://127.0.0.1:8000 · Interactive docs: http://127.0.0.1:8000/docs

### Front end
TODO

### Configuration
| Variable | File | Purpose | Default |
|---|---|---|---|
| `FRONTEND_ORIGIN` | `backend/.env` | The only origin allowed by CORS | `http://localhost:5173` |
| `LOG_LEVEL` | `backend/.env` | TODO | `info` |

---

## 2. Architecture

<!-- Brief, 3 Deliverables: "an architecture diagram" -->

TODO: architecture diagram

### Project structure
```
backend/
  app/
    main.py              API endpoints and CORS middleware
    schemas.py           Pydantic request and response models
    config.py            settings read from environment variables
    signals.py           signal cards shown with each result
    ml/
      config.py          paths, column names, feature list
      data_processing.py URL cleaning and feature extraction (from A2)
      inference.py       model loading and prediction (from A2)
  models/
    hist_gradient_boosting.joblib   trained model (A2)
    feature_reference.json          average feature values per class
  scripts/
    make_reference.py    builds feature_reference.json from data/processed_features.csv
  data/
    processed_features.csv
  requirements.txt
  .env.example
frontend/
  TODO
```

---

## 3. API

<!-- Brief, 3 Deliverables: "API documentation. Use the /docs page that FastAPI generates for you. Make sure every endpoint has a description and an example request and response."
     Rubric, Back end 1) API design and documentation (3 pts): "(4) /docs describes every endpoint, with an example request and response." -->

Full documentation: http://127.0.0.1:8000/docs

| Method | Path | Purpose | Status codes |
|---|---|---|---|
| GET | `/api/health` | Server and model status | 200, 503 |
| POST | `/api/predict` | Score one URL | 200, 422, 503 |

### Error format

<!-- Brief, 2.2 Back end: "Every error, including unexpected ones, returned in one consistent JSON format, without internal details such as stack traces"
     Rubric, Back end 2) Error handling (2 pts): "Invalid input receives a clear message with the right status code. Every error, including unexpected ones such as a failing model call, is returned in the same JSON format, without stack traces or other internal details." -->

TODO

---

## 4. Dependencies

<!-- Brief, 2.4 Running the application: "Dependency versions are pinned, so the application runs the same way for the marker as it does for you" -->

- **Back end:** every package pinned with `==` in `backend/requirements.txt`
- **Front end:** TODO

TODO: table of main packages and versions

---

## 5. Security

### 5.1 Threat model

<!-- Brief, 2.6 Threat model: "Write a short threat model that answers three questions.
     1. Who would want to attack your application?
     2. What are they trying to achieve?
     3. What can they actually do to it?"
     "Half a page in your README is enough, and you should summarise it in your video before demonstrating your defences."
     Rubric, Security 2) Threat model (1 pt): "Answers the three questions specifically for this application, identifies which risks in section 2.7 the design actually exposes, and says briefly why the others do not apply." -->

**Who would want to attack PhishLens?**
TODO

**What are they trying to achieve?**
TODO

**What can they actually do to it?**
TODO

**Risks from section 2.7**

| Risk | Applies? | Why |
|---|---|---|
| Unsafe model loading | TODO | TODO |
| Command injection | TODO | TODO |
| Missing rate limiting | TODO | TODO |
| SQL injection | TODO | TODO |
| Unsafe file upload | TODO | TODO |
| Misconfiguration and vulnerable dependencies | TODO | TODO |
| Denial of service | TODO | TODO |
| Server-side request forgery (SSRF) | TODO | TODO |
| Broken access control | TODO | TODO |

### 5.2 Security hygiene

<!-- Rubric, Security 1) Hygiene requirements (2 pts): "All four requirements in section 2.3 are met on the back end and set sensibly. User input is never rendered as HTML, size limits suit each input, CORS lists the front end's exact origin, and no secret appears anywhere in the repository." -->

| Requirement | How PhishLens meets it | Where |
|---|---|---|
| User input is never rendered as HTML | TODO | TODO |
| Size limits enforced on the back end | URL must be 1 to 2,048 characters, checked by Pydantic before the endpoint runs | `backend/app/schemas.py` |
| CORS allows only our front end | One exact origin from `FRONTEND_ORIGIN`; methods GET and POST and header `Content-Type` only | `backend/app/main.py` |
| Secrets kept out of source code | `.env` is git-ignored and `.env.example` is the template. TODO | `backend/app/config.py` |

### 5.3 Defences (section 2.7)

<!-- Brief, 2.7: "Choose up to two defences, from risks your application actually has, and name them in your README. Only those two are marked, so building more earns nothing extra."
     "The highest marks go to a defence that stops the attack and its obvious variations, is shown in your video with the attack succeeding without the defence and failing with it, is justified by your threat model, and has its cost explained." -->

**Defence 1: TODO (level: TODO)**
- Attack: TODO
- Defence and where in the code: TODO
- How to test it: TODO
- Cost: TODO

**Defence 2: TODO (level: TODO)**
- Attack: TODO
- Defence and where in the code: TODO
- How to test it: TODO
- Cost: TODO

### 5.4 Advanced security (section 2.8)

<!-- Brief, 2.8: "Choose one, name it in your README, and do it properly. Only one is marked."
     "Measure before and after. Implement the attack, measure it, add your defence, and measure again."
     "Explain what the defence costs."
     Rubric, Innovation 2) Advanced security (4 pts): "The attack is implemented, and its success is measured with enough repetitions to be convincing, for example, as distributions rather than single runs. The defence is implemented, and the same measurement is repeated, showing how far the attack's success falls. Results are interpreted honestly, including when an obvious defence turns out not to work, and the cost of the defence is measured or clearly explained." -->

**Attack: TODO**
- How the attack works: TODO
- Measurement before the defence: TODO
- Defence: TODO
- Measurement after the defence: TODO
- Cost of the defence: TODO
- How to reproduce: TODO

---

## 6. References

<!-- Brief, 3 Deliverables: "references in Harvard style" -->

- TODO
- TODO: generative AI use
