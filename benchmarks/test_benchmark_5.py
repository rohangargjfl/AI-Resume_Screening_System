import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["OMP_NUM_THREADS"] = "1"

import time
import tracemalloc
from sentence_transformers import SentenceTransformer
from feature_extraction.extractor import FeatureExtractor

def run_benchmark_5():
    print("="*60)
    print("BENCHMARK 5: COST & RESOURCE EFFICIENCY (TF-IDF vs LLM)")
    print("="*60)

    # Sample batch of 500 resumes (simulated text) for a more noticeable difference
    jd_text = "Backend Engineer with Python, Django, REST, PostgreSQL."
    resume_batch = [
        "Software Engineer skilled in Python, Django, and database management." * 5
    ] * 500 

    # ---------------------------------------------------------
    # TEST A: Your Project's TF-IDF Architecture
    # ---------------------------------------------------------
    print("\nStarting Test A: Project TF-IDF (Scikit-Learn)...")
    extractor = FeatureExtractor()
    
    tracemalloc.start()
    start_time = time.time()
    
    # Process the batch exactly as your project does
    all_docs = [jd_text] + resume_batch
    # FIX: Use the actual method or attribute from your project
    tfidf_matrix = extractor.tfidf_vectors(all_docs)
    
    end_time = time.time()
    current, peak_tfidf = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    tfidf_time = end_time - start_time
    print(f"-> Time Taken : {tfidf_time:.4f} seconds")
    print(f"-> Peak RAM   : {peak_tfidf / 10**6:.4f} MB")

    # ---------------------------------------------------------
    # TEST B: Semantic LLM (Sentence-Transformers)
    # ---------------------------------------------------------
    print("\nStarting Test B: Semantic Transformer (all-MiniLM-L6-v2)...")
    
    tracemalloc.start()
    start_time = time.time()
    
    # Load model and encode (mimics real-world transformer usage)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(all_docs)
    
    end_time = time.time()
    current, peak_llm = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    llm_time = end_time - start_time
    print(f"-> Time Taken : {llm_time:.4f} seconds")
    print(f"-> Peak RAM   : {peak_llm / 10**6:.4f} MB")

    # ---------------------------------------------------------
    # COMPARISON RESULTS
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("EFFICIENCY MULTIPLIERS:")
    # Prevent division by zero if tfidf_time is extremely small
    speed_gain = (llm_time / tfidf_time) if tfidf_time > 0 else float('inf')
    print(f"Speed Gain : TF-IDF is {speed_gain:.1f}x faster")
    print(f"RAM Saved  : TF-IDF uses {peak_llm / peak_tfidf:.1f}x less memory")
    print("="*60)

if __name__ == "__main__":
    run_benchmark_5()