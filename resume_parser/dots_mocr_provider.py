"""
dots.mocr provider — wraps the 3B vision-language model as a drop-in
OCR backend for the resume parser.
"""

import os
import logging
import torch

logger = logging.getLogger("DotsMOCR")

_model = None
_processor = None

def _load_model():
    """Lazy-load model once; reuse across requests."""
    global _model, _processor
    if _model is not None:
        return _model, _processor
    
    from transformers import AutoModelForCausalLM, AutoProcessor
    import transformers.dynamic_module_utils
    import sys
    import types
    
    # Workaround 1: Mock sys.modules so the custom code's hard imports don't fail
    if "flash_attn" not in sys.modules:
        mock_fa = types.ModuleType("flash_attn")
        mock_fa.__version__ = "2.8.0"
        def dummy_func(*args, **kwargs):
            raise NotImplementedError("flash_attn is bypassed")
        mock_fa.flash_attn_func = dummy_func
        mock_fa.flash_attn_varlen_func = dummy_func
        sys.modules["flash_attn"] = mock_fa

    # Workaround 2: Patch transformers core check_imports so it doesn't look for package metadata
    original_check_imports = transformers.dynamic_module_utils.check_imports
    def patched_check_imports(filename):
        try:
            return original_check_imports(filename)
        except ImportError as e:
            if "flash_attn" in str(e):
                return []
            raise e
    transformers.dynamic_module_utils.check_imports = patched_check_imports
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    logger.info(f"[dots.mocr] Loading model on {device} (this takes ~30 sec first time, plus download time if not cached)...")
    
    model_id = "rednote-hilab/dots.mocr"
    
    _model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True,
    )
    if device == "cpu":
        _model = _model.to("cpu")
    
    _processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    logger.info("[dots.mocr] Model loaded ✓")
    return _model, _processor


def ocr_image(image_path: str) -> str:
    """Run dots.mocr on a single image, return plain text."""
    from qwen_vl_utils import process_vision_info

    model, processor = _load_model()
    device = next(model.parameters()).device

    # Use a prompt focused on simple text extraction for resumes
    prompt = (
        "Please extract all the text from this document image. "
        "Output only the plain text content in reading order, "
        "preserving section headings and bullet points."
    )
    
    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "image": image_path},
            {"type": "text", "text": prompt},
        ],
    }]

    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    
    inputs = processor(
        text=[text], images=image_inputs, videos=video_inputs,
        padding=True, return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=8192)

    generated_ids_trimmed = [
        out[len(inp):] for inp, out in zip(inputs.input_ids, generated_ids)
    ]
    output = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )
    return output[0] if output else ""


def ocr_pdf(pdf_path: str) -> str:
    """Convert each PDF page to image and run dots.mocr on each."""
    from pdf2image import convert_from_path
    import tempfile

    images = convert_from_path(pdf_path, dpi=200)
    parts = []
    for i, img in enumerate(images):
        logger.info(f"[dots.mocr] Processing page {i+1}/{len(images)}...")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name, format="PNG")
            tmp_path = tmp.name
        try:
            page_text = ocr_image(tmp_path)
            parts.append(page_text)
        finally:
            os.unlink(tmp_path)
    return "\n\n".join(parts)
