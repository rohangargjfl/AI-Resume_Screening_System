import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

from nlp_processing.processor import NLPProcessor
from matching_engine.matcher import MatchingEngine

def run_benchmark_2():
    print("="*80)
    print("BENCHMARK 2: DILUTION & KEYWORD STUFFING RESISTANCE")
    print("="*80)

    nlp = NLPProcessor()
    matcher = MatchingEngine()

    jd_text = "Required Technical Skills: Python, Django, REST, PostgreSQL."
    
    # Test Data: 3 Resumes with the exact same 4 technical skills, but different text contexts.
    resumes = {
        "Baseline Profile": "Technical skills include Python, Django, REST, and PostgreSQL.",
        
        "Verbose Profile (Dilution)": "Technical skills include Python, Django, REST, and PostgreSQL. " + 
                                      "In my free time, I really love hiking up large mountains, cooking Italian food, " + 
                                      "playing the acoustic guitar, and walking my dog in the park.",
                                      
        "Keyword Stuffer (Cheater)": "Technical skills include Python, Django, REST, and PostgreSQL. " +
                                     "Python Python Python Django Django REST REST PostgreSQL " * 10
    }
    
    jd_data = nlp.process(jd_text)
    resumes_list = []
    
    for name, text in resumes.items():
        data = nlp.process(text)
        data['text'] = text
        data['name'] = name  # Tag it to keep track
        resumes_list.append(data)
        
    weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}
    
    project_results = matcher.compute_scores_detailed(
        jd_text=jd_text,
        jd_tech_skills=list(jd_data['technical_skills']),
        jd_soft_skills=list(jd_data['soft_skills']),
        resumes=resumes_list,
        jd_yoe=jd_data.get('years_of_experience', 0),
        weights=weights
    )
    
    print(f"Target JD Skills: {list(jd_data['technical_skills'])}\n")
    
    for idx, r in enumerate(project_results):
        name = resumes_list[idx]['name']
        print(f"--- {name} ---")
        if name == "Baseline Profile":
            print("-> Expected Action   : Baseline standard performance.")
        elif name == "Verbose Profile (Dilution)":
            print("-> Expected Action   : Tech score remains 100%. Context score drops drastically due to unrelated hobbies (Dilution).")
        elif name == "Keyword Stuffer (Cheater)":
            print("-> Expected Action   : Tech score remains 100%. Context score grows logarithmically, but stops far below 100% to prevent cheating.")
        
        print(f"-> Actual Tech Score : {r.get('tech_skill_score', 0):.1f}% (Regex Protection)")
        print(f"-> Actual Context    : {r.get('text_similarity', 0):.1f}% (TF-IDF Sensitivity)")
        print(f"-> Final Score       : {r.get('final_score', 0):.1f}%\n")
        
    print("="*80)
    print("RESEARCH EXPECTATIONS:")
    print("1. All three should have identical Tech Scores (proving Regex protects core competencies).")
    print("2. The Verbose profile's Context score should drop (proving the Dilution Effect).")
    print("3. The Keyword Stuffer should NOT see a massive linear Context increase due to sublinear TF-IDF math.")
    print("="*80)

if __name__ == "__main__":
    run_benchmark_2()
