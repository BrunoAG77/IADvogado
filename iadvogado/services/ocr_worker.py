from PIL import Image
import pytesseract
import io

# Simple OCR wrapper. For production consider using external OCR services for better accuracy.

def image_bytes_to_text(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    # You can add preprocessing here
    text = pytesseract.image_to_string(image, lang='por')
    return text