import os
import sys
import subprocess
import shutil
from typing import Optional

def convert_docx_to_pdf(docx_path: str, output_pdf_path: Optional[str] = None) -> str:
    """
    Converte un file DOCX in PDF preservando al 100% il layout:
    - Metodo 1: Su macOS, usa Microsoft Word nativo via AppleScript (massima fedeltà assoluta).
    - Metodo 2: Se disponibile, usa LibreOffice headless (soffice).
    """
    abs_docx = os.path.abspath(docx_path)
    if not os.path.isfile(abs_docx):
        raise FileNotFoundError(f"File DOCX non trovato: {abs_docx}")

    if not output_pdf_path:
        output_pdf_path = os.path.splitext(abs_docx)[0] + ".pdf"
    abs_pdf = os.path.abspath(output_pdf_path)

    # 1. Prova con Microsoft Word su macOS se disponibile
    if sys.platform == "darwin" and os.path.exists("/Applications/Microsoft Word.app"):
        try:
            # Word accetta il path in formato POSIX o HFS
            applescript = f'''
            tell application "Microsoft Word"
                set myDoc to open (POSIX file "{abs_docx}" as text)
                save as myDoc file name "{abs_pdf}" file format format PDF
                close myDoc saving no
            end tell
            '''
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=45
            )
            if result.returncode == 0 and os.path.isfile(abs_pdf):
                return abs_pdf
            else:
                # Variante alternativa di script Word
                applescript_alt = f'''
                tell application "Microsoft Word"
                    open POSIX file "{abs_docx}"
                    set activeDoc to active document
                    save as activeDoc file name "{abs_pdf}" file format format PDF
                    close activeDoc saving no
                end tell
                '''
                res_alt = subprocess.run(["osascript", "-e", applescript_alt], capture_output=True, text=True, timeout=45)
                if res_alt.returncode == 0 and os.path.isfile(abs_pdf):
                    return abs_pdf
                print(f"[Info] Word AppleScript: {res_alt.stderr.strip() or result.stderr.strip()}")
        except Exception as e:
            print(f"[Info] Word automation fallita ({e}), tentativo LibreOffice...")

    # 2. Prova con LibreOffice (soffice)
    soffice_cmd = shutil.which("soffice")
    if not soffice_cmd and os.path.exists("/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        soffice_cmd = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

    if soffice_cmd:
        out_dir = os.path.dirname(abs_pdf)
        cmd = [soffice_cmd, "--headless", "--convert-to", "pdf", "--outdir", out_dir, abs_docx]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        expected_pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(abs_docx))[0] + ".pdf")
        if os.path.isfile(expected_pdf):
            if expected_pdf != abs_pdf:
                shutil.move(expected_pdf, abs_pdf)
            return abs_pdf

    raise RuntimeError(
        "Nessun convertitore PDF disponibile. Installa LibreOffice (`brew install --cask libreoffice`) "
        "oppure abilita i permessi di automazione per Microsoft Word."
    )
