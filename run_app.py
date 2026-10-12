import os
import sys
import webbrowser
import time
import uvicorn
from threading import Timer

def open_browser():
    time.sleep(1.2)
    print("🌐 Apertura automatica del browser su http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

def main():
    print("=" * 60)
    print("🚀 Avvio di CV Offer Agent - Web Interface (FastAPI + React)")
    print("=" * 60)
    print("📍 Backend & Web UI disponibili su: http://localhost:8000")
    print("💡 Per arrestare il server premi CTRL + C")
    print("=" * 60)

    # Assicura che esista il template di esempio
    sample_cv = os.path.join("templates", "master_cv.docx")
    if not os.path.isfile(sample_cv):
        from create_sample_cv import create_sample_master_cv
        create_sample_master_cv(sample_cv)

    Timer(1.5, open_browser).start()
    uvicorn.run("api.app:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
