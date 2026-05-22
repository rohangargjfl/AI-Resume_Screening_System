"""
MocrEngine – Isolated subprocess runner for rednote-hilab/dots.mocr.

The model's custom processor (trust_remote_code=True) crashes when loaded
in a thread context on macOS due to a Rust tokenizer mutex bug. Running
inference in a dedicated subprocess bypasses this entirely.

Environment:
    USE_MOCR=true   (default) – enable this engine
    USE_MOCR=false            – skip and let caller use Tesseract fallback
"""

import os
import sys
import json
import logging
import subprocess
import tempfile

logger = logging.getLogger("MocrEngine")

_MODEL_ID = "rednote-hilab/dots.mocr"

_OCR_PROMPT = (
    "Please extract all text from this image exactly as it appears. "
    "Output only the raw text content, preserving line breaks. "
    "Do not add explanations, JSON, or markdown formatting."
)

# Path to the worker script (same directory as this file)
_WORKER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_mocr_worker.py")


def _is_enabled() -> bool:
    """Return True unless the user explicitly set USE_MOCR=false."""
    return os.environ.get("USE_MOCR", "true").strip().lower() not in ("false", "0", "no")


def run(image_path: str) -> str:
    """
    Run dots.mocr OCR on a single image file via an isolated subprocess.

    Running in a subprocess avoids the Rust tokenizer mutex crash that occurs
    when the model's custom processor is loaded inside a thread on macOS.

    Args:
        image_path: Absolute path to a PNG / JPG image.

    Returns:
        Extracted text string (may be empty if model returns nothing).

    Raises:
        RuntimeError: if USE_MOCR is disabled, or inference fails.
    """
    if not _is_enabled():
        raise RuntimeError("USE_MOCR is disabled.")

    if not os.path.exists(_WORKER_SCRIPT):
        raise RuntimeError(f"Worker script not found: {_WORKER_SCRIPT}")

    logger.info(f"[MOCR] Spawning inference subprocess for: {os.path.basename(image_path)}")

    env = os.environ.copy()
    env["TOKENIZERS_PARALLELISM"] = "false"
    env["TRANSFORMERS_OFFLINE"] = "1"   # use local cache only, skip network check
    env["HF_DATASETS_OFFLINE"] = "1"

    try:
        result = subprocess.run(
            [sys.executable, _WORKER_SCRIPT, image_path, _OCR_PROMPT],
            capture_output=True,
            timeout=300,   # 5 min timeout for slow CPU inference
            env=env,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore").strip()
            raise RuntimeError(f"Worker exited {result.returncode}: {stderr[-500:]}")

        output = result.stdout.decode("utf-8", errors="ignore").strip()

        # Worker outputs: {"text": "...", "error": null}
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            # Fallback: if worker printed plain text (shouldn't happen)
            return output

        if data.get("error"):
            raise RuntimeError(f"Worker error: {data['error']}")

        return data.get("text", "")

    except subprocess.TimeoutExpired:
        raise RuntimeError("dots.mocr inference timed out (>5 min).")
    except Exception as e:
        raise RuntimeError(f"dots.mocr subprocess failed: {e}") from e
