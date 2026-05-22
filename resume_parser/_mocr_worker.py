"""
_mocr_worker.py – Standalone subprocess worker for dots.mocr inference.

Called by mocr_engine.py via subprocess.run().
Outputs JSON to stdout: {"text": "...", "error": null}

Usage:
    python _mocr_worker.py <image_path> <prompt>
"""

import os
import sys
import json

# Must be set before any tokenizers import
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")

_MODEL_ID = "rednote-hilab/dots.mocr"


def _output(text: str = "", error: str = None):
    print(json.dumps({"text": text, "error": error}), flush=True)


def main():
    if len(sys.argv) < 3:
        _output(error="Usage: _mocr_worker.py <image_path> <prompt>")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2]

    if not os.path.exists(image_path):
        _output(error=f"Image not found: {image_path}")
        sys.exit(1)

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoProcessor
        from qwen_vl_utils import process_vision_info

        # Load processor
        processor = AutoProcessor.from_pretrained(
            _MODEL_ID,
            trust_remote_code=True,
            local_files_only=True,
        )

        # Load model on CPU (MPS causes Metal deadlock with custom-code models)
        model = AutoModelForCausalLM.from_pretrained(
            _MODEL_ID,
            trust_remote_code=True,
            torch_dtype=torch.float32,
            attn_implementation="eager",
            low_cpu_mem_usage=True,
            local_files_only=True,
        )
        model.eval()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {"type": "text",  "text": prompt},
                ],
            }
        ]

        text_input = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = processor(
            text=[text_input],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )

        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=4096,
                do_sample=False,
            )

        generated_ids_trimmed = [
            out_ids[len(in_ids):]
            for in_ids, out_ids in zip(inputs["input_ids"], generated_ids)
        ]

        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )

        result = output_text[0].strip() if output_text else ""
        _output(text=result)

    except Exception as e:
        _output(error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
