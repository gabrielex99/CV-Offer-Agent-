import React, { useState, useEffect } from 'react';
import { 
  Upload, FileText, Sparkles, CheckCircle2, AlertCircle, 
  ArrowRight, Download, RefreshCw, FileCheck, Layers, Cpu, ShieldCheck
} from 'lucide-react';

export default function App() {
  // Stati di input
  const [cvFile, setCvFile] = useState(null);
  const [cvInfo, setCvInfo] = useState(null);
  const [jdText, setJdText] = useState('');
  const [isUploadingCv, setIsUploadingCv] = useState(false);

  // Stati di elaborazione agenti
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState('');
  const [jobAnalysis, setJobAnalysis] = useState(null);
  const [tailoredData, setTailoredData] = useState(null);

  // Stati generazione e download
  const [isGenerating, setIsGenerating] = useState(false);
  const [exportPdf, setExportPdf] = useState(true);
  const [generatedFiles, setGeneratedFiles] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  // Controlla lo stato del server all'avvio
  useEffect(() => {
    fetch('/api/status')
      .then(res => res.json())
      .then(data => setSystemStatus(data))
      .catch(() => setSystemStatus({ status: 'offline', has_api_key: false }));
  }, []);

  // Upload file CV DOCX
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.endsWith('.docx')) {
      setErrorMsg('Per favore carica un file in formato Word (.docx)');
      return;
    }
    setErrorMsg(null);
    setIsUploadingCv(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload-cv', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Errore durante il caricamento del file');
      const data = await res.json();
      setCvFile(data.filename);
      setCvInfo(data);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsUploadingCv(false);
    }
  };

  // Carica CV di esempio integrato
  const handleLoadSampleCv = async () => {
    setIsUploadingCv(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/load-sample-cv');
      const data = await res.json();
      setCvFile(data.filename);
      setCvInfo(data);
    } catch (err) {
      setErrorMsg('Impossibile caricare il CV di esempio');
    } finally {
      setIsUploadingCv(false);
    }
  };

  // Incolla JD di esempio
  const handleLoadSampleJd = () => {
    setJdText(`Titolo: Senior Cloud & Backend Engineer
Azienda: FinTech Global Services
Requisiti Chiave:
- 4-5 anni di esperienza con Python (FastAPI, asyncio)
- Forte esperienza con Docker, Kubernetes (EKS/GKE)
- Database distribuiti: PostgreSQL e Redis caching
- Pipeline CI/CD con GitHub Actions e Terraform
- Metodologia Agile/Scrum e orientamento all'affidabilità mission-critical.`);
  };

  // Flusso agentico di analisi e tailoring
  const handleAnalyzeAndTailor = async () => {
    if (!cvFile || !cvInfo) {
      setErrorMsg('Carica prima il tuo CV in formato .docx nella colonna di sinistra');
      return;
    }
    if (!jdText.trim()) {
      setErrorMsg("Incolla la Job Description dell'offerta nella colonna di destra");
      return;
    }

    setErrorMsg(null);
    setIsAnalyzing(true);
    setGeneratedFiles(null);

    try {
      // Step 1: Job Analyzer Agent
      setAnalysisStep('1/2: Job Analyzer Agent estrae keyword ATS e requisiti...');
      const jdRes = await fetch('/api/analyze-jd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jd_input: jdText }),
      });
      if (!jdRes.ok) throw new Error("Errore durante l'analisi della Job Description");
      const jdData = await jdRes.json();
      setJobAnalysis(jdData);

      // Step 2: CV Tailor Agent
      setAnalysisStep('2/2: CV Tailor Agent ottimizza bullet point ed esperienze...');
      const tailorRes = await fetch('/api/tailor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cv_text: cvInfo.full_text,
          job_analysis: jdData,
        }),
      });
      if (!tailorRes.ok) throw new Error("Errore durante l'ottimizzazione del CV");
      const tailorResult = await tailorRes.json();
      setTailoredData(tailorResult);

    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsAnalyzing(false);
      setAnalysisStep('');
    }
  };

  // Generazione del documento finale DOCX + PDF
  const handleGenerateDocument = async () => {
    if (!cvFile || !tailoredData) return;
    setIsGenerating(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/generate-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cv_filename: cvFile,
          replacements: tailoredData.replacements_map || {},
          mode: 'inplace',
          export_pdf: exportPdf,
        }),
      });
      if (!res.ok) throw new Error('Errore durante la compilazione del documento');
      const data = await res.json();
      setGeneratedFiles(data);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* HEADER */}
        <header className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-500/20">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  CV Offer Agent
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-900/60 text-indigo-300 border border-indigo-700/50">
                    Layout Preserving 100%
                  </span>
                </h1>
                <p className="text-sm text-slate-400">
                  Adatta il tuo CV a qualunque offerta con agenti AI, mantenendo grafica, font e tabelle perfettamente intatti.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {systemStatus && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
                <span className={`w-2 h-2 rounded-full ${systemStatus.status === 'online' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                <span className="text-slate-400">Model:</span>
                <span className="font-semibold text-slate-200">{systemStatus.default_model || 'gpt-4o'}</span>
              </div>
            )}
            <button
              onClick={handleLoadSampleCv}
              className="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
            >
              Usa CV Master di Esempio
            </button>
          </div>
        </header>

        {/* MESSAGGIO ERRORE */}
        {errorMsg && (
          <div className="p-4 bg-red-950/60 border border-red-800/80 rounded-xl text-red-200 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* GRIGLIA PRINCIPALE A 2 COLONNE: CV (A SINISTRA) | OFFERTA (A DESTRA) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* COLONNA SINISTRA: CV MASTER (.DOCX) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-blue-500/20 text-blue-400 rounded-lg">
                    <FileText className="w-5 h-5" />
                  </div>
                  <h2 className="text-lg font-semibold text-white">1. Il tuo CV Master</h2>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2.5 py-1 rounded-full">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Stile & Tabelle Protetti</span>
                </div>
              </div>

              {/* Upload Box */}
              {!cvInfo ? (
                <label className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition bg-slate-950/40 group">
                  <input
                    type="file"
                    accept=".docx"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <div className="p-4 bg-slate-800 group-hover:bg-indigo-600/20 rounded-full mb-3 text-slate-400 group-hover:text-indigo-400 transition">
                    <Upload className="w-7 h-7" />
                  </div>
                  <p className="text-sm font-medium text-slate-200">
                    {isUploadingCv ? 'Caricamento ed estrazione in corso...' : 'Trascina o clicca per caricare il tuo CV .docx'}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Solo formato Word (.docx). La grafica non verrà modificata.
                  </p>
                </label>
              ) : (
                <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-lg border border-indigo-800/50">
                        <FileCheck className="w-6 h-6" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-200 text-sm truncate max-w-[240px]">
                          {cvInfo.original_name}
                        </h4>
                        <p className="text-xs text-slate-400">
                          {cvInfo.paragraphs_count} paragrafi • {cvInfo.tables_count} tabelle rilevate
                        </p>
                      </div>
                    </div>
                    <label className="text-xs text-indigo-400 hover:text-indigo-300 cursor-pointer font-medium">
                      Cambia
                      <input type="file" accept=".docx" onChange={handleFileUpload} className="hidden" />
                    </label>
                  </div>

                  {/* Anteprima estratta */}
                  <div className="bg-slate-900 rounded-lg p-3 max-h-48 overflow-y-auto text-xs text-slate-300 font-mono whitespace-pre-line border border-slate-800">
                    {cvInfo.full_text.slice(0, 500)}...
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-slate-500" />
                Compatibile con tabelle a 2 colonne, colonne multiple ed icone
              </span>
            </div>
          </div>

          {/* COLONNA DESTRA: JOB DESCRIPTION */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-purple-500/20 text-purple-400 rounded-lg">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <h2 className="text-lg font-semibold text-white">2. Job Description</h2>
                </div>
                <button
                  onClick={handleLoadSampleJd}
                  className="text-xs text-purple-400 hover:text-purple-300 font-medium"
                >
                  Incolla Esempio
                </button>
              </div>

              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Incolla qui il testo dell'offerta di lavoro (o link URL dell'annuncio)..."
                rows={10}
                className="w-full bg-slate-950/60 border border-slate-800 focus:border-purple-500 rounded-xl p-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none transition resize-none"
              />
            </div>

            <div className="mt-4 pt-4 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
              <span>{jdText ? `${jdText.trim().split(/\s+/).length} parole` : 'Nessun testo'}</span>
              <span className="text-slate-500">Supporta testo libero, elenchi puntati o link URL</span>
            </div>
          </div>

        </div>

        {/* PULSANTE CENTRALE DI AZIONE */}
        <div className="flex flex-col items-center justify-center pt-2">
          <button
            onClick={handleAnalyzeAndTailor}
            disabled={isAnalyzing || !cvFile || !jdText.trim()}
            className={`flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-base shadow-xl transition transform active:scale-95 ${
              isAnalyzing || !cvFile || !jdText.trim()
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white hover:opacity-95 shadow-indigo-600/25'
            }`}
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>{analysisStep || 'Analisi ed elaborazione in corso...'}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Analizza Offerta & Mostra Miglioramenti</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>

        {/* PANNELLO IN BASSO: I MIGLIORAMENTI DA FARE */}
        {tailoredData && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-2xl animate-fade-in">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2.5">
                  <Sparkles className="w-6 h-6 text-yellow-400" />
                  Miglioramenti Proposti dall'Agent per questa Offerta
                </h3>
                <p className="text-sm text-slate-400 mt-1">
                  Ecco come l'agent ha ottimizzato il tuo CV per massimizzare il punteggio ATS senza inventare qualifiche.
                </p>
              </div>

              {/* Match Score Badge */}
              <div className="flex items-center gap-4 bg-slate-950 px-5 py-3 rounded-xl border border-slate-800">
                <div className="text-right">
                  <div className="text-xs text-slate-400 font-medium">ATS Match Score</div>
                  <div className="text-2xl font-black text-emerald-400">
                    {tailoredData.match_score_estimate}%
                  </div>
                </div>
                <div className="w-12 h-12 rounded-full border-4 border-emerald-500/30 border-t-emerald-400 flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                </div>
              </div>
            </div>

            {/* Keyword e Hard Skills individuate */}
            {jobAnalysis && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Hard Skills Target Identificate dalla JD
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {jobAnalysis.hard_skills.map((s, idx) => (
                      <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-indigo-950/80 text-indigo-300 border border-indigo-800/60">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Keyword ATS Chiave Valorizzate nel CV
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {jobAnalysis.ats_keywords.map((kw, idx) => (
                      <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-purple-950/80 text-purple-300 border border-purple-800/60">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Profilo / Summary Ottimizzato */}
            <div className="bg-slate-950/60 p-5 rounded-xl border border-slate-800/80 space-y-2">
              <h4 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Profilo Professionale (Summary) Riscritto & Allineato
              </h4>
              <p className="text-sm text-slate-300 leading-relaxed bg-slate-900 p-4 rounded-lg border border-slate-800">
                {tailoredData.tailored_summary}
              </p>
            </div>

            {/* Esperienze e Bullet Points Ottimizzati */}
            {tailoredData.experiences && tailoredData.experiences.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-slate-200">
                  Esperienze & Bullet Point Riformulati con Metriche e Azioni
                </h4>
                <div className="space-y-3">
                  {tailoredData.experiences.map((exp, i) => (
                    <div key={i} className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="text-xs font-bold text-indigo-400 uppercase tracking-wide">
                        {exp.original_company_or_role}
                      </div>
                      <ul className="space-y-1.5 text-xs text-slate-300">
                        {exp.optimized_bullets.map((b, bi) => (
                          <li key={bi} className="flex items-start gap-2">
                            <span className="text-indigo-400 font-bold">•</span>
                            <span>{b}</span>
                          </li>
                        ))}
                      </ul>
                      {exp.rationale && (
                        <p className="text-[11px] text-slate-500 italic mt-2 border-t border-slate-800/60 pt-2">
                          💡 Motivazione strategica: {exp.rationale}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Consigli e Strategia Colloquio */}
            {tailoredData.advice_notes && tailoredData.advice_notes.length > 0 && (
              <div className="bg-amber-950/20 border border-amber-800/40 rounded-xl p-4 text-xs text-amber-200 space-y-1">
                <div className="font-semibold text-amber-300">📌 Consigli per il Colloquio:</div>
                <ul className="list-disc list-inside space-y-0.5 text-amber-200/90">
                  {tailoredData.advice_notes.map((note, idx) => (
                    <li key={idx}>{note}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* AZIONE DI GENERAZIONE FINALE */}
            <div className="pt-4 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
              <label className="flex items-center gap-2.5 text-sm text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={exportPdf}
                  onChange={(e) => setExportPdf(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-950 border-slate-700"
                />
                <span>Esporta anche copia in <strong>PDF</strong> ad alta fedeltà</span>
              </label>

              <button
                onClick={handleGenerateDocument}
                disabled={isGenerating}
                className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold shadow-lg shadow-emerald-600/20 transition active:scale-95"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Compilazione DOCX & Preservazione Layout...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Applica Miglioramenti & Salva Documento</span>
                  </>
                )}
              </button>
            </div>

            {/* CARD DOWNLOAD COMPILATO */}
            {generatedFiles && (
              <div className="p-6 bg-emerald-950/40 border border-emerald-800/80 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl">
                    <FileCheck className="w-7 h-7" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white text-base">Il tuo CV Adattato è Pronto!</h4>
                    <p className="text-xs text-emerald-300/80">
                      Layout grafico, tabelle, font e colori originali mantenuti intatti al 100%.
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {generatedFiles.docx_download_url && (
                    <a
                      href={generatedFiles.docx_download_url}
                      download
                      className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-sm font-semibold border border-slate-700 transition"
                    >
                      <Download className="w-4 h-4 text-blue-400" />
                      <span>Scarica .DOCX</span>
                    </a>
                  )}

                  {generatedFiles.pdf_download_url && (
                    <a
                      href={generatedFiles.pdf_download_url}
                      download
                      className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold shadow transition"
                    >
                      <Download className="w-4 h-4" />
                      <span>Scarica .PDF</span>
                    </a>
                  )}
                </div>
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}
