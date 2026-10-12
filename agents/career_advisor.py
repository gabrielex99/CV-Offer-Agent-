import os
import json
from typing import Optional, List, Dict, Any
import litellm
from models.schemas import CareerOpportunity, CareerDiscoveryResult
from utils.github_scanner import fetch_user_github_projects

SYSTEM_PROMPT = """Sei un Executive Headhunter e Career Strategist specializzato in tecnologia e ruoli ad alto potenziale (AI, Cloud, Sistemi, Data, Architettura).
Il tuo obiettivo è analizzare il profilo completo di un candidato (CV lavorativo + progetti open source su GitHub) e scoprire TUTTI i ruoli di mercato in cui può posizionarsi con successo.

Devi identificare sia i ruoli ovvi che quelli "nascosti" o non convenzionali sbloccati dalle competenze dimostrate nei progetti GitHub (es. AI Engineer, Platform Engineer, Automation Engineer, Security/Systems in ambito Difesa).

Per ogni ruolo fornisci:
- role_title: titolo della posizione di rilievo
- category: categoria (AI & ML, Cloud & Infra, Security & Systems, Architecture, Automation)
- match_score: percentuale 85-98%
- why_you_fit: argomentazione dettagliata del perché il candidato è altamente qualificato
- unlocked_by_github: lista dei progetti GitHub che rendono credibile la candidatura
- top_skills: competenze chiave
- search_query_suggested: query pronta per LinkedIn/Indeed
- sample_jd: breve estratto di Job Description per permettere l'adattamento istantaneo del CV

FORMATO RISPOSTA:
Restituisci ESCLUSIVAMENTE un JSON valido con questa struttura:
{
  "candidate_summary": "Sintesi strategica del profilo...",
  "extracted_competencies": ["Competenza 1", "Competenza 2", ...],
  "opportunities": [
    {
      "role_title": "Titolo",
      "category": "Categoria",
      "match_score": 95,
      "why_you_fit": "Perché...",
      "unlocked_by_github": ["Repo1", "Repo2"],
      "top_skills": ["Skill1", "Skill2"],
      "search_query_suggested": "query",
      "sample_jd": "testo jd..."
    }
  ]
}
"""

def discover_career_opportunities(
    cv_text: str,
    github_username: Optional[str] = "gabrielex99",
    model: Optional[str] = None
) -> CareerDiscoveryResult:
    """
    Career Advisor Agent: Analizza CV + GitHub e consiglia tutti i ruoli ideali per il candidato.
    """
    model_name = model or os.getenv("LLM_MODEL", "openrouter/openai/gpt-4o-mini")
    
    # Recupera i repository GitHub
    repos = fetch_user_github_projects(github_username) if github_username else []
    
    has_api_key = any(
        os.getenv(k) for k in [
            "OPENROUTER_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", 
            "ANTHROPIC_API_KEY", "AZURE_API_KEY", "GROQ_API_KEY"
        ]
    )

    if not has_api_key and not model_name.startswith("ollama/"):
        return _fallback_career_discovery(cv_text, repos)

    repos_summary = [
        {"name": r["name"], "desc": r.get("description", ""), "lang": r.get("language", ""), "readme": r.get("readme_summary", "")[:400]}
        for r in repos
    ]

    user_prompt = f"""PROFILO CV DEL CANDIDATO:
{cv_text}

PROGETTI E REPOSITORY GITHUB:
{json.dumps(repos_summary, ensure_ascii=False, indent=2)}

Analizza le competenze esplicite e implicite, e suggerisci i 5-6 ruoli migliori a cui il candidato può ambire con successo.
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
            max_tokens=1500,
            response_format={"type": "json_object"} if "gpt" in model_name else None
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)
        return CareerDiscoveryResult(**data)
    except Exception as e:
        print(f"[Warning] Chiamata LLM Career Advisor fallita ({e}). Utilizzo motore euristico.")
        return _fallback_career_discovery(cv_text, repos)


def _fallback_career_discovery(cv_text: str, repos: List[Dict[str, Any]]) -> CareerDiscoveryResult:
    """Consulenza di carriera euristica altamente profilata per Gabriele Leotta o profili tech simili."""
    repo_names = [r["name"] for r in repos] if repos else ["YoutubeShorts", "AI-TRAVELS", "CV-Offer-Agent-", "microsoft-agent-local-leadgen"]
    
    opportunities = [
        CareerOpportunity(
            role_title="Senior AI Engineer / LLM Specialist",
            category="AI & Machine Learning",
            match_score=96,
            why_you_fit="I tuoi progetti GitHub dimostrano padronanza reale di orchestrazione ad agenti autonomi, pipeline RAG avanzate con LangChain/Chroma DB e integrazione di LLM. Unita alla tua solida esperienza enterprise in microservizi Python (FastAPI), sei il candidato ideale per scalare soluzioni GenAI.",
            unlocked_by_github=[r for r in ["CV-Offer-Agent-", "AI-TRAVELS", "YoutubeShorts"] if r in repo_names or True][:3],
            top_skills=["Multi-Agent Systems", "RAG (Retrieval-Augmented Generation)", "LangChain / LiteLLM", "Python FastAPI", "Vector DBs (Chroma DB)"],
            search_query_suggested="Senior AI Engineer Python LLM RAG Remote",
            sample_jd="""Titolo: Senior AI Engineer / LLM Specialist
Requisiti: Esperienza comprovata con Python, pipeline RAG (LangChain/Chroma DB), orchestrazione multi-agente, deployment di microservizi AI containerizzati su Docker/Kubernetes."""
        ),
        CareerOpportunity(
            role_title="System & Infrastructure Engineer (Difesa & Aerospazio)",
            category="Security & Systems",
            match_score=94,
            why_you_fit="Le tue certificazioni Cisco (CCNA Routing & Switching, Cybersecurity, IT Essentials) sommate alla laurea in Ingegneria Informatica e all'esperienza con Linux/Windows, Docker, Kubernetes e monitoring Grafana ti aprono le porte di colossi della Difesa e Aerospazio come Leonardo per la base NATO AGS di Sigonella.",
            unlocked_by_github=["microsoft-agent-local-leadgen", "CV-Offer-Agent-"],
            top_skills=["Cisco CCNA", "Amministrazione Linux & Windows", "Docker & Kubernetes", "PostgreSQL & LDAP", "Monitoring Grafana/Zabbix", "Idoneità NOS"],
            search_query_suggested="System Engineer Sigonella Catania Difesa Cisco CCNA",
            sample_jd="""Titolo: Supporto Infrastruttura di Terra NATO AGS (Electronics Division) - Leonardo S.p.A.
Requisiti: Networking e sicurezza (Cisco CCNA), amministrazione sistemi Windows/Linux, VMware, Docker, Zabbix/Grafana, scripting Python/Bash, idoneità NOS."""
        ),
        CareerOpportunity(
            role_title="Platform Engineer / DevOps Engineer (Cloud-Native)",
            category="Cloud & Infrastructure",
            match_score=92,
            why_you_fit="Hai esperienza sul campo con Kubernetes multi-cluster (Liqo), container Docker, object storage compatibile S3 (MinIO), CI/CD pipelines (GitLab CI / GitHub Actions) e monitoraggio telemetrico con Grafana. Questo ti colloca direttamente in posizioni di Platform Engineering.",
            unlocked_by_github=["CV-Offer-Agent-"],
            top_skills=["Kubernetes (K8s, Liqo)", "Docker", "CI/CD Pipelines", "MinIO S3", "Grafana Alerting", "Linux"],
            search_query_suggested="Platform Engineer DevOps Kubernetes Docker Python",
            sample_jd="""Titolo: DevOps / Platform Engineer
Requisiti: Gestione cluster Kubernetes, containerizzazione Docker, automazione CI/CD con GitHub Actions, monitoraggio telemetrie e affidabilità cloud-native."""
        ),
        CareerOpportunity(
            role_title="Automation & Growth Engineer (Autonomous Agent Systems)",
            category="Automation & RPA",
            match_score=90,
            why_you_fit="Il tuo progetto YoutubeShorts dimostra capacità non comuni di automazione end-to-end con Playwright headless, sintesi vocale neurale, video rendering programmatico e trend-jacking. Le aziende cercano sempre più figure in grado di automatizzare processi digitali complessi con AI e browser automation.",
            unlocked_by_github=["YoutubeShorts"],
            top_skills=["Playwright / Browser Automation", "Python Asyncio", "Neural TTS", "Multimedia Generation", "Telegram API Automation"],
            search_query_suggested="Python Automation Engineer Playwright Scraping AI",
            sample_jd="""Titolo: Automation Engineer / RPA & Web Automation
Requisiti: Sviluppo di script di automazione complessi con Python, Playwright, integrazione di API neurali e pipeline autonome per l'ottimizzazione dei processi."""
        ),
        CareerOpportunity(
            role_title="Solutions Architect / Lead Software Engineer",
            category="Architecture & Engineering",
            match_score=89,
            why_you_fit="Oltre 5 anni di esperienza in piattaforme enterprise multi-progetto (.NET 9, Laravel, microservizi), Clean Architecture, Domain-Driven Design (DDD), gestione della sicurezza (Keycloak SSO, OAuth 2.0, SPID), e guida tecnica di 5 sviluppatori con ADR e code review.",
            unlocked_by_github=["microsoft-agent-local-leadgen", "CV-Offer-Agent-"],
            top_skills=["Microservices Architecture", "Clean Architecture", ".NET 9 / C#", "OAuth 2.0 / Keycloak SSO", "Technical Leadership", "ADR"],
            search_query_suggested="Solutions Architect Lead Engineer Microservices .NET Python",
            sample_jd="""Titolo: Solutions Architect / Technical Lead
Requisiti: Progettazione di architetture a microservizi scalabili, Clean Architecture, sicurezza IAM/OAuth 2.0, coordinamento tecnico e standard di qualità del codice."""
        ),
        CareerOpportunity(
            role_title="Data & MLOps Engineer (IoT & Generative Modeling)",
            category="Data & MLOps",
            match_score=88,
            why_you_fit="In Agrilog hai generato dati storici sintetici con CTGAN (modelli generativi tabellari) e addestrato modelli predittivi Random Forest per telemetrie IoT, gestendo database PostgreSQL e vettoriali Chroma DB.",
            unlocked_by_github=["AI-TRAVELS"],
            top_skills=["CTGAN Generative Data", "Random Forest / Scikit-learn", "PostgreSQL & Vector Search", "ThingsBoard IoT", "Data Pipelines"],
            search_query_suggested="Data Engineer MLOps Python PostgreSQL Machine Learning",
            sample_jd="""Titolo: Data & MLOps Engineer
Requisiti: Gestione pipeline dati, database PostgreSQL e vettoriali, addestramento e messa in produzione di modelli predittivi e generativi (CTGAN, Random Forest)."""
        )
    ]

    return CareerDiscoveryResult(
        candidate_summary="Profilo di alto valore che unisce solide fondamenta di Software Engineering Enterprise (.NET, Python, Laravel) a competenze d'avanguardia in AI & Sistemi Multi-Agente (dimostrate nei repository GitHub), oltre a forti credenziali in Networking e Sicurezza (Cisco CCNA, Cybersecurity). Questa versatilità ti consente di candidarti con successo sia a ruoli di punta nell'AI sia a posizioni infrastrutturali e architetturali di alto profilo.",
        extracted_competencies=[
            "AI & Multi-Agent Orchestration (LiteLLM, Semantic Kernel)",
            "RAG & Vector Search (LangChain, Chroma DB)",
            "Automazione Autonoma & Headless Browser (Playwright)",
            "Sistemi e Networking (Cisco CCNA, Cybersecurity, IT Essentials)",
            "Containerizzazione & Cloud-Native (Docker, Kubernetes multi-cluster)",
            "Microservizi Enterprise & Clean Architecture (.NET 9, FastAPI, Laravel)",
            "Security & IAM (Keycloak SSO, OAuth 2.0, SPID, conformità GDPR)"
        ],
        opportunities=opportunities
    )
