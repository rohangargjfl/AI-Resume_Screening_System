# AI Resume Screening and Candidate Ranking System

> **AI in Recruitment Process: Resume Analysis using NLP**

A production-style prototype that uses NLP and Sentence Transformers to automatically screen resumes, match candidates against job descriptions, and rank them with full explainability.

---

## 🚀 Run on Google Colab (No Setup Required!)

> **Mam / Evaluator:** Sirf neeche diye link pe click karein aur `Runtime → Run All` press karein. Koi installation nahi, sirf Google account chahiye!

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rohangargjfl/AI-Resume_Screening_System/blob/main/Run_On_Google_Colab.ipynb)

**Direct Link:**
```
https://colab.research.google.com/github/rohangargjfl/AI-Resume_Screening_System/blob/main/Run_On_Google_Colab.ipynb
```

### Steps to Run:
1. Click the link above → Opens directly in Google Colab
2. Go to **Runtime → Run All**
3. Wait ~5 minutes for setup (first time only)
4. Click the **public URL** that appears at the end of the last cell
5. Register with any email/password → Start screening resumes!

---

## Features

| Module | Description |
|---|---|
| **Resume Parser** | Extracts text from PDF, DOCX, TXT and preprocesses it |
| **NLP Processing** | Tokenization, lemmatization, NER, strict regex skill extraction via SpaCy |
| **Feature Extraction** | Statistical pseudo-semantic TF-IDF N-Grams (1,3) (scikit-learn) |
| **Matching Engine** | Cosine similarity → dynamic recruiter-weighted multi-variable scoring |
| **Explainable AI** | Mathematical score breakdown & reasoning text generation |
| **Visualization** | Interactive Chart.js & dynamic UI score badges |
| **Web Application** | Flask asynchronous dashboard with interactive uploading and SSO Auth |

---

## Tech Stack

Python · Flask · SpaCy · scikit-learn · Vanilla JS · Bootstrap 5 · Chart.js

---

## Project Structure

```
AI_Resume_Screening_System/
├── resume_parser/          # PDF/DOCX/TXT extraction & preprocessing
├── nlp_processing/         # SpaCy NLP pipeline & skill extraction
├── feature_extraction/     # TF-IDF + Sentence Transformer embeddings
├── matching_engine/        # Cosine similarity scoring
├── explainable_ai/         # Skill-level explanations
├── visualization/          # Matplotlib chart generation
├── web_app/                # Flask routes, templates, static assets
│   ├── templates/
│   └── static/
├── example_resumes/        # Sample resumes & job description for testing
├── requirements.txt
├── app.py                  # Application entry point
└── README.md
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Visit **http://127.0.0.1:5000**

---

## Usage

1. **Home Page** — Overview of the system and how it works.
2. **Upload** — Paste or upload a job description, then upload one or more candidate resumes.
3. **Analyse** — Confirm and run the AI analysis pipeline.
4. **Results Dashboard** — View ranked candidates with:
   - Match scores
   - Matched / missing skill breakdowns
   - Detected soft skills
   - Comparison charts

---

## Example Data

The `example_resumes/` directory contains:
- `job_description.txt` — Sample Senior Python Developer JD
- 5 candidate resumes with varying skill profiles

---

## How Scoring Works

The absolute final match score is a dynamic, recruiter-controlled blend of four core similarity measures:

| Component | Default Weight | Description |
|---|---|---|
| Tech Skills | 60% | Strict Regex Exact-Match Intersection against SpaCy NER |
| Contextual Match | 15% | Semantic N-Gram (1,3) + TF-IDF Cosine Trajectory |
| Years of Experience | 15% | Linear Threshold Ratio |
| Soft Skills | 10% | Strict Regex Exact-Match Intersection |

*Plus an autonomous mathematically bounded **Extra Skills bonus** (Default cap: +5%) for tech skills discovered but not mathematically requested in the JD.*

**All weights, metrics, and bonus caps are actively customizable by the recruiter via UI Range Sliders on the Upload Dashboard before firing the background Analysis thread!**

---

## Author

B.Tech Final Year Project — AI in Recruitment Process
