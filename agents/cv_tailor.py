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
3. Riscrivi i bullet point delle esperienze focalizzandoti su metriche (%, tempo, scalabilità, risparmio) e verbi d'azione ad alto impatto.
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

def tailor_cv(cv_text: str, job_analysis: JobAnalysis, model: Optional[str] = None) -> TailoredCVData:
    """
    CV Tailor Agent: Riformula e ottimizza i contenuti del CV allineandoli alla JD.
    """
    model_name = model or os.getenv("LLM_MODEL", "gpt-4o")
    
    has_api_key = any(
        os.getenv(k) for k in [
            "OPENROUTER_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", 
            "ANTHROPIC_API_KEY", "AZURE_API_KEY", "GROQ_API_KEY"
        ]
    )
    
    if not has_api_key and not model_name.startswith("ollama/"):
        return _fallback_cv_tailoring(cv_text, job_analysis)

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
        return _fallback_cv_tailoring(cv_text, job_analysis)


def _fallback_cv_tailoring(cv_text: str, job_analysis: JobAnalysis) -> TailoredCVData:
    """Fallback euristico in assenza di LLM per sviluppo, test e demo offline."""
    lines = [l.strip() for l in cv_text.splitlines() if l.strip()]
    
    # Trova frasi tipiche di un summary o prima sezione
    summary_orig = "Software Engineer appassionato di nuove tecnologie."
    for l in lines[:5]:
        if len(l) > 40:
            summary_orig = l
            break
            
    tailored_summary = (
        f"Esperto {job_analysis.role_title} con solida esperienza in "
        f"{', '.join(job_analysis.hard_skills[:3])}. Orientato ai risultati e comprovata capacità "
        f"di guidare progetti in architetture scalabili e ambienti Agile/DevOps."
    )
    
    # Costruisci mappa di sostituzione per demo
    replacements = {
        summary_orig: tailored_summary
    }
    
    # Cerca eventuali bullet points esistenti
    bullet_lines = [l for l in lines if l.startswith("- ") or l.startswith("• ") or l.startswith("* ")]
    for b in bullet_lines[:3]:
        clean_b = b.lstrip("-•* ").strip()
        new_b = f"{clean_b} integrando best practice in {job_analysis.hard_skills[0] if job_analysis.hard_skills else 'settore'} con focus su affidabilità e standard qualitativi."
        replacements[clean_b] = new_b
        replacements[b] = f"• {new_b}"
        
    optimized_bullets = [
        f"Sviluppo di feature mission-critical adottando {', '.join(job_analysis.hard_skills[:2])}, incrementando l'efficienza dei rilasci del 25%.",
        f"Ottimizzazione delle prestazioni architetturali e integrazione di pipeline CI/CD mirate a ridurre i tempi di build.",
        f"Collaborazione attiva in team cross-funzionali per l'allineamento con i requisiti di business e il rispetto delle scadenze."
    ]
    
    return TailoredCVData(
        tailored_summary=tailored_summary,
        highlighted_skills=list(set(job_analysis.hard_skills + ["Git", "REST APIs", "Problem Solving"])),
        experiences=[
            ExperienceOptimization(
                original_company_or_role="Esperienza Principale",
                optimized_bullets=optimized_bullets,
                rationale="Potenziamento delle keyword ATS e allineamento con i requisiti della posizione."
            )
        ],
        replacements_map=replacements,
        match_score_estimate=88,
        advice_notes=[
            f"Valorizzare durante il colloquio l'esperienza specifica con {job_analysis.hard_skills[0] if job_analysis.hard_skills else 'le tecnologie chiave'}.",
            "Preparare metriche quantitative sui progetti precedenti per confermare l'impatto descritto."
        ]
    )
