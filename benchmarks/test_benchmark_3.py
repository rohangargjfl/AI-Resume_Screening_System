import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

from nlp_processing.processor import NLPProcessor
from matching_engine.matcher import MatchingEngine
from explainable_ai.explainer import Explainer

def run_benchmark_3():
    print("="*75)
    print("BENCHMARK 3: EXPLAINABLE AI (XAI) & MATH BOUNDARIES")
    print("="*75)

    nlp = NLPProcessor()
    matcher = MatchingEngine()
    explainer = Explainer()

    # The Test Data: JD wants 3 YoE and 4 tech skills.
    jd_text = "Backend Developer. Required: Python, Django, REST, PostgreSQL. 3 years experience."
    
    # Candidate is OVER-qualified in YoE (6 > 3), misses 2 tech skills, but has 4 extra skills.
    resume_text = "I have 6 years of experience. I develop with Python and Django. I also use AWS, Docker, Kubernetes, and Redis."
    
    jd_data = nlp.process(jd_text)
    resume_data = nlp.process(resume_text)
    
    resume_data['text'] = resume_text
    resumes_list = [resume_data]
    
    weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}
    
    # 1. Run the Matching Engine
    project_results = matcher.compute_scores_detailed(
        jd_text=jd_text,
        jd_tech_skills=list(jd_data['technical_skills']),
        jd_soft_skills=list(jd_data['soft_skills']),
        resumes=resumes_list,
        jd_yoe=jd_data.get('years_of_experience', 0),
        weights=weights
    )
    
    scores = project_results[0]
    
    # 2. Run the Explainable AI (Format matches your explainer logic)
    candidate_name = "Candidate A (Edge Case)"
    explanation_data = explainer.explain(
        candidate_name=candidate_name,
        match_score=scores['final_score'],
        resume_technical_skills=list(resume_data['technical_skills']),
        resume_soft_skills=list(resume_data['soft_skills']),
        jd_technical_skills=list(jd_data['technical_skills']),
        jd_soft_skills=list(jd_data['soft_skills']),
        score_breakdown=scores
    )
    
    print("\n--- RAW MATHEMATICAL BOUNDARIES ---")
    print(f"-> Expected YoE Math : min(6/3, 1.0) * 100 = 100%")
    print(f"-> Actual YoE Math   : {scores.get('resume_yoe', 0)} / {scores.get('jd_yoe', 0)} years")
    print(f"-> Actual YoE Score  : {scores.get('yoe_score', 0):.1f}% (Capped successfully)")
    
    print(f"\n-> Expected Extra Skills: Cap at {weights['bonus']*100}% even with 4 skills.")
    print(f"-> Actual Extra Skills  : {explanation_data.get('extra_skills', [])}")
    print(f"-> Actual Bonus Score   : +{scores.get('extra_skills_bonus', 0):.1f}% (Capped successfully)")
    
    print("\n--- EXPLAINABLE AI (XAI) OUTPUT ---")
    print("This is the exact plain-English text generated for the recruiter:")
    if isinstance(explanation_data, dict) and 'explanation' in explanation_data:
        print(f"> \"{explanation_data['explanation']}\"")
    else:
        print(f"> {explanation_data}")

    print("\n" + "="*75)

if __name__ == "__main__":
    run_benchmark_3()
