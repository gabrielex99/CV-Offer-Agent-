import os
import shutil
import uuid
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from utils.jd_fetcher import fetch_job_description
from utils.docx_extractor import extract_docx_content
from agents.job_analyzer import analyze_job_description
from agents.cv_tailor import tailor_cv
from renderers.inplace_replacer import apply_inplace_replacements
from renderers.jinja_replacer import render_jinja_template
from renderers.pdf_exporter import convert_docx_to_pdf
from models.schemas import JobAnalysis, TailoredCVData

app = FastAPI(title="CV Offer Agent API", version="1.0.0")

# Abilita CORS per il frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.abspath("templates")
OUTPUT_DIR = os.path.abspath("output")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


class AnalyzeJDRequest(BaseModel):
    jd_input: str
    model: Optional[str] = None


class TailorRequest(BaseModel):
    cv_text: str
    job_analysis: JobAnalysis
    model: Optional[str] = None


class GenerateRequest(BaseModel):
    cv_filename: str
    replacements: Dict[str, str]
    mode: str = "inplace"
    export_pdf: bool = False
    context: Optional[Dict[str, Any]] = None


@app.get("/api/status")
def get_status():
    has_api_key = any(
        os.getenv(k) for k in [
            "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", 
            "AZURE_API_KEY", "GROQ_API_KEY"
        ]
    )
    master_cv_exists = os.path.isfile(os.path.join(UPLOAD_DIR, "master_cv.docx"))
    return {
        "status": "online",
        "has_api_key": has_api_key,
        "default_model": os.getenv("LLM_MODEL", "gpt-4o"),
        "has_sample_master": master_cv_exists
    }


@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Solo file .docx sono supportati")

    # Genera un nome file univoco preservando il nome originale
    clean_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, clean_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Estrae il contenuto
    extracted = extract_docx_content(file_path)
    return {
        "filename": clean_name,
        "original_name": file.filename,
        "full_text": extracted["full_text"],
        "paragraphs_count": len(extracted["paragraphs"]),
        "tables_count": len(extracted["tables"])
    }


@app.get("/api/load-sample-cv")
def load_sample_cv():
    sample_path = os.path.join(UPLOAD_DIR, "master_cv.docx")
    if not os.path.isfile(sample_path):
        from create_sample_cv import create_sample_master_cv
        create_sample_master_cv(sample_path)

    extracted = extract_docx_content(sample_path)
    return {
        "filename": "master_cv.docx",
        "original_name": "master_cv.docx (Esempio Integrato)",
        "full_text": extracted["full_text"],
        "paragraphs_count": len(extracted["paragraphs"]),
        "tables_count": len(extracted["tables"])
    }


@app.post("/api/analyze-jd", response_model=JobAnalysis)
def analyze_jd(req: AnalyzeJDRequest):
    jd_clean = fetch_job_description(req.jd_input)
    analysis = analyze_job_description(jd_clean, model=req.model)
    return analysis


@app.post("/api/tailor", response_model=TailoredCVData)
def run_tailor(req: TailorRequest):
    result = tailor_cv(req.cv_text, req.job_analysis, model=req.model)
    return result


@app.post("/api/generate-docx")
def generate_docx(req: GenerateRequest):
    src_path = os.path.join(UPLOAD_DIR, req.cv_filename)
    if not os.path.isfile(src_path):
        raise HTTPException(status_code=404, detail="File master CV non trovato sul server")

    unique_id = uuid.uuid4().hex[:8]
    base_name = f"CV_Tailored_{unique_id}.docx"
    dest_path = os.path.join(OUTPUT_DIR, base_name)

    if req.mode == "inplace":
        count = apply_inplace_replacements(src_path, dest_path, req.replacements)
    elif req.mode == "jinja":
        render_jinja_template(src_path, dest_path, req.context or {})
    else:
        raise HTTPException(status_code=400, detail="Modalità sconosciuta")

    pdf_name = None
    if req.export_pdf:
        try:
            pdf_path = convert_docx_to_pdf(dest_path)
            pdf_name = os.path.basename(pdf_path)
        except Exception as e:
            print(f"[Warning] PDF generation error: {e}")

    return {
        "docx_filename": base_name,
        "docx_download_url": f"/api/download/{base_name}",
        "pdf_filename": pdf_name,
        "pdf_download_url": f"/api/download/{pdf_name}" if pdf_name else None
    }


@app.get("/api/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File non trovato")
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )


# Serve frontend React build se disponibile
FRONTEND_DIST = os.path.abspath("frontend/dist")
if os.path.isdir(FRONTEND_DIST):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")

