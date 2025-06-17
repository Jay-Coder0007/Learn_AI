import os
from tqdm import tqdm
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import warnings
warnings.filterwarnings("ignore")

def save_text(class_dir, subject, text):
    """Save extracted text to file"""
    output_dir = os.path.join("output", class_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{subject}_raw.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def pdf_to_images(pdf_path, dpi=300):
    """Convert PDF pages to images using PyMuPDF"""
    doc = fitz.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        yield img

def extract_with_ocr(pdf_path, languages='mar+eng+hin'):
    """Extract text using Tesseract OCR on PDF pages"""
    full_text = []
    for img in pdf_to_images(pdf_path):
        text = pytesseract.image_to_string(
            img,
            lang=languages,
            config='--psm 6'  # Assume uniform block of text
        )
        full_text.append(text)
    return "\n".join(full_text)

def extract_text_from_pdf(pdf_path):
    """Main extraction function with fallback logic"""
    # First try PyMuPDF's native text extraction
    try:
        with fitz.open(pdf_path) as doc:
            text = "\n".join([page.get_text("text") for page in doc])
            if text.strip() and "�" not in text:
                print("✅ Using PyMuPDF text extraction")
                return text
    except Exception as e:
        print(f"[PyMuPDF] Error: {str(e)}")
    
    # Fallback to OCR if direct extraction fails
    print("⚠️ Falling back to OCR...")
    return extract_with_ocr(pdf_path)

def run_extraction():
    os.makedirs("output", exist_ok=True)
    
    for class_dir in os.listdir("data"):
        class_path = os.path.join("data", class_dir)
        if not os.path.isdir(class_path):
            continue

        pdf_files = [f for f in os.listdir(class_path) if f.endswith(".pdf")]
        for file in tqdm(pdf_files, desc=f"📚 Processing {class_dir}"):
            subject = os.path.splitext(file)[0].replace("_book", "")
            pdf_path = os.path.join(class_path, file)
            
            text = extract_text_from_pdf(pdf_path)
            
            if text.strip():
                save_text(class_dir, subject, text)
                print(f"✅ Extracted: {class_dir}/{subject}")
            else:
                print(f"⚠️ No text found: {pdf_path}")

if __name__ == "__main__":
    # Verify Tesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except EnvironmentError:
        print("Error: Tesseract OCR is not installed or not in your PATH")
        print("Download from https://github.com/UB-Mannheim/tesseract/wiki")
        exit(1)
    
    run_extraction()