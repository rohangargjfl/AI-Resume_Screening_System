import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

from nlp_processing.processor import NLPProcessor
from matching_engine.matcher import MatchingEngine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def run_benchmark_4():
    print("="*80)
    print("BENCHMARK 4: THE 3-WAY ARCHITECTURE COMPARISON (A vs B vs C)")
    print("="*80)

    nlp = NLPProcessor()
    matcher = MatchingEngine()
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

    # The Test Data
    jd_text = "Required: REST API, Leadership, 3 years experience."
    resume_text = "I have 3 years of experience. Built RESTful architecture. Directed a team of 5 developers."
    
    weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}
    
    jd_data = nlp.process(jd_text)
    resume_data = nlp.process(resume_text)
    resume_data['text'] = resume_text
    resumes_list = [resume_data]

    # --- APPROACH A: CURRENT PROJECT (Regex + TF-IDF + Math) ---
    project_results = matcher.compute_scores_detailed(
        jd_text=jd_text,
        jd_tech_skills=list(jd_data['technical_skills']),
        jd_soft_skills=list(jd_data['soft_skills']),
        resumes=resumes_list,
        jd_yoe=jd_data.get('years_of_experience', 0),
        weights=weights
    )
    scores_A = project_results[0]
    
    print("\n[APPROACH A: CURRENT APP (Regex + TF-IDF)]")
    print(f"-> Expected Action   : Fails to map 'RESTful' to 'REST'. Fails to map 'Directed a team' to 'Leadership'. Low Context score.")
    print(f"-> Actual Tech Score : {scores_A.get('tech_skill_score', 0):.1f}% (Missing: REST)")
    print(f"-> Actual Soft Score : {scores_A.get('soft_skill_score', 0):.1f}% (Missing: Leadership)")
    print(f"-> Actual Context    : {scores_A.get('text_similarity', 0):.1f}% (Lexical TF-IDF penalizes different phrasing)")
    print(f"-> FINAL SCORE       : {scores_A.get('final_score', 0):.1f}%")

    # --- APPROACH C: PURE LLM (Sentence-BERT Only) ---
    # Treats the entire document as one semantic vector (no hard tech boundaries)
    jd_embedding = semantic_model.encode([jd_text])
    resume_embedding = semantic_model.encode([resume_text])
    semantic_sim_raw = cosine_similarity(jd_embedding, resume_embedding)[0][0] * 100
    
    print("\n[APPROACH C: PURE LLM (Sentence-BERT Context Only)]")
    print(f"-> Expected Action   : Understands 'RESTful' = 'REST' and 'Directed a team' = 'Leadership'. High overall score, but loses hard boundaries.")
    print(f"-> Actual Context    : {semantic_sim_raw:.1f}% (Understands meaning, but no strict skill extraction)")
    print(f"-> FINAL SCORE       : {semantic_sim_raw:.1f}%")

    # --- APPROACH B: FUTURE HYBRID (Regex + Sentence-BERT + Math) ---
    # We take the strict Tech/YoE/Soft scores from Regex, but replace TF-IDF Context with LLM Context
    weighted_tech = (scores_A.get('tech_skill_score', 0) / 100) * weights['tech']
    weighted_soft = (scores_A.get('soft_skill_score', 0) / 100) * weights['soft']
    weighted_yoe = (scores_A.get('yoe_score', 0) / 100) * weights['yoe']
    weighted_context = (semantic_sim_raw / 100) * weights['context']
    bonus = scores_A.get('extra_skills_bonus', 0) / 100
    
    final_score_B = (weighted_tech + weighted_soft + weighted_yoe + weighted_context + bonus) * 100

    print("\n[APPROACH B: FUTURE HYBRID (Regex Tech + LLM Context)]")
    print(f"-> Expected Action   : Punishes for missing explicit keyword (Regex), but rewards for semantic similarity (LLM).")
    print(f"-> Actual Tech Score : {scores_A.get('tech_skill_score', 0):.1f}% (Regex Shield Activated)")
    print(f"-> Actual Context    : {semantic_sim_raw:.1f}% (LLM Context rewards implicit meaning)")
    print(f"-> FINAL SCORE       : {final_score_B:.1f}%")

    print("\n" + "="*80)
    print("EXPECTED RESEARCH CONCLUSION:")
    print("Approach A drops points heavily due to TF-IDF. Approach C provides no hard Tech/YoE boundaries.")
    print("Approach B combines the strict Regex shield for Tech/YoE with the semantic understanding of LLMs.")
    print("="*80)

if __name__ == "__main__":
    run_benchmark_4()
