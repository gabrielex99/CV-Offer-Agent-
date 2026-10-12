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


def apply_inplace_replacements(
    input_docx_path: str,
    output_docx_path: str,
    replacements: Dict[str, str]
) -> int:
    """
    Itera su tutti i paragrafi di corpo, tabelle (e relative celle), header e footer,
    applicando il dizionario delle sostituzioni senza alterare la struttura del layout.
    
    Ritorna il numero di sostituzioni effettuate con successo.
    """
    doc = docx.Document(input_docx_path)
    count = 0

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
