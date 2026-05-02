"""
Resume Parser – extracts raw text from PDF, DOCX, TXT, and image files
and performs basic text preprocessing.
Includes OCR fallback for scanned/image-based PDFs with heavy preprocessing.
"""

import os
import re
import string
import logging
import subprocess
import tempfile

import PyPDF2
import docx

logger = logging.getLogger('ResumeParser')
logger.setLevel(logging.DEBUG)


class ResumeParser:
    """Parse resumes from multiple file formats and preprocess the text."""

    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg'}

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def parse(self, file_path: str) -> str:
        """Read a resume file and return cleaned text."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        extractors = {
            '.pdf':  self._extract_pdf,
            '.docx': self._extract_docx,
            '.txt':  self._extract_txt,
            '.png':  self._extract_image,
            '.jpg':  self._extract_image,
            '.jpeg': self._extract_image,
        }
        raw_text = extractors[ext](file_path)
        return self._preprocess(raw_text)

    def parse_bytes(self, file_bytes, filename: str) -> str:
        """Parse resume from in‑memory bytes (used by the web upload)."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: {ext}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=os.path.dirname(os.path.abspath(__file__))) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            return self.parse(tmp_path)
        finally:
            os.unlink(tmp_path)

    # ------------------------------------------------------------------ #
    #  Extractors
    # ------------------------------------------------------------------ #
    @staticmethod
    def _is_real_pdf(path: str) -> bool:
        """Check if file starts with PDF magic bytes (%PDF)."""
        try:
            with open(path, 'rb') as f:
                header = f.read(5)
            return header[:4] == b'%PDF'
        except Exception:
            return False

    @staticmethod
    def _extract_pdf(path: str) -> str:
        fname = os.path.basename(path)

        # --- Detect fake PDFs (images renamed to .pdf) ---
        if not ResumeParser._is_real_pdf(path):
            logger.info(f"[EXTRACTION: FAKE-PDF] '{fname}' — Not a real PDF (missing %PDF header). Treating as image.")
            return ResumeParser._extract_image(path)

        text_parts: list[str] = []
        try:
            with open(path, 'rb') as fh:
                reader = PyPDF2.PdfReader(fh)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            logger.warning(f"[EXTRACTION: PDF-ERROR] '{fname}' — PyPDF2 raised {e}. Falling back to OCR.")
            return ResumeParser._extract_image(path)

        raw_text = '\n'.join(text_parts)

        # --- OCR Fallback Trigger ---
        if len(raw_text.strip()) < 50:
            logger.info(f"[EXTRACTION: OCR] '{fname}' — PyPDF2 returned {len(raw_text.strip())} chars, triggering OCR...")
            try:
                ocr_text = ResumeParser._extract_pdf_ocr(path)
                logger.info(f"[EXTRACTION: OCR ✓] '{fname}' — OCR succeeded, extracted {len(ocr_text.strip())} chars.")
                return ocr_text
            except Exception as e:
                logger.warning(f"[EXTRACTION: OCR ✗] '{fname}' — OCR failed ({e}). Returning partial text.")
                return raw_text

        logger.info(f"[EXTRACTION: STANDARD] '{fname}' — PyPDF2 extracted {len(raw_text.strip())} chars successfully.")
        return raw_text

    @staticmethod
    def _preprocess_image_for_ocr(img):
        """
        Apply heavy preprocessing to maximize Tesseract accuracy:
        RGBA→RGB, grayscale, 3x contrast, sharpening, adaptive binarization.
        """
        from PIL import ImageEnhance, ImageFilter, Image as PILImage

        # Step 1: Flatten RGBA/P transparency to white background
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                bg.paste(img, mask=img.split()[3])
            else:
                bg.paste(img)
            img = bg

        # Step 2: Convert to grayscale
        img = img.convert('L')

        # Step 3: Boost contrast aggressively (3x)
        img = ImageEnhance.Contrast(img).enhance(3.0)

        # Step 4: Sharpen
        img = ImageEnhance.Sharpness(img).enhance(2.0)

        # Step 5: Adaptive binarization (threshold at 140)
        img = img.point(lambda x: 0 if x < 140 else 255, '1')

        return img

    @staticmethod
    def _run_tesseract_on_image(img) -> str:
        """
        Run Tesseract via subprocess on a Pillow Image.
        Bypasses pytesseract's UTF-8 decode bug by reading raw bytes.
        """
        # Save preprocessed image to a temp file in the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=project_dir) as tmp:
            img.save(tmp.name, format='PNG')
            tmp_img_path = tmp.name

        out_base = tmp_img_path + '_out'
        try:
            # Run tesseract CLI: input.png -> output_base.txt
            subprocess.run(
                ['tesseract', tmp_img_path, out_base, '--psm', '3', '-l', 'eng'],
                capture_output=True,
                timeout=60,
            )
            out_file = out_base + '.txt'
            if os.path.exists(out_file):
                with open(out_file, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            return ''
        finally:
            # Clean up temp files
            for f in [tmp_img_path, out_base + '.txt']:
                try:
                    os.unlink(f)
                except OSError:
                    pass

    @staticmethod
    def _extract_image(path: str) -> str:
        """Extract text from a standalone image file (PNG/JPG) using OCR."""
        from PIL import Image as PILImage
        fname = os.path.basename(path)
        logger.info(f"[EXTRACTION: IMAGE-OCR] '{fname}' — Running Tesseract OCR on image...")

        try:
            img = PILImage.open(path)
            preprocessed = ResumeParser._preprocess_image_for_ocr(img)
            text = ResumeParser._run_tesseract_on_image(preprocessed)
            logger.info(f"[EXTRACTION: IMAGE-OCR ✓] '{fname}' — Extracted {len(text.strip())} chars.")
            return text
        except Exception as e:
            logger.warning(f"[EXTRACTION: IMAGE-OCR ✗] '{fname}' — Failed ({e}).")
            return ''

    @staticmethod
    def _extract_pdf_ocr(path: str) -> str:
        """Convert scanned PDF pages to images and run preprocessed OCR on each."""
        from pdf2image import convert_from_path

        images = convert_from_path(path, dpi=300)
        ocr_text_parts = []

        for i, img in enumerate(images):
            preprocessed = ResumeParser._preprocess_image_for_ocr(img)
            page_text = ResumeParser._run_tesseract_on_image(preprocessed)
            ocr_text_parts.append(page_text)

        return '\n'.join(ocr_text_parts)

    @staticmethod
    def _extract_docx(path: str) -> str:
        doc = docx.Document(path)
        return '\n'.join(para.text for para in doc.paragraphs)

    @staticmethod
    def _extract_txt(path: str) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            return fh.read()

    # ------------------------------------------------------------------ #
    #  Preprocessing
    # ------------------------------------------------------------------ #
    @staticmethod
    def _preprocess(text: str) -> str:
        """Lowercase and normalise whitespace without destroying critical punctuation (like C++, Node.js, or 1-3)."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        return text
