import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Carica variabili d'ambiente da .env se presente
load_dotenv()

from utils.jd_fetcher import fetch_job_description
from utils.docx_extractor import extract_docx_content
from agents.job_analyzer import analyze_job_description
from agents.cv_tailor import tailor_cv
from renderers.inplace_replacer import apply_inplace_replacements
from renderers.jinja_replacer import render_jinja_template
from renderers.pdf_exporter import convert_docx_to_pdf

console = Console()

def run_pipeline(
    cv_path: str,
    jd_input: str,
    mode: str = "inplace",
    export_pdf: bool = False,
    output_path: str = None,
    model: str = None,
    github_username: str = None
):
    console.print(Panel.fit("[bold cyan]CV OFFER AGENT[/bold cyan] - Tailoring Intelligente del CV", border_style="cyan"))
    
    # 1. Validazione file CV
    if not os.path.isfile(cv_path):
        console.print(f"[bold red]Errore:[/bold red] File CV non trovato: {cv_path}")
        sys.exit(1)

    # 2. Estrazione JD
    with console.status("[bold green]Recupero ed estrazione Job Description in corso...[/bold green]"):
        jd_text = fetch_job_description(jd_input)

    console.print(f"📄 [green]Job Description acquisita:[/green] {len(jd_text.split())} parole.")

    # 3. Job Analyzer Agent
    with console.status("[bold blue]Job Analyzer Agent: estrazione keyword ATS e requisiti...[/bold blue]"):
        job_analysis = analyze_job_description(jd_text, model=model)

    # Mostra tabella di sintesi requisiti
    table_jd = Table(title=f"Analisi Offerta: {job_analysis.role_title} ({job_analysis.company_name or 'N/D'})")
    table_jd.add_column("Categoria", style="cyan", no_wrap=True)
    table_jd.add_column("Dettagli", style="white")
    table_jd.add_row("Hard Skills", ", ".join(job_analysis.hard_skills[:8]))
    table_jd.add_row("Keywords ATS", ", ".join(job_analysis.ats_keywords[:8]))
    table_jd.add_row("Seniority", job_analysis.experience_level or "Non specificato")
    console.print(table_jd)

    # 4. Estrazione Master CV
    with console.status("[bold magenta]Estrazione contenuti dal Master CV...[/bold magenta]"):
        cv_data = extract_docx_content(cv_path)

    # 5. CV Tailor Agent (con eventuale scansione GitHub per ruoli AI/Tech)
    with console.status("[bold yellow]CV Tailor Agent: analisi progetti GitHub & ottimizzazione...[/bold yellow]"):
        tailored_cv = tailor_cv(
            cv_text=cv_data["full_text"], 
            job_analysis=job_analysis, 
            model=model,
            github_username=github_username
        )

    # Mostra progetti GitHub selezionati se presenti
    if tailored_cv.github_projects:
        table_gh = Table(title="🤖 Progetti GitHub Selezionati & Integrati nel CV")
        table_gh.add_column("Progetto", style="cyan", no_wrap=True)
        table_gh.add_column("Stack & Ruolo", style="green")
        table_gh.add_column("Perché Rilevante", style="white")
        for p in tailored_cv.github_projects:
            table_gh.add_row(p.project_title[:35], ", ".join(p.tech_stack[:4]), p.relevance_reason[:80])
        console.print(table_gh)

    console.print(Panel(
        f"[bold]Match Score ATS Stimato:[/bold] [green]{tailored_cv.match_score_estimate}%[/green]\n\n"
        f"[bold]Nuovo Summary:[/bold]\n{tailored_cv.tailored_summary}\n\n"
        f"[bold]Skills Evidenziate:[/bold] {', '.join(tailored_cv.highlighted_skills[:6])}",
        title="✨ Risultati Ottimizzazione",
        border_style="yellow"
    ))

    # 6. Preparazione path output
    os.makedirs("output", exist_ok=True)
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_role = "".join(c for c in job_analysis.role_title if c.isalnum() or c in (' ', '_', '-')).replace(' ', '_')
        output_path = os.path.join("output", f"CV_Tailored_{sanitized_role}_{timestamp}.docx")

    # 7. Rendering fedele al 100%
    with console.status(f"[bold cyan]Rendering documento ({mode})...[/bold cyan]"):
        if mode == "inplace":
            # Applica le sostituzioni e inserisce la sezione progetti GitHub se presenti
            replacements = dict(tailored_cv.replacements_map)
            count = apply_inplace_replacements(
                input_docx_path=cv_path, 
                output_docx_path=output_path, 
                replacements=replacements,
                github_projects=tailored_cv.github_projects
            )
            console.print(f"🎯 [bold green]In-place Replacement completato:[/bold green] {count} blocchi sostituiti con stili preservati.")
        elif mode == "jinja":
            context = {
                "summary": tailored_cv.tailored_summary,
                "skills": tailored_cv.highlighted_skills,
                "experiences": tailored_cv.experiences,
                "role_target": job_analysis.role_title,
                "company_target": job_analysis.company_name
            }
            render_jinja_template(cv_path, output_path, context)
            console.print("🎯 [bold green]Jinja Template compilato con successo.[/bold green]")
        else:
            raise ValueError(f"Modalità non supportata: {mode}")

    console.print(f"📁 [bold]File DOCX salvato:[/bold] [underline]{output_path}[/underline]")

    # 8. Esportazione PDF opzionale
    if export_pdf:
        with console.status("[bold red]Conversione in PDF in corso (Word / LibreOffice)...[/bold red]"):
            try:
                pdf_path = convert_docx_to_pdf(output_path)
                console.print(f"📕 [bold green]PDF generato:[/bold green] [underline]{pdf_path}[/underline]")
            except Exception as e:
                console.print(f"[bold red]Attenzione:[/bold red] Esportazione PDF non riuscita: {e}")

    console.print("\n[bold green]✅ Processo completato con successo![/bold green]\n")


def main():
    parser = argparse.ArgumentParser(description="CV Offer Agent - Adatta il tuo CV mantenendo la grafica intatta.")
    parser.add_argument("--cv", type=str, default="templates/master_cv.docx", help="Percorso del file master .docx")
    parser.add_argument("--jd", type=str, help="Percorso del file JD, testo o link URL dell'offerta")
    parser.add_argument("--mode", choices=["inplace", "jinja"], default="inplace", help="Modalità di rendering")
    parser.add_argument("--pdf", action="store_true", help="Esporta anche in formato PDF")
    parser.add_argument("--output", type=str, help="Percorso del file DOCX generato")
    parser.add_argument("--model", type=str, help="Modello LLM (es. gpt-4o, gemini/gemini-1.5-pro)")
    parser.add_argument("--github", type=str, default="gabrielex99", help="Username GitHub per estrarre e integrare progetti AI/Tech")
    parser.add_argument("--ui", action="store_true", help="Avvia l'interfaccia grafica Web")

    args = parser.parse_args()

    if args.ui:
        import subprocess
        console.print("[bold cyan]Avvio server Web (FastAPI + React)...[/bold cyan]")
        subprocess.run([sys.executable, "run_app.py"])
        return

    if not args.jd:
        # Se non è specificata JD né UI, suggerisci l'uso
        console.print("[yellow]Nessuna Job Description passata via --jd. Usa --ui per aprire la Web App o specifica --jd.[/yellow]")
        console.print("Esempio di test rapido: [bold]python main.py --jd 'templates/sample_job.txt' --pdf[/bold]")
        return

    run_pipeline(
        cv_path=args.cv,
        jd_input=args.jd,
        mode=args.mode,
        export_pdf=args.pdf,
        output_path=args.output,
        model=args.model,
        github_username=args.github
    )

if __name__ == "__main__":
    main()
