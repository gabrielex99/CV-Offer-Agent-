from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class JobAnalysis(BaseModel):
    """Risultato dell'analisi della Job Description eseguita dal Job Analyzer Agent."""
    role_title: str = Field(..., description="Titolo del ruolo/posizione ricercata")
    company_name: Optional[str] = Field(None, description="Nome dell'azienda, se specificato")
    summary: str = Field(..., description="Breve sintesi di ciò che l'azienda cerca e della missione del ruolo")
    hard_skills: List[str] = Field(default_factory=list, description="Hard skills, linguaggi, framework e tool richiesti")
    soft_skills: List[str] = Field(default_factory=list, description="Competenze relazionali, metodologie di lavoro richieste")
    ats_keywords: List[str] = Field(default_factory=list, description="Parole chiave critiche per il superamento dei filtri ATS")
    key_responsibilities: List[str] = Field(default_factory=list, description="Principali responsabilità e obiettivi indicati nella JD")
    experience_level: Optional[str] = Field(None, description="Livello di seniority richiesto (es. Junior, Mid, Senior, Lead)")


class ExperienceOptimization(BaseModel):
    """Ottimizzazione mirata di una singola esperienza lavorativa o progetto."""
    original_company_or_role: str = Field(..., description="Azienda o Ruolo di riferimento nel CV originale")
    optimized_bullets: List[str] = Field(
        ..., 
        description="Nuovi bullet point riscritti con focus su metriche, impatto e parole chiave della JD, senza inventare fatti"
    )
    rationale: str = Field(..., description="Spiegazione di perché sono state apportate queste modifiche")


class GitHubProjectOptimization(BaseModel):
    """Progetto GitHub estratto e ottimizzato come esperienza/progetto per il CV."""
    repo_name: str = Field(..., description="Nome del repository GitHub")
    project_title: str = Field(..., description="Titolo professionale del progetto per il CV")
    tech_stack: List[str] = Field(default_factory=list, description="Tecnologie, librerie e modelli usati (es. Python, LangChain, RAG)")
    bullets: List[str] = Field(default_factory=list, description="Bullet point d'impatto focalizzati sul ruolo target (es. AI Engineer)")
    relevance_reason: str = Field(..., description="Perché questo progetto è altamente rilevante per la posizione richiesta")
    github_url: Optional[str] = Field(None, description="Link al repository GitHub")


class TailoredCVData(BaseModel):
    """Dati del CV riadattati dal CV Tailor Agent."""
    tailored_summary: str = Field(
        ..., 
        description="Profilo professionale (Summary / About Me) riscritto con enfasi sulle priorità della Job Description"
    )
    highlighted_skills: List[str] = Field(
        ..., 
        description="Competenze tecniche e metodologiche riordinate e valorizzate in base ai requisiti dell'offerta"
    )
    experiences: List[ExperienceOptimization] = Field(
        default_factory=list, 
        description="Lista delle esperienze lavorative con bullet point ottimizzati"
    )
    github_projects: List[GitHubProjectOptimization] = Field(
        default_factory=list,
        description="Progetti GitHub selezionati e formattati come esperienze di rilievo per il ruolo (es. AI Engineer)"
    )
    replacements_map: Dict[str, str] = Field(
        default_factory=dict,
        description="Mappa di sostituzioni dirette 'testo_originale' -> 'testo_nuovo' per la modalità in-place"
    )
    match_score_estimate: int = Field(
        default=85, 
        description="Stima percentuale (0-100) di allineamento e copertura delle keyword ATS rispetto alla JD"
    )
    advice_notes: List[str] = Field(
        default_factory=list,
        description="Consigli o note per il candidato su eventuali punti scoperti o da chiarire a colloquio"
    )


class CareerOpportunity(BaseModel):
    """Ruolo o posizione suggerita dall'AI incrociando CV e progetti GitHub."""
    role_title: str = Field(..., description="Titolo della posizione lavorativa consigliata")
    category: str = Field(..., description="Settore / Categoria (es. AI & Machine Learning, Cloud & Infrastructure, Security, Architecture)")
    match_score: int = Field(..., description="Stima di affinità percentuale (0-100)")
    why_you_fit: str = Field(..., description="Spiegazione di perché il candidato è perfetto per questo ruolo")
    unlocked_by_github: List[str] = Field(default_factory=list, description="Progetti GitHub che sbloccano o avvalorano questo ruolo")
    top_skills: List[str] = Field(default_factory=list, description="Competenze chiave richieste dal mercato per questa posizione")
    search_query_suggested: str = Field(..., description="Query di ricerca consigliata per LinkedIn / Indeed")
    sample_jd: str = Field(..., description="Esempio di Job Description per adattare subito il CV")


class CareerDiscoveryResult(BaseModel):
    """Risultato globale dell'analisi di orientamento professionale dell'Agent."""
    candidate_summary: str = Field(..., description="Sintesi del potenziale professionale complessivo del candidato")
    extracted_competencies: List[str] = Field(default_factory=list, description="Tutte le competenze estratte dall'unione di CV e GitHub")
    opportunities: List[CareerOpportunity] = Field(default_factory=list, description="Lista dei ruoli consigliati ordinati per match score")
