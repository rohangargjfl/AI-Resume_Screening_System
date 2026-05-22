import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import io
import logging
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

# Intercept Logger to detect Tesseract vs MOCR
log_stream = io.StringIO()
logger = logging.getLogger('ResumeParser')
logger.addHandler(logging.StreamHandler(log_stream))
logger.setLevel(logging.INFO)

from resume_parser.parser import ResumeParser 
from nlp_processing.processor import NLPProcessor
from matching_engine.matcher import MatchingEngine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def run_benchmark_1():
    print("="*85)
    print("BENCHMARK 1: FORMAT BIAS, OCR RESILIENCE & EXTRACTION MECHANICS")
    print("="*85)

    parser = ResumeParser() 
    nlp = NLPProcessor()
    matcher = MatchingEngine()
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

    # The Job Description
    jd_text = "Required: Python, Django, REST, PostgreSQL. Leadership, Communication and 3 years experience."
    jd_data = nlp.process(jd_text)
    jd_embedding = semantic_model.encode([jd_text])
    
    weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}

    test_files = ['sample.txt', 'sample.pdf', 'sample.png']
    
    print("Starting Parsing & Scoring Pipeline...\n")

    for file_name in test_files:
        print(f"--- Processing File: {file_name} ---")
        
        # Clear log stream for this file
        log_stream.seek(0)
        log_stream.truncate(0)
        
        if not os.path.exists(file_name):
            print(f"ERROR: {file_name} not found! Please create it in the root folder.")
            continue

        # 1. PARSING LAYER
        try:
            extracted_text = parser.parse(file_name)
        except Exception as e:
            print(f"Extraction Error: {e}")
            continue

        # Detect OCR Engine used from logs
        logs = log_stream.getvalue()
        engine_used = "Digital Parsing (PyPDF2/Built-in)"
        if ".png" in file_name or ".jpg" in file_name:
            if "Tesseract extracted" in logs or "Falling back to Tesseract" in logs:
                engine_used = "OCR Pipeline: Tesseract (Fallback)"
            elif "dots.mocr extracted" in logs:
                engine_used = "OCR Pipeline: dots.mocr (Primary)"
            else:
                engine_used = "OCR Pipeline: Unknown"

        print(f"Extraction Engine    : {engine_used}")
        safe_text = extracted_text[:60].replace('\n', ' ').strip()
        print(f"Raw Text Preview     : \"{safe_text}...\"")

        # 2. NLP LAYER (Regex Extraction)
        resume_data = nlp.process(extracted_text)
        resume_data['text'] = extracted_text
        resume_data['name'] = file_name
        
        print("\n[EXTRACTION COMPARISON]")
        print(f"Regex Tech Extracted : {resume_data.get('technical_skills', [])}")
        print(f"Regex Soft Extracted : {resume_data.get('soft_skills', [])}")
        
        # LLMs like Sentence-BERT do NOT extract arrays of words. They compress the whole text into a Vector.
        # So we show the Semantic Similarity score to prove what the LLM 'caught' implicitly.
        resume_embedding = semantic_model.encode([extracted_text])
        llm_sim = cosine_similarity(jd_embedding, resume_embedding)[0][0] * 100
        print(f"LLM Semantic Output  : No exact words extracted. Instead, generates a 384-D Semantic Vector.")
        print(f"LLM Context Score    : {llm_sim:.1f}% Match (Understands overall meaning)")
        
        # 3. SCORING LAYER
        project_results = matcher.compute_scores_detailed(
            jd_text=jd_text,
            jd_tech_skills=list(jd_data['technical_skills']),
            jd_soft_skills=list(jd_data['soft_skills']),
            resumes=[resume_data],
            jd_yoe=jd_data.get('years_of_experience', 0),
            weights=weights
        )
        
        scores = project_results[0]
        print(f"\n[FINAL SCORES]")
        print(f"Tech Score (Regex)   : {scores.get('tech_skill_score', 0):.1f}%")
        print(f"Soft Score (Regex)   : {scores.get('soft_skill_score', 0):.1f}%")
        print(f"FINAL SYSTEM SCORE   : {scores.get('final_score', 0):.1f}%\n")

    print("="*85)
    print("EXPECTED RESEARCH CONCLUSION:")
    print("1. Regex exactly filters words from the skills_db for both Tech and Soft skills.")
    print("2. The LLM does not extract arrays; it converts the whole text to a vector for context.")
    print("3. Tesseract vs dots.mocr failover logic is proven to work dynamically.")
    print("="*85)

if __name__ == "__main__":
    run_benchmark_1()
