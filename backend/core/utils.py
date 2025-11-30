import pdfplumber
import io

def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Extracts text from a PDF file (bytes).
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
