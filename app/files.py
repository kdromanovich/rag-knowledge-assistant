from io import BytesIO

from pypdf import PdfReader


def extract_text(filename: str, content_type: str, data: bytes) -> str:
    lower = filename.lower()
    if content_type == "application/pdf" or lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if content_type.startswith("text/") or lower.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="replace").strip()
    raise ValueError("Supported formats: PDF, TXT, Markdown")
