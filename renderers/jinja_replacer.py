import os
from typing import Dict, Any
from docxtpl import DocxTemplate

def render_jinja_template(
    template_docx_path: str,
    output_docx_path: str,
    context: Dict[str, Any]
) -> bool:
    """
    Effettua il rendering del documento DOCX compilando i tag Jinja2 ({{ ... }})
    tramite la libreria docxtpl.
    """
    if not os.path.isfile(template_docx_path):
        raise FileNotFoundError(f"Template DOCX non trovato: {template_docx_path}")

    doc = DocxTemplate(template_docx_path)
    doc.render(context)
    doc.save(output_docx_path)
    return True
