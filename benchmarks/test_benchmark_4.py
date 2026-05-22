import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["OMP_NUM_THREADS"] = "1"

from nlp_processing.processor import NLPProcessor
from matching_engine.matcher import MatchingEngine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def run_benchmark_4():
    print("="*70)
    print("BENCHMARK 4: SYNONYM & IMPLICIT COMPETENCY GAP (Project vs LLM)")
    print("="*70)

    # Initialize your actual project classes
    nlp = NLPProcessor()
    matcher = MatchingEngine()
    
    # Initialize Semantic Baseline
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

    # The Test Data
    jd_text = "Required: REST API, Leadership, 3 years experience."
    resume_text = "I have 3 years of experience. Built RESTful architecture. Directed a team of 5 developers."
    
    # ---------------------------------------------------------
    # TEST A: Your Project's Actual Pipeline
    # ---------------------------------------------------------
    print("\n--- TEST A: Project NLP & Matching Engine ---")
    
    jd_data = nlp.process(jd_text)
    resume_data = nlp.process(resume_text)
    
    # Format resume data as expected by matcher (list of dicts, must contain 'text' key as well)
    resume_data['text'] = resume_text
    resumes_list = [resume_data]
    
    weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}
    
    # FIX: Call compute_scores_detailed with the correct signature
    project_results = matcher.compute_scores_detailed(
        jd_text=jd_text,
        jd_tech_skills=list(jd_data['technical_skills']),
        jd_soft_skills=list(jd_data['soft_skills']),
        resumes=resumes_list,
        jd_yoe=jd_data.get('years_of_experience', 0),
        weights=weights
    )
    
    project_scores = project_results[0]
    
    print(f"Extracted Tech Skills (Project) : {resume_data.get('technical_skills', [])}")
    print(f"Extracted Soft Skills (Project) : {resume_data.get('soft_skills', [])}")
    print(f"Project Tech Score              : {project_scores.get('tech_skill_score', 0):.1f}%")
    print(f"Project Soft Score              : {project_scores.get('soft_skill_score', 0):.1f}%")
    print(f"Project YoE Score               : {project_scores.get('yoe_score', 0):.1f}% (Resume: {project_scores.get('resume_yoe', 0)} / JD: {project_scores.get('jd_yoe', 0)})")
    print(f"Project TF-IDF Context Sim      : {project_scores.get('text_similarity', 0):.1f}%")
    print(f"Project Extra Skills Bonus      : +{project_scores.get('extra_skills_bonus', 0):.1f}%")
    print(f"PROJECT FINAL BLENDED SCORE     : {project_scores.get('final_score', 0):.1f}%")
    
    # ---------------------------------------------------------
    # TEST B: The Semantic Baseline (Sentence-BERT)
    # ---------------------------------------------------------
    print("\n--- TEST B: Semantic LLM Baseline ---")
    
    jd_embedding = semantic_model.encode([jd_text])
    resume_embedding = semantic_model.encode([resume_text])
    
    semantic_sim = cosine_similarity(jd_embedding, resume_embedding)[0][0] * 100
    
    print(f"JD Embedding Shape              : {jd_embedding.shape} (384 dense features)")
    print(f"Resume Embedding Shape          : {resume_embedding.shape} (384 dense features)")
    print(f"Computation Method              : Cosine Similarity (A · B / ||A|| ||B||)")
    print(f"Semantic Context Similarity     : {semantic_sim:.1f}%")

    # ---------------------------------------------------------
    # CONCLUSION
    # ---------------------------------------------------------
    print("\n" + "="*70)
    print("RESEARCH CONCLUSION:")
    print(f"1. Synonym Gap: Project Tech Score is {project_scores.get('tech_skill_score', 0):.1f}% because '\\bREST\\b' did not extract 'RESTful'.")
    print(f"2. Implicit Gap: Project Soft Score is {project_scores.get('soft_skill_score', 0):.1f}% because it missed 'Directed a team'.")
    print(f"3. Context Gap: Pure TF-IDF scored {project_scores.get('text_similarity', 0):.1f}% vs LLM's {semantic_sim:.1f}%.")
    print("="*70)

if __name__ == "__main__":
    run_benchmark_4()
