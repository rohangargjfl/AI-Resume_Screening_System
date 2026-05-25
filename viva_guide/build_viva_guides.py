from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "viva_guide"
FIG = ROOT / "latex_report" / "figures"


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0B1F3A"),
            spaceAfter=14,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#394B63"),
            spaceAfter=8,
        ),
        "H1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#0B3D91"),
            spaceBefore=12,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "H2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.4,
            leading=16,
            textColor=colors.HexColor("#1D5F75"),
            spaceBefore=8,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=13.2,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "Small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.2,
            spaceAfter=3,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=12.5,
            leftIndent=12,
            firstLineIndent=0,
            spaceAfter=3,
        ),
        "Code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.8,
            leading=9.6,
            leftIndent=4,
            rightIndent=4,
            backColor=colors.HexColor("#F4F7FB"),
            borderColor=colors.HexColor("#D6E0EA"),
            borderWidth=0.5,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=6,
        ),
        "Callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.5,
            textColor=colors.HexColor("#17324D"),
            backColor=colors.HexColor("#EEF6FF"),
            borderColor=colors.HexColor("#B7D7F0"),
            borderWidth=0.8,
            borderPadding=7,
            spaceBefore=4,
            spaceAfter=7,
        ),
        "Caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=10.5,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#546A7B"),
            spaceAfter=7,
        ),
    }
    return styles


def p(text, styles, style="Body"):
    return Paragraph(text, styles[style])


def bullets(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["Bullet"])) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=16,
        bulletFontSize=6,
        spaceAfter=6,
    )


def numbered(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["Bullet"])) for item in items],
        bulletType="1",
        leftIndent=18,
        spaceAfter=6,
    )


def code(text, styles):
    return Paragraph("<br/>".join(html_escape(line) for line in text.strip().splitlines()), styles["Code"])


def table(data, styles, widths=None, font_size=7.6):
    converted = []
    for row in data:
        converted.append([Paragraph(str(cell), styles["Small"]) for cell in row])
    t = Table(converted, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEBFA")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0B1F3A")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C7D6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def add_image(story, path, caption, styles, width=6.1 * inch):
    if path.exists():
        img = Image(str(path), width=width, height=width * 0.62)
        img.hAlign = "CENTER"
        story.extend([img, p(caption, styles, "Caption")])


def add_square_image(story, path, caption, styles, width=1.55 * inch):
    if path.exists():
        img = Image(str(path), width=width, height=width)
        img.hAlign = "CENTER"
        story.extend([img, p(caption, styles, "Caption")])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(0.62 * inch, 0.45 * inch, "AI Resume Screening System Viva Guide")
    canvas.drawRightString(A4[0] - 0.62 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_doc(filename):
    doc = BaseDocTemplate(
        str(filename),
        pagesize=A4,
        leftMargin=0.62 * inch,
        rightMargin=0.62 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.65 * inch,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=footer)])
    return doc


def common_tables(styles):
    tech_stack = table(
        [
            ["Layer", "Technology", "Why it is used"],
            ["Backend", "Python, Flask", "Lightweight REST-style web backend; easy to split parsing, NLP, matching, XAI and dashboard modules."],
            ["Frontend", "HTML5, Bootstrap 5, Jinja2", "Responsive pages with server-rendered score breakdowns and explanation panels."],
            ["Database/Auth", "SQLite, SQLAlchemy, Flask-Login, Authlib", "Simple local persistence, login protection, optional Google OAuth SSO."],
            ["Parsing", "PyPDF2, python-docx, Pillow, pdf2image, Tesseract", "Extracts text from digital files and OCRs scanned/image resumes."],
            ["NLP", "SpaCy + Regex", "Tokenization, entities, strict skill extraction, and YoE extraction."],
            ["Matching", "scikit-learn TF-IDF + Cosine Similarity", "Fast statistical context matching without heavy transformer models."],
            ["XAI/Charts", "Custom Explainer, Matplotlib, Chart.js", "Human-readable explanations and visual score dashboards."],
        ],
        styles,
        widths=[1.25 * inch, 1.75 * inch, 3.25 * inch],
    )
    bench = table(
        [
            ["Benchmark", "What was tested", "Key result / viva point"],
            ["1. Format Bias & OCR", "TXT vs PDF vs PNG extraction and scoring.", "PNG through OCR scored 90.5%, same as TXT. PDF scored 90.0% due to spacing loss."],
            ["2. Keyword Stuffing", "Baseline, verbose/diluted resume, and keyword stuffer.", "Regex kept hard-skill score stable; TF-IDF penalized dilution and contained stuffing."],
            ["3. XAI & Boundaries", "Over-qualified YoE and extra skills bonus.", "YoE capped at 100%; extra bonus +2.0% under 5.0% cap; explanation remained auditable."],
            ["4. A vs B vs C", "Current Regex+TF-IDF vs Sentence-BERT vs future hybrid.", "LLM understood semantics better; current model stayed strict and explainable."],
            ["5. Efficiency", "100-resume stress test.", "Approach A: 0.0062 sec, 0.12 MB; much faster/lighter than LLM alternatives."],
        ],
        styles,
        widths=[1.25 * inch, 2.25 * inch, 2.75 * inch],
    )
    return tech_stack, bench


def english_story(styles):
    story = []
    story += [
        p("AI-Powered Resume Screening System", styles, "Title"),
        p("Complete Final Viva Preparation Guide", styles, "Subtitle"),
        p("Project: AI in Recruitment Process: A Study on the Use of AI for Resume Analysis", styles, "Subtitle"),
        p("Team: Rohan Garg, Punit Sukhani, Saksham | Guide: Mrs. Gull Kaur", styles, "Subtitle"),
    ]
    add_square_image(story, FIG / "dtu_logo.png", "Delhi Technological University", styles)
    story.append(PageBreak())

    story += [
        p("1. One-Minute Project Summary", styles, "H1"),
        p("<b>What the project does:</b> The system takes one job description and multiple resumes, extracts readable text from every file, detects skills and years of experience, computes a weighted match score, explains the score in recruiter-friendly language, and displays ranked candidates with charts and score breakdowns.", styles),
        p("<b>Core idea:</b> The project is a lightweight, explainable first-pass resume screening prototype. It deliberately uses Regex + TF-IDF + custom mathematical rules instead of heavy LLMs so that it remains fast, low-cost, transparent, and suitable for SME-style recruitment workflows.", styles, "Callout"),
        p("<b>How to say this in viva:</b> Our system is not designed to replace HR. It is a decision-support tool that reduces the first screening workload while keeping the final judgement with the recruiter.", styles),
        p("2. Problem Statement and Motivation", styles, "H1"),
        p("Modern job postings receive a large number of resumes. Manual screening is slow, inconsistent, and prone to bias. Traditional Applicant Tracking Systems rely heavily on exact keywords, which can miss good candidates who use different wording. On the other side, LLM-based systems understand semantics better but are expensive, slower, and less explainable. This project solves the middle problem: fast and explainable screening with enough intelligence for first-pass filtering.", styles),
        bullets([
            "<b>Manual screening issue:</b> high time cost, fatigue, inconsistent judgement.",
            "<b>Keyword ATS issue:</b> fails on synonyms such as REST vs RESTful and can be tricked by stuffing.",
            "<b>LLM issue:</b> higher latency, memory/cost, and weaker auditability.",
            "<b>Our position:</b> use lightweight AI as a first-pass filter, not a final hiring authority.",
        ], styles),
        p("3. Inputs, Outputs and User Flow", styles, "H1"),
        p("<b>Inputs:</b> recruiter login, job description text, one or more resumes in PDF, DOCX, TXT, PNG, JPG/JPEG format, and scoring weights configured through the upload dashboard.", styles),
        p("<b>Outputs:</b> ranked candidate list, final match scores, matched and missing skills, detected soft skills, years-of-experience status, extra skills bonus, charts, and plain-English XAI explanation.", styles),
    ]
    add_image(story, FIG / "project_flowchart.png", "Figure: End-to-end architecture from frontend upload to parsing, NLP, matching, XAI, visualization, and final dashboard.", styles, 5.8 * inch)
    story += [
        p("Step-wise flow from input to output", styles, "H2"),
        numbered([
            "Recruiter logs in and opens the upload page.",
            "Recruiter pastes the job description and uploads resumes.",
            "Recruiter adjusts scoring weights: technical skills, experience, context match, soft skills, and bonus cap.",
            "Backend validates files and stores uploaded data in server-side memory using a UUID key.",
            "Analyze page starts a background analysis job and polls status every two seconds.",
            "Parser extracts text digitally or routes scanned/image files to OCR.",
            "NLP module extracts technical skills, soft skills, and years of experience.",
            "Matching engine computes component scores and final weighted score.",
            "Explainer converts the score dictionary into audit-ready text.",
            "Dashboard displays ranked candidates, charts, skill tags, and explanation panels.",
        ], styles),
        p("4. System Components and Responsibilities", styles, "H1"),
    ]
    tech_stack, bench = common_tables(styles)
    story += [tech_stack, Spacer(1, 8)]
    story += [
        p("Major source-code modules", styles, "H2"),
        bullets([
            "<b>app.py:</b> Creates the Flask application and registers blueprints.",
            "<b>models.py:</b> SQLAlchemy user model with email, name, password hash, SSO provider and avatar URL.",
            "<b>resume_parser/parser.py:</b> Handles PDF, DOCX, TXT, PNG, JPG/JPEG extraction and OCR fallback.",
            "<b>nlp_processing/processor.py:</b> Runs SpaCy, skill extraction, soft-skill extraction and YoE detection.",
            "<b>nlp_processing/skills_db.py:</b> Curated technical and soft-skill lists.",
            "<b>feature_extraction/extractor.py:</b> TF-IDF vectorization utilities.",
            "<b>matching_engine/matcher.py:</b> Weighted score computation and component contributions.",
            "<b>explainable_ai/explainer.py:</b> Converts score dictionaries into plain-English explanations.",
            "<b>visualization/charts.py:</b> Produces base64 Matplotlib charts embedded in HTML.",
            "<b>web_app/routes.py:</b> Upload, analyze, polling and results routes.",
            "<b>web_app/auth.py:</b> Email/password login and optional Google OAuth SSO.",
        ], styles),
        p("5. Parsing and OCR Pipeline", styles, "H1"),
        p("Every file must become plain text before any AI step can run. The parser first attempts the cheapest reliable digital extraction. If text extraction fails or returns fewer than 50 characters, the document is treated as scanned or parser-resistant and routed to OCR. This design reduces format bias because a scanned or image-based resume still gets processed instead of being rejected.", styles),
        table([
            ["Format", "Primary method", "Fallback / notes"],
            [".txt", "Direct UTF-8 read", "Uses errors='ignore' to avoid decode crashes."],
            [".docx", "python-docx paragraphs", "Reads document XML text."],
            [".pdf", "PyPDF2 page extraction", "If text length < 50, convert to image and OCR."],
            [".png/.jpg", "Pillow + OCR", "Direct OCR path with preprocessing."],
        ], styles, widths=[1.1 * inch, 2.0 * inch, 3.15 * inch]),
        p("OCR preprocessing: RGBA flattening, grayscale conversion, contrast boost, sharpening, adaptive binarization, and Tesseract CLI extraction. The project uses direct Tesseract subprocess instead of pytesseract to avoid wrapper-level decode issues.", styles),
        p("Algorithm: OCR-aware parsing", styles, "H2"),
        code("""
FUNCTION ParseDocument(file, extension):
    IF extension == ".txt": return read_text(file)
    IF extension == ".docx": return read_docx(file)
    IF extension == ".pdf":
        text = PyPDF2_extract(file)
        IF length(text) < 50:
            image_pages = convert_pdf_to_300dpi_images(file)
            return OCR_Pipeline(image_pages)
        return text
    IF extension in [".png", ".jpg", ".jpeg"]:
        return OCR_Pipeline(file)

FUNCTION OCR_Pipeline(image):
    flatten_transparency_to_white()
    grayscale()
    boost_contrast_and_sharpen()
    binarize_pixels(threshold=140)
    return tesseract_cli_extract_text()
        """, styles),
        p("6. NLP Processing and Regex Skill Extraction", styles, "H1"),
        p("The NLP layer uses SpaCy's en_core_web_sm model for tokenization, lemmatization and named entities. However, technical and soft skills are not trusted to generic NER. They are extracted using strict regex word-boundary matching against curated skill lists. This is deliberate: it prevents false matches such as the skill C appearing inside the word communication.", styles),
        code(r"""
pattern = r'\b' + re.escape(skill) + r'\b'
        """, styles),
        p("YoE extraction follows a three-tier cascade: direct phrases such as '5+ years of experience', reversed phrases such as 'Experience: 5 years', and date math from ranges such as 'June 2024 - August 2025'. Values above 40 years are ignored, and long education-like date spans are filtered to avoid counting B.Tech duration as professional experience.", styles),
        p("7. TF-IDF Context Matching", styles, "H1"),
        p("The system uses scikit-learn's TfidfVectorizer with max_features=5000, English stop-word removal and ngram_range=(1,2). Bigrams allow phrases such as machine learning or natural language to be represented better than plain unigrams. TF-IDF gives higher weight to distinctive terms and lower weight to common words.", styles),
        p("<b>Cosine similarity:</b> Context Score = (Resume Vector dot JD Vector) / (||Resume Vector|| × ||JD Vector||). Cosine similarity is used because resumes may differ in length. It measures direction/topic alignment rather than raw length.", styles),
        p("8. Matching and Scoring Formula", styles, "H1"),
        p("The final score combines hard requirements, soft evidence and contextual similarity. The first four weights always sum to 1.0, while the bonus is a capped additive offset.", styles),
        table([
            ["Component", "How it is computed", "Why it matters"],
            ["Tech Score", "Matched required tech skills / required tech skills", "Hard technical fit."],
            ["Soft Score", "Matched requested soft skills / requested soft skills", "Communication, teamwork, leadership evidence."],
            ["YoE Score", "min(resume_yoe / jd_yoe, 1.0)", "Caps over-qualified candidates at 100%."],
            ["Context Score", "TF-IDF cosine similarity", "Broader textual alignment between JD and resume."],
            ["Bonus", "min(extra_tech × bonus_step, bonus_cap)", "Rewards adjacent skills without hiding missing requirements."],
        ], styles, widths=[1.2 * inch, 2.25 * inch, 2.8 * inch]),
        code("""
Final Score =
    (Tech Score × W_tech)
  + (Soft Score × W_soft)
  + (YoE Score × W_yoe)
  + (Context Score × W_context)
  + Extra Skills Bonus

Default weights:
Tech = 60%, YoE = 15%, Context = 15%, Soft = 10%, Bonus cap = 5%
        """, styles),
        p("9. Explainable AI Layer", styles, "H1"),
        p("The XAI layer is deterministic. It does not approximate a black-box model; it reads the exact score dictionary produced by the matcher and converts it into a recruiter-readable explanation. It reports final score, match band, experience status, matched required skills, missing skills, bonus skills, soft skills and score component contributions.", styles),
    ]
    add_image(story, FIG / "ai_score_breakdown.png", "Figure: XAI score breakdown showing component contributions, matched/missing skills and bonus skills.", styles, 6.3 * inch)
    story += [
        p("Candidate buckets: Strong match >= 75%, Moderate match >= 50%, Partial match >= 30%, Weak match < 30%.", styles, "Callout"),
        p("10. Frontend and Async Backend", styles, "H1"),
    ]
    add_image(story, FIG / "ai_scoring_configuration.png", "Figure: AI scoring configuration with recruiter-controlled weights and separate bonus cap.", styles, 6.2 * inch)
    story += [
        p("The upload page contains five sliders: weight_tech, weight_yoe, weight_context, weight_soft and weight_bonus. The first four share a strict 100% pool. The JavaScript normalizeSliders() engine redistributes weights so the core total never exceeds 100%. The bonus slider is isolated because it is an additive cap, not part of the normalized core score.", styles),
        p("The backend avoids blocking the main Flask request. Uploaded data is stored in _data_store using a UUID key. The analyze page calls /start-analysis, which creates a daemon background thread. The frontend polls /analysis-status/<job_id> every two seconds and redirects to /results when complete.", styles),
        code("""
POST /upload              -> validate files, store data, redirect to /analyze
GET  /analyze             -> progress page
POST /start-analysis      -> spawn Thread(_run_analysis), return job_id
GET  /analysis-status/id  -> return queued/loading/processing/done
GET  /results             -> render ranked candidates and charts
        """, styles),
        p("11. Benchmarks and What to Say in Viva", styles, "H1"),
        bench,
        p("Approach A vs B vs C", styles, "H2"),
        bullets([
            "<b>Approach A: Current app (Regex + TF-IDF).</b> Fast, lightweight, deterministic, explainable. Weakness: cannot understand all synonyms.",
            "<b>Approach C: Pure LLM/Sentence-BERT.</b> Better semantic understanding. Weakness: no strict hard boundaries, more latency and memory.",
            "<b>Approach B: Future hybrid.</b> Keep regex hard-skill shield and replace context score with LLM embeddings. Better semantics but slower than Approach A.",
        ], styles),
        p("12. Strengths, Limitations and Future Work", styles, "H1"),
        table([
            ["Strengths", "Limitations", "Future Work"],
            ["Fast CPU-friendly scoring; OCR fallback; explainable output; adjustable weights; keyword stuffing resistance.", "Regex misses synonyms; TF-IDF lacks deep language meaning; skill ontology must be updated; OCR depends on scan quality; small controlled benchmark dataset.", "Sentence-BERT hybrid context module; dynamic skill knowledge graph; fairness/bias audit; recruiter feedback loop; production database; larger real resume dataset."],
        ], styles, widths=[2.1 * inch, 2.1 * inch, 2.05 * inch]),
        p("13. Demo Script for Final Viva", styles, "H1"),
        numbered([
            "Open the app and login/register.",
            "Go to the upload screen and paste the job description.",
            "Upload multiple resumes, ideally one TXT/PDF and one image/scanned sample.",
            "Show the weight sliders and explain default weights: Tech 60, YoE 15, Context 15, Soft 10, Bonus cap 5.",
            "Click submit and show the analyze/progress page.",
            "Open results and explain ranking order, score breakdown, matched/missing skills and XAI text.",
            "Mention why Approach A was chosen: fast, cheap, transparent first-pass screening.",
            "End honestly: semantic models are better for synonyms, so future work is a hybrid model.",
        ], styles),
        p("14. High-Probability Viva Questions", styles, "H1"),
        table([
            ["Question", "Best answer"],
            ["Why not use only LLM?", "LLMs are semantically stronger but slower, costlier and less transparent. Our goal is first-pass filtering under hardware constraints."],
            ["Why regex for skills?", "Strict word boundaries prevent false positives and make hard-skill extraction auditable."],
            ["Why TF-IDF?", "It is fast, interpretable, CPU-friendly and good enough for lexical context matching."],
            ["Why cosine similarity?", "It compares vector direction/topic alignment, not raw resume length."],
            ["What is XAI here?", "A deterministic explanation layer that converts score components into recruiter-readable reasoning."],
            ["What is format bias?", "A candidate can be penalized if the parser fails due to PDF/image formatting. OCR fallback reduces that risk."],
            ["Main limitation?", "Regex and TF-IDF cannot fully understand synonyms or implicit skills."],
            ["Future work?", "Hybrid Sentence-BERT context, dynamic skill ontology, fairness audit and recruiter feedback learning."],
        ], styles, widths=[2.0 * inch, 4.25 * inch]),
        p("15. Detailed Algorithmic Flow to Explain to Ma'am", styles, "H1"),
        p("If asked for the complete algorithm, explain the project as a deterministic pipeline. The important point is that every candidate passes through the same stages, so comparison remains consistent.", styles),
        code("""
INPUT:
    Job description J
    Resume batch R = {r1, r2, ..., rn}
    Recruiter weights W = {tech, soft, yoe, context}
    Extra skill bonus cap Bmax

PROCESS:
    1. Extract text from J.
    2. Extract required tech skills, soft skills and YoE from J.
    3. For each resume ri:
        a. Detect file type.
        b. Extract text digitally if possible.
        c. If extraction is weak, invoke OCR fallback.
        d. Normalize extracted text.
        e. Extract candidate skills, soft skills and YoE.
        f. Compute tech, soft, YoE and TF-IDF context scores.
        g. Compute capped extra skills bonus.
        h. Calculate final weighted score.
        i. Generate XAI explanation.
    4. Sort candidates by final score.

OUTPUT:
    Ranked candidate list + score breakdown + XAI explanation + charts.
        """, styles),
        p("16. Route-by-Route Backend Walkthrough", styles, "H1"),
        table([
            ["Route / Page", "What happens", "Viva explanation"],
            ["/upload", "Receives JD, resumes and weights.", "This is where input enters the AI pipeline."],
            ["/analyze", "Shows progress page.", "It prevents the user from waiting on a frozen upload page."],
            ["/start-analysis", "Starts daemon background thread.", "Heavy processing is detached from the request-response cycle."],
            ["/analysis-status/<job_id>", "Returns status and message.", "Frontend polls it every two seconds."],
            ["/results", "Renders ranked output.", "Displays scores, charts, skills and explanations."],
        ], styles, widths=[1.55 * inch, 2.15 * inch, 2.55 * inch]),
        p("17. Internal Data Objects to Remember", styles, "H1"),
        bullets([
            "<b>NLP output:</b> tokens, lemmas, entities, technical_skills, soft_skills, years_of_experience.",
            "<b>Matcher output:</b> final_score, text_similarity, tech_skill_score, soft_skill_score, yoe_score, individual score contributions and bonus.",
            "<b>Explainer output:</b> candidate_name, match_score, matched_skills, missing_skills, extra_skills, detected_soft_skills and final explanation.",
            "<b>Job state:</b> queued, loading_models, processing_jd, processing_resumes, computing_scores, generating_explanations, creating_charts, done.",
        ], styles),
        p("18. Why Each Design Choice Was Made", styles, "H1"),
        table([
            ["Choice", "Reason", "Trade-off"],
            ["Flask", "Lightweight and easy for modular prototype.", "Not as batteries-included as Django."],
            ["SQLite", "Zero-server local persistence.", "Not ideal for very high concurrent writes."],
            ["Regex skills", "Precise, auditable hard-skill matching.", "Misses synonyms unless added to ontology."],
            ["TF-IDF", "Fast, CPU-friendly context signal.", "Less semantic than BERT/Sentence-BERT."],
            ["OCR fallback", "Reduces format bias for scanned/image resumes.", "Accuracy depends on image quality."],
            ["Async thread", "Avoids blocking browser request during batch analysis.", "In production, Celery/Redis would be stronger."],
        ], styles, widths=[1.25 * inch, 2.65 * inch, 2.35 * inch]),
        p("19. Last-Minute Revision Checklist", styles, "H1"),
        bullets([
            "Know the one-line project pitch.",
            "Be able to draw the flow: Upload -> Parse/OCR -> NLP -> TF-IDF -> Score -> XAI -> Dashboard.",
            "Remember default weights: Tech 60, YoE 15, Context 15, Soft 10, Bonus 5.",
            "Remember the main benchmark numbers: 90.5% TXT/PNG, 90.0% PDF, Approach A 0.0062 sec and 0.12 MB.",
            "Admit limitations confidently: regex misses synonyms, TF-IDF lacks deep semantics, OCR depends on scan quality.",
            "Close with future work: hybrid Sentence-BERT context, fairness audit, dynamic skill ontology and recruiter feedback loop.",
        ], styles),
        p("20. Final Viva Closing Statement", styles, "H1"),
        p("This project demonstrates a practical AI recruitment decision-support system. It intentionally balances speed, cost, transparency and acceptable accuracy instead of chasing the heaviest model. The system is best understood as an explainable first-pass filter: it reduces HR workload, gives auditable reasons, handles multiple resume formats, and leaves the final decision to humans.", styles, "Callout"),
    ]
    return story


def hinglish_story(styles):
    story = []
    story += [
        p("AI-Powered Resume Screening System", styles, "Title"),
        p("Final Viva Preparation Guide - Hinglish Version", styles, "Subtitle"),
        p("Project: AI in Recruitment Process: A Study on the Use of AI for Resume Analysis", styles, "Subtitle"),
        p("Team: Rohan Garg, Punit Sukhani, Saksham | Guide: Mrs. Gull Kaur", styles, "Subtitle"),
    ]
    add_square_image(story, FIG / "dtu_logo.png", "Delhi Technological University", styles)
    story.append(PageBreak())
    story += [
        p("1. Project ka Short Summary", styles, "H1"),
        p("Ye project ek AI-powered resume screening prototype hai. System ek Job Description (JD) aur multiple resumes leta hai, sab files se text extract karta hai, skills aur years of experience detect karta hai, weighted score calculate karta hai, score ka explanation generate karta hai, aur final dashboard par candidates ko rank karke dikhata hai.", styles),
        p("<b>Viva line:</b> Hamara system HR ko replace nahi karta. Ye ek explainable first-pass filter hai jo initial shortlisting fast, transparent aur low-cost banata hai.", styles, "Callout"),
        p("2. Problem kya solve kar rahe hain?", styles, "H1"),
        p("Recruiters ko ek job opening ke liye bahut saare resumes milte hain. Manual screening slow hoti hai, inconsistent ho sakti hai, aur bias ka chance hota hai. Traditional ATS mostly keyword matching karta hai, isliye agar candidate ne same wording use nahi ki, to relevant candidate miss ho sakta hai. LLM models semantic understanding me better hote hain, but costly, slow, memory-heavy aur less explainable hote hain. Isliye humne lightweight Regex + TF-IDF + XAI based prototype banaya.", styles),
        bullets([
            "<b>Manual issue:</b> time-consuming aur inconsistent.",
            "<b>Keyword issue:</b> synonyms miss ho sakte hain, keyword stuffing possible hai.",
            "<b>LLM issue:</b> cost, latency, memory aur black-box explainability.",
            "<b>Our solution:</b> fast, transparent, auditable first-pass screening.",
        ], styles),
        p("3. Input se Output tak Flow", styles, "H1"),
        p("<b>Input:</b> recruiter login, JD text, resumes in PDF/DOCX/TXT/PNG/JPG, aur scoring weights. <b>Output:</b> ranked candidates, final score, matched/missing skills, soft skills, YoE status, bonus skills, charts, aur XAI explanation.", styles),
    ]
    add_image(story, FIG / "project_flowchart.png", "Figure: Complete flow - frontend upload se parser, OCR, NLP, matching, XAI aur result dashboard tak.", styles, 5.8 * inch)
    story += [
        p("Step-wise system flow", styles, "H2"),
        numbered([
            "Recruiter login/register karta hai.",
            "Upload screen par JD paste karta hai aur resumes upload karta hai.",
            "Recruiter weights set karta hai: technical skills, experience, context, soft skills, bonus cap.",
            "Backend files validate karta hai aur data UUID key ke saath store karta hai.",
            "Analyze page background job start karta hai aur status poll karta hai.",
            "Parser text extract karta hai; scanned/image files OCR pipeline me jaati hain.",
            "NLP module skills, soft skills aur years of experience extract karta hai.",
            "Matching engine component scores aur final weighted score calculate karta hai.",
            "XAI module score ko plain-English explanation me convert karta hai.",
            "Dashboard ranked results, charts, tags aur explanation panels dikhata hai.",
        ], styles),
        p("4. Components aur Responsibilities", styles, "H1"),
    ]
    tech_stack, bench = common_tables(styles)
    story += [tech_stack, Spacer(1, 8)]
    story += [
        p("Important source modules", styles, "H2"),
        bullets([
            "<b>app.py:</b> Flask app create karta hai.",
            "<b>models.py:</b> User model for auth.",
            "<b>resume_parser/parser.py:</b> PDF/DOCX/TXT/image parsing aur OCR fallback.",
            "<b>nlp_processing/processor.py:</b> SpaCy, skills, soft skills, YoE extraction.",
            "<b>feature_extraction/extractor.py:</b> TF-IDF vectorizer.",
            "<b>matching_engine/matcher.py:</b> weighted scoring formula.",
            "<b>explainable_ai/explainer.py:</b> human-readable explanation.",
            "<b>visualization/charts.py:</b> score and skill charts as base64 images.",
            "<b>web_app/routes.py:</b> upload, analyze, status polling, results.",
        ], styles),
        p("5. Parsing aur OCR Pipeline", styles, "H1"),
        p("AI processing se pehle har resume ko plain text me convert karna zaroori hai. Parser pehle digital extraction try karta hai. Agar PDF se 50 characters se kam text aata hai, to system assume karta hai ki file scanned ya parser-resistant hai, aur OCR fallback trigger karta hai. Isse format bias reduce hota hai.", styles),
        table([
            ["Format", "Method", "Explanation"],
            [".txt", "Direct read", "Seedha text read hota hai."],
            [".docx", "python-docx", "Word XML paragraphs se text nikalta hai."],
            [".pdf", "PyPDF2", "Agar text weak hai, PDF images me convert karke OCR."],
            [".png/.jpg", "Pillow + OCR", "Image preprocessing ke baad OCR."],
        ], styles, widths=[1.1 * inch, 1.7 * inch, 3.45 * inch]),
        p("OCR preprocessing me transparency flattening, grayscale conversion, contrast boost, sharpening, binarization, aur Tesseract CLI extraction hota hai. Direct Tesseract CLI use kiya gaya hai because pytesseract wrapper me decode issues aa sakte hain.", styles),
        p("Algorithm: OCR-aware parsing", styles, "H2"),
        code("""
FUNCTION ParseDocument(file, extension):
    IF .txt: read text directly
    IF .docx: extract paragraphs using python-docx
    IF .pdf:
        text = PyPDF2_extract(file)
        IF length(text) < 50:
            convert PDF pages to images
            return OCR_Pipeline(images)
    IF image file:
        return OCR_Pipeline(file)

FUNCTION OCR_Pipeline(image):
    flatten transparency
    grayscale -> contrast -> sharpen -> binarize
    return Tesseract text
        """, styles),
        p("6. NLP aur Regex Skill Extraction", styles, "H1"),
        p("NLP layer SpaCy ka en_core_web_sm model use karta hai tokenization, lemmatization aur entities ke liye. But technical skills generic NER se nahi nikalte; curated skills database ke against strict regex word-boundary matching use hoti hai. Reason: precision. Example: skill 'C' ko 'communication' ke andar match nahi hona chahiye.", styles),
        code(r"pattern = r'\b' + re.escape(skill) + r'\b'", styles),
        p("YoE extraction three-step cascade follow karta hai: direct phrase ('5 years experience'), reversed phrase ('Experience: 5 years'), aur date ranges ('June 2024 - August 2025'). Invalid values filter hote hain, and education-duration inflation avoid kiya jata hai.", styles),
        p("7. TF-IDF Context Matching", styles, "H1"),
        p("TF-IDF resume aur JD ko vectors me convert karta hai. Project me max_features=5000, stop_words='english', aur ngram_range=(1,2) use hota hai. Bigrams phrases jaise machine learning capture karte hain. Cosine similarity check karti hai ki resume aur JD same direction/topics me align hain ya nahi.", styles),
        p("<b>Formula:</b> Context Score = dot(A,B) / (||A|| × ||B||). Yahan A resume vector hai aur B JD vector hai.", styles, "Callout"),
        p("8. Matching Formula", styles, "H1"),
        table([
            ["Score", "Calculation", "Viva explanation"],
            ["Tech", "matched tech / required tech", "Hard technical fit."],
            ["Soft", "matched soft / required soft", "Communication/teamwork etc."],
            ["YoE", "min(resume_y / jd_y, 1.0)", "Over-qualified score cap."],
            ["Context", "TF-IDF cosine", "Broader textual similarity."],
            ["Bonus", "capped extra skills", "Adjacent skills reward, but limited."],
        ], styles, widths=[1.0 * inch, 2.05 * inch, 3.2 * inch]),
        code("""
Final Score =
    Tech*Wtech + Soft*Wsoft + YoE*Wyoe + Context*Wcontext + Bonus

Default:
Tech 60%, YoE 15%, Context 15%, Soft 10%, Bonus cap 5%
        """, styles),
        p("9. Explainable AI (XAI)", styles, "H1"),
        p("XAI module score dictionary ko directly read karke explanation banata hai. Isliye ye black-box explanation nahi hai. It lists matched skills, missing skills, extra skills, experience status, score contribution and match band.", styles),
    ]
    add_image(story, FIG / "ai_score_breakdown.png", "Figure: XAI breakdown - score components, matched skills, missing skills, bonus skills.", styles, 6.3 * inch)
    story += [
        p("Match bands: Strong >= 75%, Moderate >= 50%, Partial >= 30%, Weak < 30%.", styles, "Callout"),
        p("10. Frontend, Sliders aur Async Backend", styles, "H1"),
    ]
    add_image(story, FIG / "ai_scoring_configuration.png", "Figure: Recruiter-controlled scoring weights. Bonus cap separately handled hota hai.", styles, 6.2 * inch)
    story += [
        p("Upload dashboard me 5 sliders hain: technical skills, YoE, context, soft skills, bonus cap. First 4 sliders ka total 100% maintain hota hai using normalizeSliders(). Bonus alag rakha gaya hai because it is additive, not part of core normalized score.", styles),
        p("Backend async architecture use karta hai. Upload ke baad analyze page /start-analysis hit karta hai, background daemon thread analysis run karta hai, aur frontend /analysis-status/<job_id> ko poll karta hai. Isse browser freeze nahi hota.", styles),
        code("""
POST /upload -> validate and store data
GET /analyze -> progress page
POST /start-analysis -> background thread
GET /analysis-status/<job_id> -> progress polling
GET /results -> ranked dashboard
        """, styles),
        p("11. Benchmark Results", styles, "H1"),
        bench,
        p("Approach A/B/C ka meaning", styles, "H2"),
        bullets([
            "<b>Approach A:</b> Current app - Regex + TF-IDF. Fast, explainable, CPU-friendly.",
            "<b>Approach C:</b> Pure LLM/Sentence-BERT. Semantic understanding better, but costly and less bounded.",
            "<b>Approach B:</b> Future hybrid - regex hard-skill shield + LLM context. Better future direction but heavier.",
        ], styles),
        p("12. Strengths, Limitations, Future Work", styles, "H1"),
        table([
            ["Strengths", "Limitations", "Future work"],
            ["Fast, low-cost, OCR fallback, XAI, dynamic weights, keyword-stuffing resistance.", "Regex synonyms miss kar sakta hai; TF-IDF deep meaning nahi samajhta; skills DB update karni padti hai; OCR scan quality par depend karta hai.", "Sentence-BERT hybrid, dynamic skill graph, fairness audit, recruiter feedback, production DB, larger real dataset."],
        ], styles, widths=[2.05 * inch, 2.2 * inch, 2.0 * inch]),
        p("13. Viva Demo Script", styles, "H1"),
        numbered([
            "App run karo: python app.py, then browser me http://127.0.0.1:5001.",
            "Login/register dikhao.",
            "Upload screen par JD paste karo and resumes upload karo.",
            "Weight sliders explain karo: Tech 60, YoE 15, Context 15, Soft 10, Bonus cap 5.",
            "Submit karke analyze/progress page dikhao.",
            "Results dashboard me ranking, score breakdown, matched/missing skills explain karo.",
            "XAI panel open karke batao ki score black-box nahi hai.",
            "End me honest limitation bolo: synonyms ke liye future hybrid Sentence-BERT useful hoga.",
        ], styles),
        p("14. Viva Q&A Quick Sheet", styles, "H1"),
        table([
            ["Question", "Answer"],
            ["Regex kyun?", "Strict word boundaries precision dete hain and false positives avoid karte hain."],
            ["TF-IDF kyun?", "Fast, interpretable, CPU-friendly lexical context matching."],
            ["LLM kyun nahi?", "LLM semantic better hai but cost/latency/memory and explainability issue hai."],
            ["XAI kya hai?", "Score components ko human-readable explanation me convert karna."],
            ["OCR kyun?", "Scanned/image resumes ko process karke format bias reduce karna."],
            ["Main limitation?", "Regex implicit skills/synonyms miss kar sakta hai."],
            ["Future scope?", "Hybrid Sentence-BERT context, dynamic skill ontology, fairness audit."],
        ], styles, widths=[2.0 * inch, 4.25 * inch]),
        p("15. Ma'am ko Algorithm kaise explain karna hai", styles, "H1"),
        p("Agar ma'am pooche ki input se output tak algorithm kya hai, to project ko deterministic pipeline ki tarah explain karna. Important point: har candidate same stages se pass hota hai, isliye ranking consistent hoti hai.", styles),
        code("""
INPUT:
    Job Description J
    Resume batch R = {r1, r2, ..., rn}
    Recruiter weights W
    Bonus cap Bmax

PROCESS:
    1. JD ka text extract karo.
    2. JD se required skills, soft skills, YoE nikalo.
    3. Har resume ke liye:
        a. File type detect karo.
        b. Digital text extraction try karo.
        c. Text weak ho to OCR fallback chalao.
        d. Text normalize karo.
        e. Candidate skills, soft skills, YoE extract karo.
        f. Tech, soft, YoE, context scores calculate karo.
        g. Extra skills bonus cap ke saath calculate karo.
        h. Final weighted score banao.
        i. XAI explanation generate karo.
    4. Candidates ko final score ke according sort karo.

OUTPUT:
    Ranked list + score breakdown + explanation + charts.
        """, styles),
        p("16. Backend Routes ka Flow", styles, "H1"),
        table([
            ["Route / Page", "Kya hota hai", "Viva me kya bolna hai"],
            ["/upload", "JD, resumes and weights receive karta hai.", "Yahi se AI pipeline input leti hai."],
            ["/analyze", "Progress page dikhata hai.", "User ko freeze feel nahi hota."],
            ["/start-analysis", "Background thread start karta hai.", "Heavy analysis request thread ko block nahi karti."],
            ["/analysis-status/<job_id>", "Current status return karta hai.", "Frontend 2 sec interval me poll karta hai."],
            ["/results", "Ranked output render karta hai.", "Scores, charts, skills and explanations show hote hain."],
        ], styles, widths=[1.55 * inch, 2.15 * inch, 2.55 * inch]),
        p("17. Internal Data Objects yaad rakhna", styles, "H1"),
        bullets([
            "<b>NLP output:</b> tokens, lemmas, entities, technical_skills, soft_skills, years_of_experience.",
            "<b>Matcher output:</b> final_score, text_similarity, tech_score, soft_score, yoe_score, contributions, bonus.",
            "<b>Explainer output:</b> matched skills, missing skills, extra skills, detected soft skills, final explanation.",
            "<b>Job status:</b> queued, loading_models, processing_jd, processing_resumes, computing_scores, generating_explanations, creating_charts, done.",
        ], styles),
        p("18. Design Choices ka Reason", styles, "H1"),
        table([
            ["Choice", "Reason", "Trade-off"],
            ["Flask", "Lightweight and modular prototype ke liye easy.", "Django jitna built-in structure nahi."],
            ["SQLite", "Local DB, no server needed.", "High-concurrency production ke liye ideal nahi."],
            ["Regex skills", "Precise and auditable hard-skill matching.", "Synonyms miss ho sakte hain."],
            ["TF-IDF", "Fast, interpretable, CPU-friendly context score.", "BERT jaisa semantic nahi."],
            ["OCR fallback", "Scanned/image resumes process karne ke liye.", "Image quality par depend karta hai."],
            ["Async thread", "Browser/request block nahi hota.", "Production me Celery/Redis better hoga."],
        ], styles, widths=[1.25 * inch, 2.65 * inch, 2.35 * inch]),
        p("19. Last-Minute Revision Checklist", styles, "H1"),
        bullets([
            "One-line pitch yaad rakho: explainable first-pass resume screening system.",
            "Flow draw kar pao: Upload -> Parse/OCR -> NLP -> TF-IDF -> Score -> XAI -> Dashboard.",
            "Default weights yaad rakho: Tech 60, YoE 15, Context 15, Soft 10, Bonus 5.",
            "Benchmark numbers: TXT/PNG 90.5%, PDF 90.0%, Approach A 0.0062 sec and 0.12 MB.",
            "Limitations confidently bolo: regex synonyms miss karta hai, TF-IDF deep semantics nahi samajhta, OCR scan quality par depend karta hai.",
            "Future scope bolo: Sentence-BERT hybrid, fairness audit, dynamic skill ontology, recruiter feedback loop.",
        ], styles),
        p("20. Final Closing Line", styles, "H1"),
        p("Hamara project ek practical, explainable, low-cost first-pass resume screening system hai. Itna heavy nahi ki LLM jaisa expensive ho, aur itna simple bhi nahi ki sirf keyword counter ban jaye. Iska main value speed, transparency, OCR resilience, dynamic scoring, aur recruiter-friendly explanation hai.", styles, "Callout"),
    ]
    return story


def build_all():
    styles = make_styles()
    pdfs = [
        (OUT / "AI_Resume_Screening_Viva_Guide_English.pdf", english_story(styles)),
        (OUT / "AI_Resume_Screening_Viva_Guide_Hinglish.pdf", hinglish_story(styles)),
    ]
    for path, story in pdfs:
        doc = make_doc(path)
        doc.build(story)
        print(path)


if __name__ == "__main__":
    build_all()
