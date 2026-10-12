import os
import json
from typing import List, Dict, Any, Optional
import litellm
from models.schemas import JobAnalysis, GitHubProjectOptimization

SYSTEM_PROMPT = """Sei un Senior AI Talent Lead e Technical Recruiter specializzato in ruoli AI Engineer, Machine Learning Engineer e Full Stack AI.
Il tuo compito è analizzare i repository GitHub di un candidato e selezionare i 2-3 progetti più rilevanti e impattanti per una specifica Job Description (JD).

Per ogni progetto selezionato devi:
1. Riformulare il titolo per un CV enterprise (es. "Autonomous AI Video Automation Suite" o "Multi-Agent System for Document Tailoring").
2. Sintetizzare lo stack tecnologico (es. Python, Playwright, LLM, Neural TTS, RAG, Semantic Kernel).
3. Redigere 2 bullet point ad alto impatto tecnico con verbi d'azione e metriche architetturali.
4. Spiegare sinteticamente perché il progetto è rilevante per la posizione (relevance_reason).

FORMATO RISPOSTA:
Restituisci ESCLUSIVAMENTE un JSON valido (array di oggetti) con questa struttura:
[
  {
    "repo_name": "nome_repo_originale",
    "project_title": "Titolo Professionale Progetto | Stack",
    "tech_stack": ["Python", "LLM", "Docker"],
    "bullets": [
      "Progettata e sviluppata pipeline autonoma per...",
      "Integrati modelli di intelligenza artificiale..."
    ],
    "relevance_reason": "Dimostra padronanza in architetture ad agenti e orchestrazione LLM...",
    "github_url": "https://github.com/utente/repo"
  }
]
"""

def analyze_and_select_github_projects(
    repos: List[Dict[str, Any]], 
    job_analysis: JobAnalysis, 
    model: Optional[str] = None
) -> List[GitHubProjectOptimization]:
    """
    Seleziona ed elabora i repository GitHub più pertinenti alla Job Description per arricchire il CV.
    """
    if not repos:
        return []

    model_name = model or os.getenv("LLM_MODEL", "openrouter/openai/gpt-4o-mini")
    
    has_api_key = any(
        os.getenv(k) for k in [
            "OPENROUTER_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", 
            "ANTHROPIC_API_KEY", "AZURE_API_KEY", "GROQ_API_KEY"
        ]
    )

    if not has_api_key and not model_name.startswith("ollama/"):
        return _fallback_github_selection(repos, job_analysis)

    # Prepara riassunto dei repo disponibili
    repos_summary = []
    for r in repos:
        repos_summary.append({
            "name": r["name"],
            "description": r.get("description", ""),
            "language": r.get("language", ""),
            "topics": r.get("topics", []),
            "readme_excerpt": r.get("readme_summary", "")[:500],
            "url": r.get("html_url", "")
        })

    user_prompt = f"""JOB DESCRIPTION TARGET:
Ruolo: {job_analysis.role_title}
Azienda: {job_analysis.company_name}
Keywords ATS: {', '.join(job_analysis.ats_keywords)}
Hard Skills richieste: {', '.join(job_analysis.hard_skills)}
Sintesi: {job_analysis.summary}

REPOSITORY GITHUB DISPONIBILI DEL CANDIDATO:
{json.dumps(repos_summary, ensure_ascii=False, indent=2)}

Seleziona e ottimizza i progetti più in linea per questa offerta di lavoro (massimo 3).
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = litellm.completion(
            model=model_name,
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"} if "gpt" in model_name else None
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)
        # Se restituito come oggetto con chiave wrapper
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    data = v
                    break
        return [GitHubProjectOptimization(**item) for item in data]
    except Exception as e:
        print(f"[Warning] LLM selection GitHub fallita ({e}). Utilizzo euristica.")
        return _fallback_github_selection(repos, job_analysis)


def _fallback_github_selection(
    repos: List[Dict[str, Any]], 
    job_analysis: JobAnalysis
) -> List[GitHubProjectOptimization]:
    """Selezione euristica intelligente per profili AI Engineer o generici."""
    selected = []
    
    # Identifica parole chiave nei repo
    for r in repos:
        name = r["name"]
        name_lower = name.lower()
        desc_lower = (r.get("description") or "").lower()
        readme_lower = (r.get("readme_summary") or "").lower()
        full_text = f"{name_lower} {desc_lower} {readme_lower}"

        # Caso YoutubeShorts
        if "youtubeshorts" in name_lower or "faceless" in full_text:
            selected.append(GitHubProjectOptimization(
                repo_name=name,
                project_title="Faceless AI Video Automation Suite | Python, Playwright, Neural TTS, LLM",
                tech_stack=["Python", "Playwright", "Neural TTS", "LLM Scripting", "Video Rendering", "Telegram API"],
                bullets=[
                    "Progettata un'architettura autonoma per il trend-jacking e la sintesi neurale vocale, con montaggio video automatizzato e delivery multi-piattaforma.",
                    "Integrata pipeline di prompting avanzato per generazione script ad alta ritenzione e automazione headless dei flussi tramite Playwright."
                ],
                relevance_reason="Dimostra capacità avanzate di automazione AI end-to-end, sintesi multimodale (audio/video) e scripting Python.",
                github_url=r.get("html_url")
            ))

        # Caso Travel Planner / AI-TRAVELS
        elif "travel" in name_lower or "travel" in full_text:
            selected.append(GitHubProjectOptimization(
                repo_name=name,
                project_title="AI Travel Planner & Itinerary Engine | Full-Stack LLM Assistant",
                tech_stack=["Python", "FastAPI", "LLM", "Prompt Engineering", "JSON Structured Output"],
                bullets=[
                    "Sviluppata una piattaforma di pianificazione viaggi guidata da LLM in grado di generare itinerari personalizzati dinamici basati su budget, date e preferenze.",
                    "Implementata validazione strutturata degli output tramite schemi rigorosi e ottimizzazione delle chiamate API per massimizzare la velocità di risposta."
                ],
                relevance_reason="Mostra padronanza nell'integrazione di LLM in applicazioni utente reali con output strutturato e logiche di business.",
                github_url=r.get("html_url")
            ))

        # Caso CV Offer Agent
        elif "cv-offer" in name_lower or "cv" in name_lower:
            selected.append(GitHubProjectOptimization(
                repo_name=name,
                project_title="CV Offer Agent — Multi-Agent AI Resume Tailoring System",
                tech_stack=["Python", "Multi-Agent AI", "LiteLLM", "python-docx", "FastAPI", "React"],
                bullets=[
                    "Architettato un sistema multi-agente per analisi semantica ATS delle offerte di lavoro e ottimizzazione mirata dei contenuti professionali.",
                    "Implementato motore di rendering AST per documenti Word DOCX in grado di garantire il 100% dell'invarianza grafica e tipografica."
                ],
                relevance_reason="Eccellente esempio di architettura ad agenti cooperanti, prompt engineering specializzato e manipolazione documentale complessa.",
                github_url=r.get("html_url")
            ))

        # Caso Microsoft Agent Local Leadgen
        elif "agent" in name_lower or "leadgen" in name_lower:
            selected.append(GitHubProjectOptimization(
                repo_name=name,
                project_title="Autonomous Agentic Web Audit & Lead Pipeline | .NET 9, Clean Architecture",
                tech_stack=[".NET 9", "C# 13", "Agentic Workflows", "Clean Architecture", "REST API"],
                bullets=[
                    "Implementato agente autonomo enterprise per audit tecnico multi-parametro e scouting proattivo con pattern Clean/Onion Architecture.",
                    "Sviluppata pipeline di generazione autonoma di reportistica e bozze di outreach per clienti PMI."
                ],
                relevance_reason="Conferma la capacità di progettare architetture ad agenti anche in ambiente enterprise C# / .NET.",
                github_url=r.get("html_url")
            ))

    # Limita a 2-3 progetti top
    return selected[:3]
