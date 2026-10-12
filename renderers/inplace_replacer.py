import docx
from typing import Dict, List, Optional
import copy

def replace_in_paragraph(paragraph, target: str, replacement: str) -> bool:
    """
    Sostituisce 'target' con 'replacement' all'interno di un paragrafo Word,
    preservando rigorosamente font, dimensione, colore, stili e interlinee.
    """
    if target not in paragraph.text:
        return False

    # Caso 1: il target si trova interamente all'interno di un singolo Run
    for run in paragraph.runs:
        if target in run.text:
            run.text = run.text.replace(target, replacement)
            return True

    # Caso 2: il target attraversa più Run (frammentazione tipica di Word)
    # Conserviamo le proprietà del primo Run esistente
    full_text = paragraph.text
    new_full_text = full_text.replace(target, replacement)

    if not paragraph.runs:
        paragraph.text = new_full_text
        return True

    # Se il paragrafo originale ha un'etichetta in grassetto (es. "Backend:") e il replacement ha formato "Nuova Etichetta: Dettagli"
    if ":" in new_full_text and len(paragraph.runs) >= 2 and paragraph.runs[0].bold:
        parts = new_full_text.split(":", 1)
        label_part = parts[0] + ":"
        content_part = parts[1]
        
        # Preserva run[0] per l'etichetta
        paragraph.runs[0].text = label_part
        # Preserva run[1] per il contenuto
        paragraph.runs[1].text = content_part
        for r in paragraph.runs[2:]:
            r.text = ""
        return True

    # Salva le proprietà del primo run
    first_run = paragraph.runs[0]
    font_name = first_run.font.name
    font_size = first_run.font.size
    bold = first_run.bold
    italic = first_run.italic
    underline = first_run.underline
    color = first_run.font.color.rgb if first_run.font.color else None

    # Assegna il testo completo al primo run e svuota i run successivi
    first_run.text = new_full_text
    first_run.font.name = font_name
    if font_size:
        first_run.font.size = font_size
    first_run.bold = bold
    first_run.italic = italic
    first_run.underline = underline
    if color:
        first_run.font.color.rgb = color

    for r in paragraph.runs[1:]:
        r.text = ""

    return True


def insert_github_projects(doc, github_projects: List[Any]) -> bool:
    """
    Inserisce una sezione dedicata ai Progetti GitHub nel documento DOCX,
    preservando lo stile Heading 1 e List Paragraph per integrarsi al 100% con il layout.
    """
    if not github_projects:
        return False

    # Cerca il punto di ancoraggio (es. prima di "Istruzione" o "Certificazioni")
    anchor_paragraph = None
    heading_style = "Heading 1"
    
    for p in doc.paragraphs:
        txt = p.text.strip().lower()
        if txt in ["istruzione", "education", "formazione", "certificazioni", "certifications"]:
            anchor_paragraph = p
            if p.style:
                heading_style = p.style.name
            break

    if not anchor_paragraph and doc.paragraphs:
        anchor_paragraph = doc.paragraphs[-1]

    if not anchor_paragraph:
        return False

    # Inserisce l'intestazione di sezione
    h = anchor_paragraph.insert_paragraph_before("Progetti AI & Soluzioni Open Source (GitHub)", style=heading_style)
    
    # Inserisce ciascun progetto con titolo in grassetto e relative bullet
    for proj in github_projects:
        # Supporta sia Pydantic model che dict
        title = getattr(proj, "project_title", None) or proj.get("project_title") or getattr(proj, "repo_name", "")
        bullets = getattr(proj, "bullets", None) or proj.get("bullets", [])
        
        # Paragrafo Titolo Progetto
        p_title = anchor_paragraph.insert_paragraph_before(style="Normal")
        r_title = p_title.add_run(title)
        r_title.bold = True
        
        # Bullet points
        for b in bullets:
            p_b = anchor_paragraph.insert_paragraph_before(style="List Paragraph")
            r_b = p_b.add_run(f"• {b}")

    return True


def apply_inplace_replacements(
    input_docx_path: str,
    output_docx_path: str,
    replacements: Dict[str, str],
    github_projects: Optional[List[Any]] = None
) -> int:
    """
    Itera su tutti i paragrafi di corpo, tabelle (e relative celle), header e footer,
    applicando il dizionario delle sostituzioni ed eventuale inserimento progetti GitHub
    senza alterare la struttura del layout.
    
    Ritorna il numero di sostituzioni effettuate con successo.
    """
    doc = docx.Document(input_docx_path)
    count = 0

    # Inserimento progetti GitHub se forniti
    if github_projects:
        insert_github_projects(doc, github_projects)

    # 1. Paragrafi principali del documento
    for p in doc.paragraphs:
        for target, replacement in replacements.items():
            if replace_in_paragraph(p, target, replacement):
                count += 1

    # 2. Celle di tutte le tabelle
    def process_table(table):
        nonlocal count
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for target, replacement in replacements.items():
                        if replace_in_paragraph(p, target, replacement):
                            count += 1
                # Supporto a tabelle annidate
                for nested_table in cell.tables:
                    process_table(nested_table)

    for table in doc.tables:
        process_table(table)

    # 3. Header e Footer di tutte le sezioni
    for section in doc.sections:
        for header_p in section.header.paragraphs:
            for target, replacement in replacements.items():
                if replace_in_paragraph(header_p, target, replacement):
                    count += 1
        for footer_p in section.footer.paragraphs:
            for target, replacement in replacements.items():
                if replace_in_paragraph(footer_p, target, replacement):
                    count += 1

    doc.save(output_docx_path)
    return count
