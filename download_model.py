import os
from huggingface_hub import snapshot_download, try_to_load_from_cache

if __name__ == "__main__":
    model_id = "rednote-hilab/dots.mocr"
    print(f"Checking cache for {model_id}...")
    
    cached_path = try_to_load_from_cache(model_id, "config.json")
    if cached_path:
        print(f"Model already cached at: {os.path.dirname(cached_path)}")
    else:
        print("Starting download of dots.mocr model... (This is ~6-7 GB)")
        try:
            path = snapshot_download(repo_id=model_id, resume_download=True, max_workers=4)
            print(f"Download complete! Model cached at: {path}")
        except Exception as e:
            print(f"Error downloading model: {e}")
