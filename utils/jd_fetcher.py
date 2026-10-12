import os
import re
import requests
from bs4 import BeautifulSoup

def fetch_job_description(source: str) -> str:
    """
    Estrae e normalizza il testo della Job Description.
    Supporta:
    - URL (es. https://...)
    - File path locale (.txt, .md, .docx)
    - Testo grezzo passato direttamente
    """
    source_clean = source.strip()
    
    # Caso 1: URL HTTP/HTTPS
    if source_clean.startswith("http://") or source_clean.startswith("https://"):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(source_clean, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Rimuove script, style e tag non pertinenti
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()
            
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
        
    # Caso 2: File locale esistente
    if os.path.isfile(source_clean):
        ext = os.path.splitext(source_clean)[1].lower()
        if ext in [".txt", ".md"]:
            with open(source_clean, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".docx":
            import docx
            doc = docx.Document(source_clean)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        else:
            with open(source_clean, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
                
    # Caso 3: Testo grezzo inserito via CLI
    return source_clean
