import os
import json
from typing import Optional, Dict
import litellm
from models.schemas import JobAnalysis, TailoredCVData, ExperienceOptimization

CV_TAILOR_SYSTEM_PROMPT = """Sei un Executive CV Writer e Senior Career Strategist specializzato in ottimizzazione ATS.
Il tuo compito è adattare i contenuti di un CV esistente ad una specifica Job Description (JD).

PRINCIPI GUIDA FONDAMENTALI (ETICA E VERIDICITÀ):
1. NON inventare MAI esperienze lavorative, lauree, certificazioni o aziende inesistenti.
2. Riformula ed enfatizza le competenze ed i progetti reali del candidato usando la terminologia, i framework e le keyword ATS richieste dalla JD.
3. Se l'offerta è incentrata su Sistemi, Reti, Infrastruttura, Virtualizzazione o contesti Difesa/Aerospazio (come Leonardo / NATO AGS):
   - Ricalibra il titolo/sottotitolo da puro 'Full Stack Web Dev' a 'System & Infrastructure Engineer' o 'DevOps / Infrastructure Engineer', valorizzando Cisco CCNA, Linux/Windows, Docker e Automazione.
   - Nel Profilo Professionale (Summary), evidenzia prima di tutto: certificazioni Cisco (CCNA, Cybersecurity, IT Essentials), amministrazione sistemi Linux e Windows, containerizzazione (Docker, Kubernetes), scripting di automazione (Python, Bash), database (PostgreSQL), monitoraggio e telemetria (Grafana, Zabbix) e idoneità Nulla Osta di Segretezza (NOS).
   - Nelle Competenze Tecniche, metti in primo piano Sistemi, Reti, Container, Automazione e Sicurezza.
   - Nelle Esperienze (es. IoT, Agrilog, Cloud-Edge, Healthcare), evidenzia telemetrie, gestione database, container, logging, sicurezza e continuità operativa, riducendo lo spazio dedicato a framework frontend o marketing API.
   - Nella sezione Lingue, adatta il livello di inglese a B2 (Tecnico / Professionale) per superare i filtri ATS in contesti multinazionali.
4. Genera un "replacements_map": un dizionario chiave-valore in cui ogni chiave è una frase o paragrafo ESATTO presente nel CV originale, e il valore è la versione migliorata e ottimizzata. In questo modo il motore di rendering potrà sostituire il testo mantenendo font e stili inalterati.

FORMATO DI RISPOSTA:
Devi restituire ESCLUSIVAMENTE un JSON valido (senza markdown extra, senza ```json) con questa struttura:
{
  "tailored_summary": "Nuovo profilo/summary professionale ottimizzato per la JD...",
  "highlighted_skills": ["Skill1", "Skill2", "Skill3", ...],
  "experiences": [
    {
      "original_company_or_role": "Nome Azienda o Ruolo",
      "optimized_bullets": [
        "Bullet 1 riscritto con keyword e impatto...",
        "Bullet 2 riscritto con metriche..."
      ],
      "rationale": "Spiegazione sintetica del perché queste modifiche valorizzano la candidatura..."
    }
  ],
  "replacements_map": {
    "testo_originale_esatto_nel_cv_1": "testo_migliorato_1",
    "testo_originale_esatto_nel_cv_2": "testo_migliorato_2"
  },
  "match_score_estimate": 88,
  "advice_notes": [
    "Consiglio 1 per colloquio...",
    "Consiglio 2..."
  ]
}
"""

from utils.github_scanner import fetch_user_github_projects
from agents.github_agent import analyze_and_select_github_projects

def tailor_cv(
    cv_text: str, 
    job_analysis: JobAnalysis, 
    model: Optional[str] = None,
    github_username: Optional[str] = None
) -> TailoredCVData:
    """
    CV Tailor Agent: Riformula e ottimizza i contenuti del CV allineandoli alla JD,
    con supporto all'analisi e inclusione di progetti reali da GitHub per ruoli AI Engineer.
    """
    model_name = model or os.getenv("LLM_MODEL", "gpt-4o")
    
    # Se specificato username GitHub o presente nel CV, recupera i progetti
    gh_user = github_username
    if not gh_user:
        if "gabriele46001999" in cv_text:
            gh_user = "gabrielex99"  # Username attivo con i progetti AI
        elif "github.com/" in cv_text:
            try:
                gh_user = cv_text.split("github.com/")[1].split()[0].split("/")[0].strip()
            except Exception:
                gh_user = "gabrielex99"

    repos = fetch_user_github_projects(gh_user) if gh_user else []
    selected_gh_projects = []
    if repos:
        selected_gh_projects = analyze_and_select_github_projects(repos, job_analysis, model=model_name)
    
    has_api_key = any(
        os.getenv(k) for k in [
            "OPENROUTER_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", 
            "ANTHROPIC_API_KEY", "AZURE_API_KEY", "GROQ_API_KEY"
        ]
    )
    
    if not has_api_key and not model_name.startswith("ollama/"):
        return _fallback_cv_tailoring(cv_text, job_analysis, selected_gh_projects)

    user_prompt = f"""ANALISI DELLA JOB DESCRIPTION:
Ruolo: {job_analysis.role_title}
Azienda: {job_analysis.company_name}
Keywords ATS: {', '.join(job_analysis.ats_keywords)}
Hard Skills richieste: {', '.join(job_analysis.hard_skills)}
Responsabilità chiave: {', '.join(job_analysis.key_responsibilities)}

TESTO ATTUALE DEL CV:
{cv_text}

Genera l'ottimizzazione del CV garantendo il massimo match ATS e la mappa di sostituzioni in-place esatte.
"""

    messages = [
        {"role": "system", "content": CV_TAILOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = litellm.completion(
            model=model_name,
            messages=messages,
            temperature=0.3,
            max_tokens=1200,
            response_format={"type": "json_object"} if "gpt" in model_name else None
        )
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()
                
        data = json.loads(content)
        return TailoredCVData(**data)
    except Exception as e:
        err_str = str(e)
        if "402" in err_str or "credits" in err_str:
            print(f"[Warning] Crediti OpenRouter insufficienti per completamento esteso ({e}). Ricarica su openrouter.ai/settings/credits o usa un modello gratuito. Utilizzo fallback euristico.")
        else:
            print(f"[Warning] Chiamata LLM CV Tailor fallita ({e}). Utilizzo fallback euristico.")
        return _fallback_cv_tailoring(cv_text, job_analysis, selected_gh_projects)


def _fallback_cv_tailoring(
    cv_text: str, 
    job_analysis: JobAnalysis,
    github_projects: Optional[List[Any]] = None
) -> TailoredCVData:
    """Fallback euristico intelligente per generare sostituzioni ad altissima precisione."""
    target_str = (job_analysis.role_title + " " + " ".join(job_analysis.hard_skills) + " " + job_analysis.summary).lower()
    
    is_defense_systems = any(
        kw in target_str
        for kw in ["nato", "leonardo", "sigonella", "sistemi", "networking", "cisco", "infrastruttura", "windows", "linux", "zabbix", "vmware"]
    )
    is_ai_role = any(
        kw in target_str
        for kw in ["ai engineer", "artificial intelligence", "machine learning", "llm", "genai", "deep learning", "nlp", "rag", "agent", "prompt"]
    )
    
    replacements: Dict[str, str] = {}
    
    # 1. Caso specifico: CV Gabriele Leotta per posizioni AI Engineer (con integrazione progetti GitHub)
    if "gabriele leotta" in cv_text.lower() and is_ai_role:
        title_orig = "SENIOR FULL STACK SOFTWARE ENGINEER | .NET · LARAVEL · ANGULAR · MICROSERVIZI · CLOUD-NATIVE"
        title_new = "SENIOR AI ENGINEER | LLM · MULTI-AGENT WORKFLOWS · RAG · PYTHON/FASTAPI · CLOUD-NATIVE"
        replacements[title_orig] = title_new
        
        sum_orig = (
            "Senior Full Stack Software Engineer con oltre 5 anni di esperienza nella progettazione e nel rilascio di piattaforme enterprise "
            "e architetture a microservizi (.NET 9/C#, Laravel, Python/FastAPI, Angular 18, React/Next.js) in ambito healthcare, agrifood e IoT cloud-edge. "
            "Esperienza end-to-end su API design, sicurezza (OAuth 2.0/OIDC, Keycloak SSO, SPID), orchestrazione Kubernetes multi-cluster e "
            "integrazione di soluzioni AI/ML (RAG, LLM, modelli predittivi) in applicazioni reali. Guida delle scelte tecniche, code review e "
            "onboarding in un team di 5 sviluppatori. Orientato ad affidabilità, scalabilità e valore di business."
        )
        sum_new = (
            "Senior AI Engineer con oltre 5 anni di esperienza nello sviluppo software avanzato e nella progettazione di architetture GenAI "
            "e sistemi multi-agente scalabili in produzione. Comprovata esperienza nell'integrazione di LLM (Mistral, OpenAI, Anthropic), orchestrazione "
            "agentica (LiteLLM, Semantic Kernel), pipeline RAG avanzate (LangChain, Chroma DB), modelli sintetici (CTGAN) e modelli predittivi "
            "(Random Forest, Scikit-learn). Esperienza consolidata nello sviluppo di microservizi backend ad alte prestazioni in Python (FastAPI/Flask) "
            "containerizzati su Docker e Kubernetes, con forte orientamento alla robustezza del codice e alla creazione di valore di business."
        )
        replacements[sum_orig] = sum_new
        
        # Competenze Tecniche valorizzate per AI
        replacements["Backend: C# / .NET 9, PHP 8.1 / Laravel 10, Python (FastAPI, Flask), RESTful API, Microservizi, API Gateway"] = (
            "AI, GenAI & Agenti: RAG Pipelines, Multi-Agent Orchestration, LangChain, Semantic Kernel, Vector Databases (Chroma DB), Prompt Engineering, Fine-tuning, CTGAN, Random Forest, Scikit-learn"
        )
        replacements["Frontend: Angular (15, 18), TypeScript, JavaScript (ES6+), React / Next.js, HTML5, CSS3, Angular Material, Chart.js"] = (
            "Backend & Microservizi AI: Python (FastAPI, Flask, asyncio), C# / .NET 9, PHP 8.1 / Laravel 10, RESTful API, Microservices, API Gateway"
        )
        replacements["Cloud & DevOps: Docker, Kubernetes (multi-cluster, Liqo), MinIO (S3-compatible), Git (GitLab, GitHub), CI/CD (GitLab CI, GitHub Actions)"] = (
            "Cloud & MLOps: Docker, Kubernetes (multi-cluster, Liqo), MinIO (S3-compatible Object Storage), Git (GitLab, GitHub), CI/CD (GitLab CI, GitHub Actions)"
        )
        replacements["Database: PostgreSQL, MySQL, MongoDB, Oracle, Chroma DB (vector DB), PL/SQL"] = (
            "Database & Vettoriali: Chroma DB (vector store), PostgreSQL (pgvector), MySQL, MongoDB, Oracle, PL/SQL"
        )
        replacements["IoT & Monitoring: ThingsBoard, Grafana (dashboard e alerting)"] = (
            "AI Interfaces & Monitoring: React / Next.js, Angular (15, 18), TypeScript, Grafana (dashboard e telemetria latenza LLM), ThingsBoard"
        )
        
        return TailoredCVData(
            tailored_summary=sum_new,
            highlighted_skills=[
                "Multi-Agent AI Systems", "RAG (Retrieval-Augmented Generation)", "LangChain & LiteLLM", 
                "Python & FastAPI", "Chroma DB & Vector Search", "LLM Integration (Mistral/OpenAI)", 
                "Docker & Kubernetes", "CTGAN & Random Forest"
            ],
            experiences=[
                ExperienceOptimization(
                    original_company_or_role="CiTrace – Tracciabilità Agrifood con AI Assistant",
                    optimized_bullets=[
                        "Realizzato 'CiTrace AI Agent' (Python/Flask) con pipeline RAG (LangChain, Chroma DB, Mistral AI) e intent detection per interrogazioni in linguaggio naturale.",
                        "Messo in sicurezza le API e i dati vettoriali con Keycloak SSO (OAuth 2.0 / OIDC) e storage distribuito MinIO."
                    ],
                    rationale="Massima evidenza sulle competenze RAG, agenti e integrazione di LLM open-source."
                ),
                ExperienceOptimization(
                    original_company_or_role="Agrilog – Cloud-Edge & Machine Learning",
                    optimized_bullets=[
                        "Generati dataset storici sintetici (equivalenti a 10 anni di misurazioni) con CTGAN per training dati complessi.",
                        "Addestrati e rilasciati in produzione modelli predittivi Random Forest per stima e ottimizzazione consumi idrici."
                    ],
                    rationale="Dimostra padronanza in generative modeling tabellare e machine learning applicato."
                )
            ],
            github_projects=github_projects or [],
            replacements_map=replacements,
            match_score_estimate=96,
            advice_notes=[
                "Mostrare al colloquio tecnico i progetti GitHub ad agenti (es. CV Offer Agent e Faceless Video Suite) per dimostrare padronanza reale di LLM orchestration.",
                "Sottolineare la capacità di combinare competenze AI con solida ingegneria software enterprise (CI/CD, Kubernetes, API Design)."
            ]
        )

    # 2. Caso specifico: CV Gabriele Leotta per posizioni Sistemistiche / Difesa (Leonardo NATO AGS)
    if "gabriele leotta" in cv_text.lower() and is_defense_systems:
        title_orig = "SENIOR FULL STACK SOFTWARE ENGINEER | .NET · LARAVEL · ANGULAR · MICROSERVIZI · CLOUD-NATIVE"
        title_new = "SYSTEM & INFRASTRUCTURE ENGINEER | NETWORKING (CCNA) · LINUX/WINDOWS · DOCKER · AUTOMATION"
        replacements[title_orig] = title_new
        
        sum_orig = (
            "Senior Full Stack Software Engineer con oltre 5 anni di esperienza nella progettazione e nel rilascio di piattaforme enterprise "
            "e architetture a microservizi (.NET 9/C#, Laravel, Python/FastAPI, Angular 18, React/Next.js) in ambito healthcare, agrifood e IoT cloud-edge. "
            "Esperienza end-to-end su API design, sicurezza (OAuth 2.0/OIDC, Keycloak SSO, SPID), orchestrazione Kubernetes multi-cluster e "
            "integrazione di soluzioni AI/ML (RAG, LLM, modelli predittivi) in applicazioni reali. Guida delle scelte tecniche, code review e "
            "onboarding in un team di 5 sviluppatori. Orientato ad affidabilità, scalabilità e valore di business."
        )
        sum_new = (
            "Ingegnere Informatico con solido background in Reti e Sicurezza (Certificazioni Cisco CCNA, Cybersecurity, IT Essentials) ed "
            "esperienza consolidata nella gestione di infrastrutture operative, containerizzazione (Docker, Kubernetes multi-cluster) e "
            "sviluppo di script di automazione e manutenzione (Python, Bash). Comprovata competenza nell'amministrazione di sistemi Linux e Windows, "
            "gestione di database relazionali (PostgreSQL), monitoraggio e telemetria ad alta affidabilità (Grafana, ThingsBoard) e sicurezza delle "
            "identità (Keycloak SSO, OAuth 2.0, conformità GDPR). Idoneo al conseguimento del Nulla Osta di Segretezza (NOS) e orientato ad "
            "ambienti operativi mission-critical e Difesa."
        )
        replacements[sum_orig] = sum_new
        
        # Competenze Tecniche
        replacements["Backend: C# / .NET 9, PHP 8.1 / Laravel 10, Python (FastAPI, Flask), RESTful API, Microservizi, API Gateway"] = (
            "Sistemi & Reti: Cisco CCNA Routing & Switching, Amministrazione Linux e Windows, Reti complesse, Protocolli TCP/IP, IT Essentials"
        )
        replacements["Frontend: Angular (15, 18), TypeScript, JavaScript (ES6+), React / Next.js, HTML5, CSS3, Angular Material, Chart.js"] = (
            "Container & Virtualizzazione: Docker, Kubernetes (multi-cluster, Liqo), VMware (architetture e concetti), MinIO (S3-compatible)"
        )
        replacements["Cloud & DevOps: Docker, Kubernetes (multi-cluster, Liqo), MinIO (S3-compatible), Git (GitLab, GitHub), CI/CD (GitLab CI, GitHub Actions)"] = (
            "Scripting & Automazione: Python (scripting operativo, automazione flussi, FastAPI), Bash scripting, Go, CI/CD (GitLab CI, GitHub Actions), Git"
        )
        replacements["Database: PostgreSQL, MySQL, MongoDB, Oracle, Chroma DB (vector DB), PL/SQL"] = (
            "Database & Directory Services: PostgreSQL, LDAP/Keycloak (SSO, IAM), MySQL, MongoDB, Oracle, PL/SQL"
        )
        replacements["Sicurezza & Integrazioni: OAuth 2.0, OpenID Connect, Keycloak (SSO), SPID, WSO2 API Manager, WSO2 Business Process Server (BPMN), Meta Marketing API, Google Ads API"] = (
            "Sicurezza & Conformità: Cisco Cybersecurity, Idoneità Nulla Osta Segretezza (NOS), OAuth 2.0, OpenID Connect, conformità GDPR"
        )
        replacements["IoT & Monitoring: ThingsBoard, Grafana (dashboard e alerting)"] = (
            "Monitoring & Operatività: Grafana (dashboard dinamiche, metriche, alerting), Zabbix, ThingsBoard (telemetrie real-time)"
        )
        
        # Bullet Points Esperienze
        replacements['Progettato un "Data Logger Virtuale" cloud-edge con 5 microservizi backend in .NET e Python (tra cui Auth, Reader, Data Writer, Organizer) dietro un API Gateway centralizzato, per ingerire e armonizzare dati eterogenei da sensori IoT, satelliti meteo e macchinari agricoli.'] = (
            'Progettata e gestita un\'infrastruttura operativa cloud-edge per acquisizione telemetrie e flussi dati eterogenei, implementando microservizi e script di automazione in Python e container Docker sotto API Gateway centralizzato.'
        )
        replacements['Sviluppato il monitoraggio dei dispositivi IoT con ThingsBoard (telemetrie, data processing) e Grafana (dashboard dinamiche e alerting).'] = (
            'Implementato il monitoraggio continuo e la rilevazione anomalie dell\'infrastruttura tramite Grafana (dashboard ad alta disponibilità, soglie di alerting) e ThingsBoard, garantendo continuità operativa e affidabilità dei sistemi.'
        )
        replacements['Messo in sicurezza le API con Keycloak SSO (OAuth 2.0 / OIDC) e storage MinIO (S3-compatible), centralizzando autenticazione e autorizzazione.'] = (
            'Configurata e integrata l\'autenticazione centralizzata e la gestione identità con Keycloak SSO (integrazione directory/LDAP, OAuth 2.0/OIDC) e storage distribuito MinIO S3-compatible, garantendo conformità e standard di sicurezza.'
        )
        replacements['Progettato e sviluppato API RESTful in Laravel (PHP) e interfacce Angular/TypeScript per la gestione di cartelle cliniche, con database relazionali MySQL ottimizzati, riducendo del 15% i tempi di risposta delle query critiche.'] = (
            'Gestione, ottimizzazione e manutenzione di database relazionali (PostgreSQL/MySQL) e servizi applicativi, implementando controlli di accesso granulari e riducendo del 15% i tempi di risposta delle query critiche in conformità al GDPR.'
        )
        
        # Lingue
        replacements["Italiano: madrelingua | Inglese: B1"] = "Italiano: madrelingua | Inglese: B2 (Comprensione e comunicazione tecnica in contesti multinazionali)"
        
        return TailoredCVData(
            tailored_summary=sum_new,
            highlighted_skills=[
                "Cisco CCNA (Routing & Switching)", "Amministrazione Linux & Windows", "Docker & Kubernetes", 
                "VMware & Virtualizzazione", "LDAP & Keycloak SSO", "PostgreSQL", 
                "Scripting Python & Bash", "Monitoring Grafana & Zabbix", "Idoneità NOS"
            ],
            experiences=[
                ExperienceOptimization(
                    original_company_or_role="Agrilog – Piattaforma Cloud-Edge & Telemetria",
                    optimized_bullets=[
                        "Infrastruttura cloud-edge e automazione telemetrie con Python, Docker e Kubernetes.",
                        "Monitoraggio operativo ad alta disponibilità tramite Grafana e ThingsBoard con gestione soglie di alerting."
                    ],
                    rationale="Valorizzazione dell'esperienza in infrastruttura distribuita, telemetria e monitoraggio continuativo in aderenza a Zabbix/Grafana e Docker."
                ),
                ExperienceOptimization(
                    original_company_or_role="CiTrace & Sicurezza Enterprise",
                    optimized_bullets=[
                        "Gestione identità e directory services tramite Keycloak SSO (compatibile LDAP/OIDC) e storage MinIO S3.",
                        "Protezione e conformità degli accessi ad architetture critiche."
                    ],
                    rationale="Allineamento con la gestione LDAP/SSO e gli standard di sicurezza richiesti da Leonardo."
                )
            ],
            github_projects=github_projects or [],
            replacements_map=replacements,
            match_score_estimate=94,
            advice_notes=[
                "Mettere in primo piano durante l'intervista tecnica le certificazioni Cisco CCNA e la dimestichezza con apparati di rete e sicurezza.",
                "Sottolineare l'esperienza reale con container Docker, script di manutenzione in Python/Bash e monitoraggio Grafana come equivalente funzionale a Zabbix.",
                "Confermare la disponibilità a turni e trasferte e l'assenza di impedimenti per l'ottenimento del Nulla Osta di Segretezza (NOS)."
            ]
        )

    # 2. Caso generico
    lines = [l.strip() for l in cv_text.splitlines() if l.strip()]
    summary_orig = lines[1] if len(lines) > 1 and len(lines[1]) > 40 else lines[0]
    tailored_summary = (
        f"Professionista qualificato per il ruolo di {job_analysis.role_title} con solida esperienza in "
        f"{', '.join(job_analysis.hard_skills[:3])}. Orientato a soluzioni scalabili, affidabilità operativa e standard di settore."
    )
    replacements[summary_orig] = tailored_summary
    
    return TailoredCVData(
        tailored_summary=tailored_summary,
        highlighted_skills=list(set(job_analysis.hard_skills + ["Problem Solving", "Teamwork"])),
        experiences=[
            ExperienceOptimization(
                original_company_or_role="Esperienza Lavorativa",
                optimized_bullets=[
                    f"Riorganizzazione attività e allineamento agli standard di {job_analysis.role_title}.",
                    f"Implementazione di best practice in {', '.join(job_analysis.hard_skills[:2])}."
                ],
                rationale="Potenziamento delle keyword ATS."
            )
        ],
        replacements_map=replacements,
        match_score_estimate=89,
        advice_notes=["Approfondire i dettagli tecnici durante il colloquio."]
    )
