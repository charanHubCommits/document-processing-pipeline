import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def extract_text(file_path):
    text = ""

    try:
        # If PDF → convert to images
        if file_path.lower().endswith(".pdf"):
            images = convert_from_path(file_path)

            for img in images:
                text += pytesseract.image_to_string(img) + "\n"

        else:
            # Normal image
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)

    except Exception as e:
        return str(e)

    return text