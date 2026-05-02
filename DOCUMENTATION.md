# AI Resume Screening System - Technical Documentation

This document provides a comprehensive breakdown of the core technologies, algorithms, and architectural decisions used to build the AI Resume Screening System.

## 1. Core Technology Stack
The application is built on a robust, lightweight Python backend designed for horizontal scalability and rapid text processing.

*   **Backend Framework:** `Flask`
    *   **Why:** Flask was chosen because it is incredibly lightweight, allows for rapid prototyping of REST APIs, and does not enforce a rigid directory structure (unlike Django), making it perfect for custom AI micro-architecture.
*   **Frontend UI:** `HTML5`, `Vanilla CSS`, `Bootstrap 5`, `Jinja2`
    *   **Why:** Bootstrap 5 allows for rapid, responsive UI development without writing thousands of lines of custom CSS. Jinja2 templates allow the Python backend to dynamically inject the complex AI explainability variables directly into the HTML before sending it to the browser.
*   **Database & Authentication:** `SQLite`, `Flask-SQLAlchemy`, `Authlib`
    *   **Why:** SQLite is self-contained and requires no external server setup, perfect for local storage of user profiles. `Authlib` was utilized to securely build the automated Google OAuth 2.0 Single Sign-On (SSO) integration.

---

## 2. Text Parsing Library Stack
Extracting clean data from unpredictable file formats is the most critical first step before any AI analysis can begin.

*   `PyPDF2` & `python-docx`: Used in `resume_parser/parser.py`.
    *   **Why:** These libraries traverse the raw binary of uploaded `.pdf` and `.docx` files page-by-page. They strip away images and formatting chunks to dump pure UTF-8 strings.
*   **Preprocessing:** `re` (Python Regex Module)
    *   **Why:** Before the semantic AI sees the text, the parser uses regex to normalize spacing and lowercase all text. However, we intentionally **avoid** blanket punctuation stripping to ensure nuanced phrases like `C++`, `Node.js`, and `1-3 Yrs` are preserved exactly as written.

---

## 3. Natural Language Processing (NLP) Engine
The Brain of the operation. Found in `nlp_processing/processor.py`.

*   **Core Library:** `SpaCy` (`en_core_web_sm` model)
    *   **Why:** SpaCy is an industry-standard, execution-optimized NLP library. The `sm` (small) web model is used to keep RAM footprint low while still providing excellent tokenization and Named Entity Recognition (NER).
*   **Stopword Removal & Lemmatization:**
    *   **What it does:** It removes grammatically required but semantically useless words (e.g., "the", "and", "is") and reduces verbs to their root form (e.g., "managing" -> "manage"). 
    *   **Why:** This dramatically reduces the mathematical noise when the TF-IDF vectorizer attempts to calculate keyword alignment.
*   **Experience Extraction (Regex + Date Math Fallback):**
    *   **What it does:** Scans the document for explicit declarations (e.g., "5+ years") using `re`. If no explicit number is found, a Date-Math fallback parser triggers. It hunts for chronological date strings (e.g., "June 2024 - August 2025"), converts them into active `datetime` objects, calculates the month spread, and mathematically converts it into integer Years of Experience (YoE).

---

## 4. The Matching & Scoring Algorithms
Found in `matching_engine/matcher.py` and `feature_extraction/extractor.py`.

The AI does *not* utilize heavy Large Language Models (LLMs) like GPT or BERT for matching. Instead, it uses blazing-fast statistical machine learning matrix math via `scikit-learn`.

### Algorithmic Breakdown: TF-IDF N-Grams + Cosine Similarity
*   **TF-IDF + N-Grams (1, 3):**
    *   **What it does:** Instead of shattering a sentence into single meaningless words, the engine binds up to 3 words together concurrently (e.g., "Natural Language Processing"). It then evaluates how *important* that clustered phrase is compared to normal English stop-words.
    *   **Why:** By linking words into Tri-Grams, it simulates pseudo-semantic understanding without needing a heavy Neural Network layer. Furthermore, it completely solves the "Keyword Stuffing" problem. If a candidate pastes the word "Java" 50 times in white text at the bottom of their resume, TF-IDF mathematically penalizes the abnormal term frequency curve.
*   **Cosine Similarity:**
    *   **What it does:** Once TF-IDF turns the Job Description and the Resume into geometric vectors in a multi-dimensional space, Cosine Similarity calculates the geometric angle between the two arrows.
    *   **Why:** Unlike Euclidean distance (measuring the raw distance between two points), Cosine Similarity measures the *directional trajectory* of the words. A 5-page resume and a 1-page resume might have wildly different lengths (Euclidean distance), but if they discuss the exact same topics, their semantic arrows point in the exact same direction (giving a Cosine similarity matrix approaching `1.0` or `100%`).

### The Final Weighted Ranking Formula
After the system statistically analyzes the text, it aggregates the extracted points and feeds them into a dynamic, recruiter-controlled mathematical matrix:

**`Final Match Score = (Tech Score * W1) + (YoE Score * W2) + (Context Score * W3) + (Soft Skill Score * W4) + Unrequested Extra Tech Bonus Cap`**

*(Note: W1, W2, W3, W4, and the Extra Bonus Cap are completely configurable in real-time by the recruiter using dynamic UI sliders on the Upload Dashboard. Default configurations map to 60/15/15/10/5).*

Here is exactly how each component is mathematically derived before the custom UI weighting multiplier is applied:

1.  **Technical Skills (`tech_score`):**
    *   **Algorithm:** Normalized Set Intersection (Jaccard-like Overlap)
    *   **Math:** `(Count of Extracted JD Tech Skills found in Resume) / (Total Count of JD Tech Skills) * 100`
    *   *Result:* Measures explicit technical proficiency based strictly on the required stack.
2.  **Context Match (`context_score`):**
    *   **Algorithm:** TF-IDF Cosine Vector Trajectory
    *   **Math:** Angles between vectorized strings converted into a bounded 0-100 float scale.
    *   *Result:* Ensures the candidate's general experience "vibes" spatially with the Job Description text, acting as a plagiarism and keyword-stuffing defense.
3.  **Years of Experience (`yoe_score`):**
    *   **Algorithm:** Linear Ratio Penalty Thresholds
    *   **Math:**
        *   If `Resume YoE >= JD YoE`: Score is statically locked at `100.0` (No arbitrary inflation for being wildly overqualified).
        *   If `Resume YoE < JD YoE`: Score is heavily penalized proportionally: `(Resume YoE / JD YoE) * 100`
    *   *Result:* A 1-Year intern applying for a 3-Year role will mathematically retain `33.3%` of the Experience band rather than instantly failing the gate.
4.  **Soft Skills (`soft_skill_score`):**
    *   **Algorithm:** Normalized Set Intersection
    *   **Math:** `(Count of Match Soft Skills) / (Total Soft Skills Required) * 100`

This strictly bounded system ensures that top candidates are mathematically pushed to the top based squarely on objective tech requirements, rather than subjective or hallucinated criteria.

---

## 5. Explainable AI (XAI)
Found in `explainable_ai/explainer.py`.

*   **Why:** Black-box AI that arbitrary spits out a number like "86%" is dangerous and often rejected by legal compliance and HR teams. 
*   **How it works:** The XAI engine intercepts the raw mathematical array outputs from the Matching Engine and translates them into plain-English feedback strings. For example, instead of outputting a YoE float penalty of `0.334`, the Explainer dynamically generates the tooltip: *"Falls slightly short of the required 3 years."* This ensures recruiters understand perfectly why the AI made a specific algorithmic ranking decision.

---

## 6. Frontend UI Architecture & Javascript Normalization
The UI is built with Bootstrap 5 and carefully injected Vanilla JS without needing React/Vue overhead.

### `upload.html` (The Config Dashboard)
*   **The AI Scoring Configuration Card:** This is the most complex UI component. It houses 5 HTML5 Range Sliders (`weight_tech`, `weight_yoe`, `weight_context`, `weight_soft`, `weight_bonus`).
*   **Javascript Normalization Engine (`normalizeSliders`):** The first 4 sliders share a strictly bound `100%` pool. If a user drags the Tech slider up, the Javascript natively captures the `input` event and forces the nearest neighboring slider mathematically down so the total NEVER breaches 100%.
*   **Bonus Slider Isolation:** The 5th slider (`Extra Skills Bonus Cap`) is explicitly isolated from the `100%` math pool, acting as an additive offset variable.
*   **Quick Presets:** The JS contains a static dictionary mapping 4 preset keys (`default`, `strict`, `balanced`, `soft`) to their integer values. Pressing a preset button loops through the inputs and forces their values instantly, triggering an `updateBadges()` refresh.

### `results.html` (The Output Dashboard)
*   **Dynamic Jinja2 Injection:** The UI is purely stateless. `routes.py` passes the completed `results` dictionary directly into the render string. 
*   **Visualization Engine:** We avoided heavy python charting libraries. Instead, we use `Chart.js` directly in the browser. The Python backend ships the arrays (e.g. `[85, 92, 40]`) into the HTML `<canvas>` dataset, which Javascript natively renders upon load.

---

## 7. Backend Flask Routing & Async Threading
Found in `web_app/routes.py`.

*   **The Problem:** TF-IDF Cosine algorithms take severe processing time (up to ~5 seconds per 10 PDFs). If we ran this sequentially, the browser's HTTP POST request would eventually time out and crash.
*   **The Solution (`/start-analysis`):** When the user hits "Upload", `routes.py` intercepts the payload, extracts the Dynamic Weights variables (`w_tech`, `w_bonus`, etc.), and spawns a **detached asynchronous Python `<Thread>`**.
*   **State Management:** The async thread stores its progress (e.g., `'status': 'extracting_text'`) inside a globally instantiated dictionary `_job_store`. 
*   **Long-Polling:** The frontend immediately boots `loading.html`, which runs `setInterval()` every 2 seconds pinging the `/analysis-status/<job_id>` API endpoint to update the progress bar. Once the JSON returns `'status': 'done'`, the browser executes `window.location.href = '/results'`.

---

## 8. Instructions for Future LLMs / AI Assistants
If you are an AI reading this file as context to assist the developer in upgrading this codebase, you MUST adhere to the following architectural laws:

1.  **Do NOT break the Regex Keyword Matcher:** The NLP engine uses SpaCy for NER, but `processor.py` explicitly uses strict Regex Word Boundaries (`\b`) mapped against `skills_db.py` to extract tech skills. NEVER switch this to an AI summarizer—the strict boundaries guarantee 100% accuracy.
2.  **Do NOT alter `upload.html` Javascript variables without mapping `routes.py`:** If you add a new AI weight slider to the frontend, you MUST isolate its DOM ID, update the `normalizeSliders()` pool, update the `Quick Presets` dictionary, extract it via `request.form.get()` in `routes.py`, and pass it precisely into the algorithm kwargs inside `matcher.py`.
3.  **Do NOT add heavy dependencies:** This project is deliberately engineered to use `scikit-learn` TF-IDF N-Grams to simulate Semantic Context Trajectory instead of using HuggingFace `sentence-transformers`. Do NOT attempt to install PyTorch, TensorFlow, or heavy Transformers unless the user explicitly requests a permanent migration to Dense Neural Vector embeddings.
4.  **Do NOT block the main thread:** All AI mathematical processing MUST occur inside `_run_analysis()` in `routes.py` and must update `_job_store[job_id]` incrementally. Modifying the Matrix Engine synchronously will lock the Flask worker.
