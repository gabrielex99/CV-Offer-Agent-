# 📄 CV Offer Agent - AI Resume Tailor

> **Adatta automaticamente il tuo CV a qualunque offerta di lavoro, preservando al 100% la grafica, i font, i colori e le tabelle del tuo file `.docx` originale.**

![UI Architecture](https://img.shields.io/badge/Architecture-Agentic%20AI-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Tailwind-indigo)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-teal)

---

## 🌟 Caratteristiche Principali

1. **Invarianza Grafica al 100%**:
   - Non riscrive il file Word alla cieca.
   - Preserva tabelle complesse, layout a 2 o 3 colonne, interlinee, font e colori modificando esclusivamente i testi all'interno dei `Run` di Word.
2. **Architettura ad Agenti Intelligenti**:
   - **Job Analyzer Agent**: Analizza minuziosamente la Job Description estraendo keyword ATS, hard skills, seniority e responsabilità chiave.
   - **CV Tailor Agent**: Riformula bullet points, profilazione (Summary) e competenze senza inventare qualifiche o esperienze fasulle, massimizzando il Match Score ATS.
3. **Interfaccia Web Split-View (React + Tailwind)**:
   - **Sinistra**: Drag & Drop del CV Master (`.docx`) con rilevamento automatico di tabelle e sezioni.
   - **Destra**: Box per incollare la Job Description o link all'annuncio.
   - **In Basso**: Pannello dei **Miglioramenti da fare**:
     - Match Score ATS stimato (es. 88%)
     - Keyword ATS e Hard Skills target individuate
     - Profilo / Summary riscritto
     - Bullet point riformulati con metriche e impatto
     - Consigli strategici per il colloquio
   - **Download Diretto**: Scarica con 1 click il file `.docx` e il `.pdf` esportato ad alta fedeltà.
4. **Supporto Multi-LLM (via LiteLLM / OpenAI SDK)**:
   - OpenAI (`gpt-4o`, `gpt-4o-mini`)
   - Google Gemini (`gemini/gemini-1.5-pro`)
   - Anthropic Claude (`claude-3-5-sonnet`)
   - Modelli locali via Ollama (`ollama/llama3.1`)
5. **Esportazione PDF Integrata**:
   - Esportazione nativa ad alta fedeltà tramite Microsoft Word (su macOS) o LibreOffice headless.

---

## 🏗️ Struttura del Progetto

```
Cv_Offer_Agent/
├── agents/                  # Agenti AI
│   ├── job_analyzer.py      # Estrazione requisiti JD e ATS keywords
│   └── cv_tailor.py         # Ottimizzazione sezioni e bullet point
├── renderers/               # Motori di rendering fedele
│   ├── inplace_replacer.py  # Preserva stili, font, colori nei Run di Word
│   ├── jinja_replacer.py    # Rendering tramite docxtpl (Jinja2)
│   └── pdf_exporter.py      # Conversione in PDF (Word AppleScript / LibreOffice)
├── models/
│   └── schemas.py           # Validazione schemi JSON con Pydantic
├── utils/
│   ├── docx_extractor.py    # Estrazione testo e tabelle dal DOCX
│   └── jd_fetcher.py        # Normalizzazione JD da testo, file o link web
├── api/
│   └── app.py               # Backend FastAPI
├── frontend/                # Web UI React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── App.jsx          # Interfaccia split-view a 2 colonne + pannello inferiore
│   │   └── ...
├── templates/
│   ├── master_cv.docx       # CV Master di esempio (generabile con script)
│   └── sample_job.txt       # Esempio di Job Description per test rapidi
├── output/                  # Cartella dove vengono salvati i CV generati
├── create_sample_cv.py      # Script per creare un CV master di esempio
├── main.py                  # Entrypoint CLI
├── run_app.py               # Avvio rapido interfaccia grafica (FastAPI + React)
├── requirements.txt         # Dipendenze Python
└── .env.example             # Template chiavi API
```

---

## 🚀 Guida Rapida all'Installazione

### 1. Clona il repository e prepara l'ambiente Python
```bash
git clone https://github.com/gabrielex99/CV-Offer-Agent-.git
cd CV-Offer-Agent-

# Crea e attiva il virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Installa le dipendenze Python
pip install -r requirements.txt
```

### 2. Configura le API Key (opzionale se usi la modalità demo offline)
Copia il file di esempio e inserisci la tua chiave:
```bash
cp .env.example .env
```
Nel file `.env`:
```env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
```
*(Se non configuri alcuna chiave, il sistema funziona comunque in modalità euristica offline per farti testare l'intera pipeline e il rendering).*

---

## 💻 Come Avviare l'Interfaccia Grafica Web (React)

Basta lanciare un solo comando:
```bash
python run_app.py
```
Il server si avvierà su **`http://localhost:8000`** e aprirà in automatico il browser.

### Come usare la UI:
1. **A Sinistra**: Carica il tuo CV Master `.docx` (oppure clicca su *"Usa CV Master di Esempio"* in alto a destra).
2. **A Destra**: Incolla la descrizione dell'offerta di lavoro (oppure clicca *"Incolla Esempio"*).
3. **Pulsante Centrale**: Clicca su **"Analizza Offerta & Mostra Miglioramenti"**.
4. **In Basso**: Consulta il punteggio ATS, le keyword individuate, il profilo riscritto e i bullet point ottimizzati.
5. **Generazione**: Seleziona se desideri anche il PDF e clicca **"Applica Miglioramenti & Salva Documento"** per scaricare subito il file.

---

## ⌨️ Uso da Riga di Comando (CLI)

Puoi utilizzare il tool anche direttamente da terminale o in pipeline automatiche:

```bash
# Esecuzione rapida con template e job description di esempio:
python main.py --jd "templates/sample_job.txt" --cv "templates/master_cv.docx" --pdf

# Con una tua offerta specifica:
python main.py --jd "https://link-offerta-di-lavoro..." --cv "templates/mio_cv.docx" --pdf
```

---

## 🎨 Come Preparare il Tuo File DOCX

Il sistema supporta due strategie per preservare al 100% la grafica:

### Approccio A: In-Place Replacement (Zero Modifiche al tuo File)
Non devi cambiare nulla nel tuo file attuale! L'agent:
- Legge i testi attuali (es. il tuo summary o i bullet point delle esperienze).
- Li sostituisce direttamente preservando font, colore, dimensione, grassetto e interlinea del paragrafo originale.

### Approccio B: Placeholder Espliciti
Se preferisci indicare con precisione dove inserire i miglioramenti, puoi inserire nel tuo documento Word dei placeholder come:
- `[[SUMMARY]]` nel riquadro del profilo professionale
- `[[SKILLS]]` nella sezione competenze

Entrambi gli approcci garantiscono che tabelle, intestazioni, colori e margini rimangano intatti al pixel.

---

## 📄 Licenza
Rilasciato sotto licenza MIT.
