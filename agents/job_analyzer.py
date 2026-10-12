import os
import json
from typing import Optional
import litellm
from models.schemas import JobAnalysis

SYSTEM_PROMPT = """Sei un Senior Technical Recruiter e un esperto di sistemi ATS (Applicant Tracking System).
Il tuo obiettivo è analizzare minuziosamente la Job Description fornita ed estrarre tutti i requisiti chiave, le competenze e i criteri di selezione.

Devi restituire ESCLUSIVAMENTE un JSON valido (senza markdown extra, senza ```json) con i seguenti campi:
{
  "role_title": "Titolo del ruolo esatto",
  "company_name": "Nome dell'azienda (o null se non presente)",
  "summary": "Breve sintesi degli obiettivi strategici del ruolo (max 2 frasi)",
  "hard_skills": ["skill1", "skill2", ...],
  "soft_skills": ["soft1", "soft2", ...],
  "ats_keywords": ["keyword1", "keyword2", ...],
  "key_responsibilities": ["responsabilità 1", "responsabilità 2", ...],
  "experience_level": "Junior | Mid | Senior | Lead | Executive"
}
"""

def analyze_job_description(jd_text: str, model: Optional[str] = None) -> JobAnalysis:
    """
    Job Analyzer Agent: Esegue l'analisi semantica della JD ed estrae requisiti ed ATS keywords.
    """
    model_name = model or os.getenv("LLM_MODEL", "gpt-4o")
    
    # Se non ci sono chiavi API configurate, forniamo un'analisi euristica per test immediati
    has_api_key = any(
        os.getenv(k) for k in [
            "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", 
            "AZURE_API_KEY", "GROQ_API_KEY"
        ]
    )
    
    if not has_api_key and not model_name.startswith("ollama/"):
        return _fallback_job_analysis(jd_text)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analizza la seguente Job Description:\n\n{jd_text}"}
    ]

    try:
        response = litellm.completion(
            model=model_name,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"} if "gpt" in model_name else None
        )
        content = response.choices[0].message.content.strip()
        
        # Pulizia backticks se presenti
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()
                
        data = json.loads(content)
        return JobAnalysis(**data)
    except Exception as e:
        print(f"[Warning] Chiamata LLM fallita ({e}). Utilizzo fallback euristico.")
        return _fallback_job_analysis(jd_text)


def _fallback_job_analysis(jd_text: str) -> JobAnalysis:
    """Fallback euristico in assenza di chiavi API per garantire l'esecuzione dei test offline."""
    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
    first_line = lines[0] if lines else "Software Engineer"
    
    # Euristiche semplici per trovare keyword frequenti nel testo
    keywords_candidates = [
        "Python", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "FastAPI", "Django",
        "React", "TypeScript", "SQL", "NoSQL", "PostgreSQL", "CI/CD", "Git", "REST API",
        "Microservices", "TDD", "Agile", "Scrum", "Machine Learning", "LLM", "DevOps"
    ]
    found_skills = [kw for kw in keywords_candidates if kw.lower() in jd_text.lower()]
    if not found_skills:
        found_skills = ["Python", "Problem Solving", "Teamwork", "Git"]
        
    return JobAnalysis(
        role_title=first_line[:60],
        company_name="Azienda Target",
        summary="Ricerca di un professionista con comprovate competenze tecniche e capacità di problem solving.",
        hard_skills=found_skills,
        soft_skills=["Team Collaboration", "Problem Solving", "Proattività", "Agile Mindset"],
        ats_keywords=found_skills + ["Agile", "Cloud", "Architecture"],
        key_responsibilities=[
            "Sviluppo e manutenzione di componenti core",
            "Collaborazione cross-funzionale con team agili",
            "Garantire standard elevati di qualità del codice e testing"
        ],
        experience_level="Mid/Senior"
    )
