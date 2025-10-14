import PyPDF2
from docx import Document
from io import BytesIO

def extract_text_from_pdf(data: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = BytesIO(data)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text if text else "No text extracted from PDF"
    except Exception as e:
        return f"PDF error: {str(e)}"

def extract_text_from_docx(data: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = BytesIO(data)
        doc = Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"DOCX error: {str(e)}"

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    data = uploaded_file.getvalue()

    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(data)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(data)
    else:
        return data.decode("utf-8", errors="ignore")
