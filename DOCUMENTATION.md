# AI Resume Screening System - Technical Documentation

This document provides a comprehensive breakdown of the core technologies, algorithms, and architectural decisions used to build the AI Resume Screening System. Every section is verified against the actual source code.

---

## 1. Core Technology Stack

The application is built on a lightweight Python backend designed for rapid text processing.

*   **Backend Framework:** `Flask` (`app.py`, `web_app/routes.py`)
    *   **Why:** Flask is incredibly lightweight and allows rapid prototyping of REST APIs. It does not enforce a rigid directory structure (unlike Django), making it ideal for a custom AI micro-architecture where each component (parsing, NLP, matching, explainability) is an independent module.
*   **Frontend UI:** `HTML5`, `Vanilla CSS`, `Bootstrap 5`, `Jinja2`
    *   **Why:** Bootstrap 5 allows responsive UI development without thousands of lines of custom CSS. Jinja2 templates let the Python backend dynamically inject complex AI explainability variables (matched skills, score breakdowns, chart data) directly into the HTML before sending it to the browser.
*   **Visualization:** `Matplotlib` (`visualization/charts.py`) + `Chart.js` (browser-side)
    *   **How:** The backend (`Visualizer` class) renders 3 charts using `matplotlib` with a non-interactive `Agg` backend, encodes each chart as a **Base64 PNG string**, and injects it directly into the HTML `<img>` tag. This means **no chart files are ever saved to disk** — the chart lives entirely in memory. Chart.js is also available in the browser for any client-side rendering needs.
*   **Database & Authentication:** `SQLite`, `Flask-SQLAlchemy`, `Flask-Login`, `Authlib`, `Werkzeug`
    *   **Why:** SQLite is self-contained and requires no external server — perfect for local storage of user profiles. `Flask-Login` manages session state and protects routes with `@login_required`. `Authlib` handles the Google OAuth 2.0 SSO handshake. Passwords for email/password accounts are securely hashed using `werkzeug.security`.

---

## 2. Project File Structure

```
AI_Resume_Screening_System/
│
├── app.py                      # Entry point — creates Flask app, registers blueprints
├── models.py                   # SQLAlchemy User model (email, name, password_hash, sso_provider, avatar_url)
├── requirements.txt            # All Python dependencies
├── .env                        # Local secrets (gitignored)
├── .env.example                # Template for environment variables (safe to commit)
│
├── resume_parser/
│   └── parser.py               # ResumeParser class — handles PDF, DOCX, TXT, PNG, JPG
│
├── nlp_processing/
│   ├── processor.py            # NLPProcessor class — SpaCy pipeline, skill extraction, YoE
│   └── skills_db.py            # Master list of TECHNICAL_SKILLS and SOFT_SKILLS
│
├── feature_extraction/
│   └── extractor.py            # FeatureExtractor class — TF-IDF vectorization
│
├── matching_engine/
│   └── matcher.py              # MatchingEngine class — weighted score computation
│
├── explainable_ai/
│   └── explainer.py            # Explainer class — translates scores to plain-English feedback
│
├── visualization/
│   └── charts.py               # Visualizer class — matplotlib charts as base64 PNGs
│
└── web_app/
    ├── routes.py               # All Flask routes — upload, analyze, poll, results
    ├── auth.py                 # Authentication — email/password + Google OAuth SSO
    └── templates/
        ├── home.html
        ├── login.html
        ├── register.html
        ├── upload.html         # Config dashboard with AI weight sliders
        ├── analyze.html        # Intermediate page that triggers background analysis
        └── results.html        # Final output dashboard
```

---

## 3. Text Parsing & OCR Pipeline

Found in `resume_parser/parser.py`. This is the first stage — every uploaded file must be converted to plain text before any AI processing can begin.

### Supported File Formats
`.pdf`, `.docx`, `.txt`, `.png`, `.jpg`, `.jpeg`

### Extraction Strategy (per format)

| Format | Library | Strategy |
|---|---|---|
| `.pdf` | `PyPDF2` | Extracts text page-by-page. If `< 50 chars` returned (scanned PDF), falls back to OCR. Also detects fake PDFs (image renamed to `.pdf`) by checking the `%PDF` magic byte header. |
| `.docx` | `python-docx` | Iterates all `doc.paragraphs` and joins their `.text`. |
| `.txt` | Built-in `open()` | Direct UTF-8 read with `errors='ignore'`. |
| `.png` / `.jpg` | `Pillow` + Tesseract | Full OCR pipeline (see below). |

### OCR Pipeline (for Image-Based Resumes & Scanned PDFs)

When a scanned PDF or image file is encountered, the parser runs a **4-step preprocessing pipeline** before OCR:

1.  **RGBA Flattening** — Transparent images (RGBA/P mode) are pasted onto a white RGB background.
2.  **Grayscale Conversion** — Removes color noise.
3.  **Contrast Boost (3×)** + **Sharpening (2×)** — Using `PIL.ImageEnhance` to make text edges crisp.
4.  **Adaptive Binarization** — Pixels below intensity `140` become pure black; above become pure white.

**Why direct subprocess Tesseract, not `pytesseract`?** The `pytesseract` wrapper has a known UTF-8 decode bug. This system calls the **Tesseract CLI directly via `subprocess`** (`tesseract input.png output_base --psm 3 -l eng`) and reads the output `.txt` file manually with `errors='ignore'`. For scanned PDFs, `pdf2image` converts each page to a 300 DPI image first, then each page is run through the same pipeline.

### Text Preprocessing (`_preprocess`)
After extraction, text is normalized:
- **Lowercased** entirely.
- **Whitespace normalized** (`\s+` → single space).
- Punctuation is **intentionally preserved** to protect tokens like `C++`, `Node.js`, and `1-3 Yrs`.

---

## 4. NLP Processing Engine

Found in `nlp_processing/processor.py`. The NLP engine runs on every uploaded document (both Job Description and each Resume).

*   **Core Library:** `SpaCy` (`en_core_web_sm` model)
    *   **Why:** SpaCy is an industry-standard, execution-optimized NLP library. The `sm` (small) English model is used to keep RAM low while still providing accurate tokenization and Named Entity Recognition (NER).

### What `NLPProcessor.process()` Returns

```python
{
    'tokens': [...],              # Non-stopword, non-punctuation tokens
    'lemmas': [...],              # Lemmatized versions of the above tokens
    'entities': [{'text': ..., 'label': ...}],  # NER entities (ORG, DATE, etc.)
    'technical_skills': [...],    # Skills matched against TECHNICAL_SKILLS database
    'soft_skills': [...],         # Skills matched against SOFT_SKILLS database
    'years_of_experience': int,   # Extracted integer YoE
}
```

### Skill Extraction (Regex Word-Boundary Matching)
Technical and soft skills are extracted using **strict Regex Word Boundaries** (`\b`) against the master `skills_db.py` lists:
```python
pattern = r'\b' + re.escape(skill) + r'\b'
```
**Why not SpaCy NER for skills?** Strict `\b` regex guarantees 100% precision — `c` will NOT match inside `communication`. SpaCy NER is used for contextual entities (organizations, dates) but NOT for skill extraction.

### Years of Experience (YoE) Extraction — 3-tier cascade

1.  **Primary Pattern** — Explicit declarations like `"5+ years of experience"`, `"3 yrs exp"`.
2.  **Secondary Pattern** — Reversed declarations like `"Experience: 5+ years"`.
3.  **Date Math Fallback** — Scans for chronological date ranges (e.g., `"June 2024 - August 2025"`), converts them to `datetime` objects, calculates the month spread, and returns `total_months // 12`. Supports both `Month Year` and `Year-only` formats. Also handles `"present"` / `"current"` end dates.

**Edge Case Handling:**
- Values > 40 years are filtered as invalid.
- Date-math totals > 5 years are reset to `0` to prevent **education inflation** (a 4-year BTech would otherwise count as 4 years of work experience).
- If date math yields 0 years but ≥ 6 months are found, it returns `1` (for active interns/juniors).

---

## 5. Feature Extraction (TF-IDF Vectorization)

Found in `feature_extraction/extractor.py`. The `FeatureExtractor` class wraps `scikit-learn`'s `TfidfVectorizer`.

### Primary Vectorizer (used in matching)
```python
TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
```
- **Bi-grams** (`ngram_range=(1,2)`) — Captures two-word phrases like `"machine learning"` as a single feature, simulating semantic understanding without a neural network.
- **`max_features=5000`** — Caps the vocabulary to prevent memory overuse.

### Secondary Vectorizer (semantic embeddings)
```python
TfidfVectorizer(max_features=8000, stop_words='english', ngram_range=(1, 3), sublinear_tf=True)
```
- **Tri-grams** (`ngram_range=(1,3)`) — Captures three-word phrases like `"Natural Language Processing"`.
- **`sublinear_tf=True`** — Applies log normalization to term frequency, which penalizes **keyword stuffing** (if a candidate pastes `"Java"` 50 times in white text, TF-IDF mathematically penalizes the abnormal frequency curve).

> **Note:** The primary `(1,2)` vectorizer is what's actually called in `matcher.py`. The `(1,3)` vectorizer is available as `sentence_embeddings()` for future use.

---

## 6. The Matching & Scoring Engine

Found in `matching_engine/matcher.py`. This is the core AI scoring layer.

The system does **NOT** use heavy LLMs (GPT, BERT, etc.). It uses fast statistical machine learning via `scikit-learn`.

### The Final Weighted Score Formula

```
Final Score = (tech_score × W_tech) + (soft_score × W_soft) + (yoe_score × W_yoe) + (text_sim × W_context) + extra_bonus
```

All weights `W_tech + W_soft + W_yoe + W_context` must always sum to `1.0`. The bonus is an additive offset, capped separately.

**Default weights:** `Tech=60%, YoE=15%, Context=15%, Soft=10%, Bonus cap=5%`

These are configured in real-time by the recruiter via sliders on the Upload Dashboard.

### Score Component Breakdown

| Component | Algorithm | Math |
|---|---|---|
| **Tech Score** | Set Intersection | `len(matched_tech) / len(required_tech)` |
| **Soft Score** | Set Intersection | `len(matched_soft) / len(required_soft)` |
| **YoE Score** | Linear Ratio | `min(resume_yoe / jd_yoe, 1.0)` — capped at 1.0 (no inflation for over-qualified) |
| **Context Score** | TF-IDF Cosine Similarity | Geometric angle between JD and Resume TF-IDF vectors |
| **Extra Skills Bonus** | Additive offset | `min(len(extra_tech) × (bonus_weight / 10), bonus_weight)` |

### Cosine Similarity — Why Not Euclidean Distance?
A 5-page resume and a 1-page resume may be far apart in raw length (Euclidean distance), but if they discuss the same topics, their TF-IDF vectors point in the same *direction* — giving a Cosine Similarity approaching `1.0`. Cosine measures **directional alignment**, not magnitude.

### `compute_scores_detailed()` — What it Returns Per Candidate
```python
{
    'final_score': float,           # 0–100 final weighted score
    'text_similarity': float,       # Raw TF-IDF cosine ×100
    'tech_skill_score': float,      # % of required tech skills matched
    'soft_skill_score': float,      # % of required soft skills matched
    'yoe_score': float,             # YoE ratio ×100
    'tech_contribution': float,     # Points contributed by tech to final score
    'soft_contribution': float,     # Points contributed by soft skills
    'yoe_contribution': float,      # Points contributed by YoE
    'text_contribution': float,     # Points contributed by context match
    'extra_skills_bonus': float,    # Extra bonus points for unrequested skills
    'jd_yoe': int,                  # Required YoE from JD
    'resume_yoe': int,              # Detected YoE from resume
}
```

---

## 7. Explainable AI (XAI)

Found in `explainable_ai/explainer.py`.

**Why XAI?** Black-box AI that outputs an arbitrary number like `"86%"` is dangerous and often rejected by legal compliance and HR teams. Every score must be explainable.

**How it works:** The `Explainer.explain()` method takes the raw score breakdown dict from the Matching Engine and translates it into:
- A plain-English paragraph (e.g., *"Falls short on experience (1 yrs / 3 yrs requested)."*)
- A structured skills report (matched, missing, extra tech skills, matched/missing soft skills)

The explanation classifies candidates into 4 buckets: **Strong (≥75%)**, **Moderate (≥50%)**, **Partial (≥30%)**, **Weak (<30%)**.

**Output per candidate:**
```python
{
    'candidate_name': str,
    'match_score': float,
    'matched_skills': [...],
    'missing_skills': [...],
    'extra_skills': [...],            # Skills in resume but NOT required by JD
    'detected_soft_skills': [...],
    'matched_soft_skills': [...],
    'missing_soft_skills': [...],
    'skill_match_ratio': float,       # % of JD tech skills matched
    'breakdown': {...},               # Full score_details dict from matcher
    'explanation': str,               # Human-readable paragraph
}
```

---

## 8. Visualization Engine

Found in `visualization/charts.py`. The `Visualizer` class generates **3 matplotlib charts**, each returned as a **Base64-encoded PNG string** embedded directly in the HTML — no files written to disk.

| Chart | Method | What it Shows |
|---|---|---|
| Candidate Score Bar Chart | `candidate_score_chart()` | Horizontal bars, color-coded: green ≥75%, amber ≥50%, red <50% |
| Skill Distribution Chart | `skill_distribution_chart()` | Grouped bars: Matched (green) vs Missing (red) skills per candidate |
| Soft Skills Chart | `soft_skills_chart()` | Bar chart of detected soft skills count per candidate |

---

## 9. Frontend UI Architecture

### `upload.html` — The Config Dashboard
The most complex UI component. Key elements:

- **5 HTML5 Range Sliders:** `weight_tech`, `weight_yoe`, `weight_context`, `weight_soft`, `weight_bonus`.
- **`normalizeSliders()` JS engine:** The first 4 sliders share a strictly bound `100%` pool. When any slider moves, the JS redistributes the remaining budget proportionally among the others — the total NEVER breaches `100%`.
- **Bonus Slider Isolation:** `weight_bonus` is explicitly isolated from the 100% pool — it's an additive offset variable, not part of the normalization math.
- **Quick Presets:** A JS dictionary maps 4 preset keys (`default`, `strict`, `balanced`, `soft`) to slider values. Pressing a preset button updates all sliders and triggers `updateBadges()`.

### `analyze.html` — The Loading Page
An intermediate page shown after upload. It:
1. Immediately POSTs to `/start-analysis` (JSON) to spawn the background thread and get a `job_id`.
2. Starts `setInterval()` every **2 seconds**, polling `/analysis-status/<job_id>`.
3. Updates a progress bar from the `message` field in the response.
4. On `status === 'done'`, redirects to `/results`.

### `results.html` — The Output Dashboard
Fully server-rendered via Jinja2 with `explanations`, `score_chart`, `skill_chart`, `soft_chart`, and `jd_skills` passed directly from `routes.py`. No client-side data fetching needed.

---

## 10. Backend Flask Routing & Async Architecture

Found in `web_app/routes.py`.

### The Problem
TF-IDF Cosine computation on 10+ PDFs can take several seconds. A synchronous HTTP POST would block the Flask worker thread and eventually time out the browser connection.

### The Solution — Detached Background Thread + Long-Polling

**Flow:**
```
POST /upload → validate files → store data in _data_store (in-memory) → redirect to /analyze
GET  /analyze → render analyze.html (progress page)
POST /start-analysis → spawn daemon Thread(_run_analysis) → return {job_id}
GET  /analysis-status/<job_id> → return {status, message} from _job_store
GET  /results → render results from _job_store[job_id]['results']
```

**Key Design Decisions:**
- **`_data_store` (dict):** Stores uploaded file text and weights server-side by a UUID key, avoiding cookie size limits (cookies only store the UUID key).
- **`_job_store` (dict):** Stores background job state (`queued → loading_models → processing_jd → processing_resumes → computing_scores → generating_explanations → creating_charts → done`).
- **Lazy Singletons:** Heavy modules (`NLPProcessor`, `MatchingEngine`, `Visualizer`, `Explainer`) are initialized only on first use (`_get_nlp_processor()`, etc.) to keep app startup fast.
- **`daemon=True` Thread:** The background thread is a daemon so it won't block Flask shutdown.

---

## 11. Authentication System

Found in `web_app/auth.py`.

Supports two login methods:

| Method | How |
|---|---|
| **Email/Password** | Passwords hashed with `werkzeug.security.generate_password_hash` (PBKDF2). Stored in SQLite `User` table. |
| **Google OAuth SSO** | `Authlib` OAuth client registers with `accounts.google.com/.well-known/openid-configuration`. Retrieves `email`, `name`, `picture` from Google's userinfo. Creates or updates user record on first SSO login. |

Google SSO is **optional** — if `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are not set in `.env`, the "Continue with Google" button is hidden and only email/password login is available.

**User model fields:** `id`, `email`, `name`, `password_hash`, `avatar_url`, `sso_provider`

---

## 12. Environment Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"
SECRET_KEY="your-flask-secret-key"
```

Get Google credentials from: https://console.cloud.google.com/apis/credentials

---

## 13. How to Run

```bash
# Activate the conda environment where all dependencies are installed
conda activate ai

# Start the Flask development server
python app.py
```

Visit **http://127.0.0.1:5001** in your browser.

**Required system dependency for OCR:** Tesseract must be installed and on PATH.
```bash
brew install tesseract   # macOS
```

---

## 14. Instructions for Future AI Assistants / Developers

If you are an AI or developer reading this file to assist with this codebase, you **MUST** adhere to these architectural laws:

1.  **Do NOT break the Regex Skill Matcher.** `processor.py` uses strict `\b` word-boundary regex against `skills_db.py`. Never replace this with an AI summarizer or fuzzy matcher — the strict boundaries guarantee precision.

2.  **Do NOT alter `upload.html` sliders without mapping `routes.py`.** If you add a new weight slider, you must: isolate its DOM ID, update `normalizeSliders()`, update the Quick Presets dictionary, extract it via `request.form.get()` in `routes.py`, and pass it into `matcher.py`'s weights dict.

3.  **Do NOT add heavy ML dependencies.** This project deliberately uses `scikit-learn` TF-IDF + Cosine Similarity instead of HuggingFace `sentence-transformers`. Do NOT install PyTorch, TensorFlow, or Transformers unless the user explicitly requests a migration to dense neural embeddings.

4.  **Do NOT block the main Flask thread.** All AI processing MUST occur inside `_run_analysis()` in `routes.py` as a daemon thread, updating `_job_store[job_id]` incrementally. Synchronous analysis will lock the Flask worker.

5.  **Do NOT use `ngram_range=(1,3)` in the primary matching vectorizer.** The `sentence_embeddings()` method uses tri-grams, but `tfidf_vectors()` (used in actual matching) uses bi-grams `(1,2)` for speed. Mixing these will produce incorrect cosine similarity results.

6.  **Do NOT hard-code weights.** The `weights` dict is always passed dynamically from the user's slider configuration. Default values exist only as a fallback when `weights=None`.
