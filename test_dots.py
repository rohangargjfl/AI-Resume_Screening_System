import os
import sys

# Ensure root is on path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from resume_parser.dots_mocr_provider import ocr_image
from PIL import Image, ImageDraw

def create_test_image():
    img = Image.new('RGB', (400, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10,10), 'Resume\n\nExperience: Software Engineer', fill=(0,0,0))
    img.save('test_ocr.png')

if __name__ == "__main__":
    if not os.path.exists('test_ocr.png'):
        create_test_image()
    print("Testing dots.mocr on test_ocr.png...")
    result = ocr_image('test_ocr.png')
    print("Result:")
    print(result)
