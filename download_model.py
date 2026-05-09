import os
from huggingface_hub import snapshot_download

if __name__ == "__main__":
    print("Starting download of dots.mocr model...")
    model_id = "rednote-hilab/dots.mocr"
    try:
        path = snapshot_download(repo_id=model_id, resume_download=True, max_workers=4)
        print(f"Download complete! Model cached at: {path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
