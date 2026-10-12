import React, { useState, useEffect } from 'react';
import { 
  Upload, FileText, Sparkles, CheckCircle2, AlertCircle, 
  ArrowRight, Download, RefreshCw, FileCheck, Layers, Cpu, ShieldCheck,
  Github, Code2, ExternalLink, Compass, Briefcase, Search, ArrowUpRight,
  TrendingUp, Award, ChevronRight
} from 'lucide-react';

export default function App() {
  // Tab attiva: 'tailor' | 'discover'
  const [activeTab, setActiveTab] = useState('tailor');

  // Stati di input CV & JD
  const [cvFile, setCvFile] = useState(null);
  const [cvInfo, setCvInfo] = useState(null);
  const [jdText, setJdText] = useState('');
  const [isUploadingCv, setIsUploadingCv] = useState(false);
  const [githubUsername, setGithubUsername] = useState('gabrielex99');
  const [includeGithub, setIncludeGithub] = useState(true);

  // Stati di elaborazione agenti (Tailoring)
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState('');
  const [jobAnalysis, setJobAnalysis] = useState(null);
  const [tailoredData, setTailoredData] = useState(null);

  // Stati Career Discovery
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [discoveryResult, setDiscoveryResult] = useState(null);
  const [discoveryError, setDiscoveryError] = useState(null);

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

  // Incolla JD di esempio (Leonardo NATO AGS)
  const handleLoadSampleJd = () => {
    setJdText(`Titolo: Supporto Infrastruttura di Terra NATO AGS (Electronics Division)
Azienda: Leonardo S.p.A.
Sede: Catania / Base Militare di Sigonella

Requisiti Chiave:
- Configurazione e manutenzione reti informatiche complesse (Networking & Sicurezza Cisco).
- Amministrazione dei sistemi operativi Windows e Linux.
- Conoscenza di LDAP, PostgreSQL, VMware, Docker e Zabbix (o Grafana).
- Sviluppo script in Python, Bash, Go per automazione processi operativi.
- Idoneità Nulla Osta di Segretezza (NOS).
- Buona conoscenza lingua inglese (B2).`);
  };

  // Incolla JD di esempio (AI Engineer)
  const handleLoadAiEngineerJd = () => {
    setJdText(`Titolo: Senior AI Engineer / LLM Specialist
Azienda: TechGenius Labs (Milano / Remote)

Chi cerchiamo:
Un Senior AI Engineer per guidare lo sviluppo di piattaforme GenAI e sistemi ad agenti autonomi.

Requisiti Chiave & Hard Skills:
- Comprovata esperienza con Python (FastAPI), PyTorch o framework moderni di intelligenza artificiale.
- Progettazione di pipeline RAG avanzate con LangChain, LlamaIndex o LiteLLM e Vector Databases (Chroma DB, pgvector).
- Esperienza con modelli multimodali, generazione video/audio, prompting avanzato e agenti cooperanti.
- Esperienza con architetture containerizzate (Docker, Kubernetes) e automazione MLOps.
- Familiarità con l'ingegnerizzazione di prodotti AI reali e progetti open source.`);
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
      setAnalysisStep('1/2: Job Analyzer Agent estrae requisiti e keyword ATS...');
      const jdRes = await fetch('/api/analyze-jd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jd_input: jdText }),
      });
      if (!jdRes.ok) throw new Error("Errore durante l'analisi della Job Description");
      const jdData = await jdRes.json();
      setJobAnalysis(jdData);

      // Step 2: CV Tailor Agent & GitHub Project Scanner
      setAnalysisStep('2/2: CV Tailor & GitHub Agent scansionano i progetti ed ottimizzano il CV...');
      const tailorRes = await fetch('/api/tailor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cv_text: cvInfo.full_text,
          job_analysis: jdData,
          github_username: includeGithub && githubUsername.trim() ? githubUsername.trim() : null
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
          github_projects: tailoredData.github_projects || []
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

  // Flusso Career Discovery Agent (Scoperta Nuovi Ruoli)
  const handleDiscoverRoles = async () => {
    setIsDiscovering(true);
    setDiscoveryError(null);

    try {
      const res = await fetch('/api/discover-roles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cv_text: cvInfo ? cvInfo.full_text : '',
          cv_filename: cvFile || 'master_cv.docx',
          github_username: githubUsername.trim() || 'gabrielex99'
        }),
      });
      if (!res.ok) throw new Error('Errore durante la ricerca dei ruoli ideali');
      const data = await res.json();
      setDiscoveryResult(data);
    } catch (err) {
      setDiscoveryError(err.message);
    } finally {
      setIsDiscovering(false);
    }
  };

  // Applica un ruolo scoperto direttamente al modulo di Tailoring
  const handleApplyRoleOpportunity = (opp) => {
    if (opp.sample_jd) {
      setJdText(opp.sample_jd);
    } else {
      setJdText(`Titolo: ${opp.role_title}\nCategoria: ${opp.category}\nCompetenze Richieste: ${opp.top_skills.join(', ')}\n\nDescrizione del Ruolo:\nCerchiamo un profilo specializzato con forte background in ${opp.top_skills.slice(0, 3).join(', ')}.\n${opp.why_you_fit}`);
    }
    setActiveTab('tailor');
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
                  Adatta il tuo CV a ruoli specifici (es. AI Engineer, Sistemi, Cloud) preservando font e grafica al 100% ed integrando i tuoi progetti GitHub reali.
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

        {/* TAB NAVIGATION */}
        <div className="flex items-center gap-3 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('tailor')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition ${
              activeTab === 'tailor'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20 font-semibold'
                : 'bg-slate-900/80 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>🎯 Adatta CV a un'Offerta</span>
          </button>

          <button
            onClick={() => setActiveTab('discover')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition ${
              activeTab === 'discover'
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-600/20 font-semibold'
                : 'bg-slate-900/80 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
            }`}
          >
            <Compass className="w-4 h-4 text-pink-400" />
            <span>🧭 Scopri Ruoli & Opportunità Nascoste</span>
            <span className="text-[10px] bg-amber-400/20 text-amber-300 px-2 py-0.5 rounded-full font-bold border border-amber-400/30">
              Career Advisor
            </span>
          </button>
        </div>

        {/* MESSAGGIO ERRORE */}
        {errorMsg && (
          <div className="p-4 bg-red-950/60 border border-red-800/80 rounded-xl text-red-200 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 1: ADATTA CV A UN'OFFERTA (CORE TAILORING WORKFLOW) */}
        {/* ========================================================================= */}
        {activeTab === 'tailor' && (
          <div className="space-y-6">
            {/* BARRA INTEGRAZIONE GITHUB SCANNER */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-slate-800 text-indigo-400 rounded-xl">
              <Github className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white flex items-center gap-2">
                GitHub AI Projects Scanner
                <span className="text-[10px] uppercase font-bold bg-indigo-900/60 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-700/40">
                  Nuova Funzionalità
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Estrae i tuoi progetti (es. AI, LLM, Agenti) e li inserisce nel CV come esperienze pratiche.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 w-full md:w-auto">
              <span className="text-xs text-slate-500 font-mono">github.com/</span>
              <input
                type="text"
                value={githubUsername}
                onChange={(e) => setGithubUsername(e.target.value)}
                placeholder="username"
                className="bg-transparent text-xs text-indigo-300 font-mono focus:outline-none w-28"
              />
            </div>

            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={includeGithub}
                onChange={(e) => setIncludeGithub(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600 bg-slate-950 border-slate-700"
              />
              <span className="whitespace-nowrap">Attiva Scansione</span>
            </label>
          </div>
        </div>

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
                Mantiene 100% stili, colori, font e interlinee
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
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleLoadAiEngineerJd}
                    className="text-xs bg-indigo-950/80 hover:bg-indigo-900 text-indigo-300 px-2.5 py-1 rounded-md border border-indigo-800/60 transition"
                  >
                    💡 Esempio AI Engineer
                  </button>
                  <button
                    onClick={handleLoadSampleJd}
                    className="text-xs text-purple-400 hover:text-purple-300 font-medium"
                  >
                    Esempio Sistemi/NATO
                  </button>
                </div>
              </div>

              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Incolla qui il testo dell'offerta (es. Posizione AI Engineer, Machine Learning, Sistemi)..."
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
                  Ecco come l'agent ha ottimizzato il tuo CV per massimizzare il punteggio ATS ed evidenziare i tuoi progetti GitHub reali.
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

            {/* SEZIONE PROGETTI GITHUB SELEZIONATI (NUOVA FEATURE!) */}
            {tailoredData.github_projects && tailoredData.github_projects.length > 0 && (
              <div className="bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-800/60 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-indigo-300 flex items-center gap-2">
                    <Code2 className="w-4 h-4 text-indigo-400" />
                    Progetti GitHub Integrati nel CV come Esperienze Pratiche
                  </h4>
                  <span className="text-xs px-2 py-0.5 bg-indigo-900/60 text-indigo-300 rounded border border-indigo-700/50">
                    {tailoredData.github_projects.length} Progetti Selezionati
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {tailoredData.github_projects.map((proj, pi) => (
                    <div key={pi} className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="font-semibold text-white text-xs">
                          {proj.project_title}
                        </div>
                        {proj.github_url && (
                          <a
                            href={proj.github_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-slate-500 hover:text-indigo-400 shrink-0"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-1">
                        {proj.tech_stack && proj.tech_stack.map((t, ti) => (
                          <span key={ti} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                            {t}
                          </span>
                        ))}
                      </div>

                      <ul className="space-y-1 text-xs text-slate-300 pt-1">
                        {proj.bullets && proj.bullets.map((b, bi) => (
                          <li key={bi} className="flex items-start gap-1.5">
                            <span className="text-indigo-400 font-bold">•</span>
                            <span>{b}</span>
                          </li>
                        ))}
                      </ul>

                      {proj.relevance_reason && (
                        <p className="text-[11px] text-indigo-300/80 italic border-t border-slate-800/80 pt-1.5 mt-2">
                          🎯 Perché è rilevante: {proj.relevance_reason}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Esperienze e Bullet Points Ottimizzati */}
            {tailoredData.experiences && tailoredData.experiences.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-slate-200">
                  Esperienze Lavorative Riformulate con Metriche e Focus Tecnico
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
                      Layout grafico, tabelle, font e colori originali mantenuti intatti al 100%. Progetti GitHub integrati.
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
        )}

        {/* ========================================================================= */}
        {/* TAB 2: SCOPRI RUOLI & OPPORTUNITÀ NASCOSTE (CAREER ADVISOR AGENT) */}
        {/* ========================================================================= */}
        {activeTab === 'discover' && (
          <div className="space-y-6">
            
            {/* HERO BANNER CAREER ADVISOR */}
            <div className="bg-gradient-to-r from-purple-950/60 via-slate-900 to-indigo-950/60 border border-purple-800/50 rounded-2xl p-6 md:p-8 shadow-2xl space-y-5">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-2">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-900/60 border border-purple-700/50 text-xs font-semibold text-purple-300">
                    <Compass className="w-3.5 h-3.5" />
                    Career Discovery & Role Advisor Agent
                  </div>
                  <h2 className="text-2xl font-black text-white">
                    Scopri Nuove Opportunità Sbloccate dal tuo Profilo GitHub + CV
                  </h2>
                  <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
                    Spesso abbiamo competenze pratiche su repository GitHub personali (es. <em>Agenti AI, LangChain, Kubernetes, Scraper</em>) che nel CV tradizionale passano inosservate. Questo Agent scova i lavori ideali in cui hai un <strong>fit altissimo</strong>.
                  </p>
                </div>

                <button
                  onClick={handleDiscoverRoles}
                  disabled={isDiscovering}
                  className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 hover:opacity-95 text-white font-bold rounded-xl shadow-lg shadow-purple-600/30 transition transform active:scale-95 shrink-0"
                >
                  {isDiscovering ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Analisi Profilo & Progetti in corso...</span>
                    </>
                  ) : (
                    <>
                      <Compass className="w-5 h-5" />
                      <span>🔍 Scopri Ruoli Consigliati</span>
                    </>
                  )}
                </button>
              </div>

              {/* Parametri di analisi */}
              <div className="pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-6 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  <span>CV Base:</span>
                  <strong className="text-slate-200">
                    {cvInfo ? cvInfo.original_name : 'master_cv.docx (Default)'}
                  </strong>
                </div>

                <div className="flex items-center gap-2">
                  <Github className="w-4 h-4 text-indigo-400" />
                  <span>GitHub:</span>
                  <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                    <span className="text-slate-500 font-mono">@</span>
                    <input
                      type="text"
                      value={githubUsername}
                      onChange={(e) => setGithubUsername(e.target.value)}
                      className="bg-transparent text-indigo-300 font-mono focus:outline-none w-24 text-xs font-semibold"
                    />
                  </div>
                </div>

                <div className="text-slate-500">
                  Tip: Clicca su <em>"Usa per Adattare il CV"</em> per caricare istantaneamente il ruolo nel generatore.
                </div>
              </div>
            </div>

            {/* ERRORE DISCOVERY */}
            {discoveryError && (
              <div className="p-4 bg-red-950/60 border border-red-800/80 rounded-xl text-red-200 text-sm flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
                <span>{discoveryError}</span>
              </div>
            )}

            {/* RISULTATI DISCOVERY */}
            {discoveryResult && (
              <div className="space-y-6 animate-fade-in">

                {/* SINTESI STRATEGICA DEL PROFILO */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                  <div className="flex items-center gap-2.5 text-base font-bold text-white">
                    <Award className="w-5 h-5 text-amber-400" />
                    <span>Sintesi Strategica del Candidato (Executive View)</span>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800/80">
                    {discoveryResult.candidate_summary}
                  </p>

                  {/* Competenze Rilevate */}
                  {discoveryResult.extracted_competencies && discoveryResult.extracted_competencies.length > 0 && (
                    <div className="space-y-2 pt-2">
                      <div className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                        Competenze Chiave Identificate dall'Unione CV + Progetti
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {discoveryResult.extracted_competencies.map((comp, ci) => (
                          <span
                            key={ci}
                            className="text-xs px-3 py-1 bg-purple-950/50 text-purple-200 border border-purple-800/50 rounded-lg font-medium"
                          >
                            {comp}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* GRIGLIA OPPORTUNITÀ E RUOLI CONSIGLIATI */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-emerald-400" />
                      Ruoli di Mercato Consigliati ({discoveryResult.opportunities.length})
                    </h3>
                    <span className="text-xs text-slate-400">
                      Ordinati per Fit e Potenziale di Posizionamento
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {discoveryResult.opportunities.map((opp, oi) => (
                      <div
                        key={oi}
                        className="bg-slate-900 border border-slate-800 hover:border-purple-600/60 rounded-2xl p-5 flex flex-col justify-between shadow-xl transition space-y-4 group"
                      >
                        <div className="space-y-3">
                          {/* Header card: Categoria e Match Score */}
                          <div className="flex items-center justify-between">
                            <span className="text-[11px] uppercase tracking-wider font-bold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                              {opp.category}
                            </span>
                            <span className="text-xs font-black px-2.5 py-1 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-800/50 flex items-center gap-1">
                              <span>{opp.match_score}%</span>
                              <span className="text-[10px] text-emerald-500 font-normal">fit</span>
                            </span>
                          </div>

                          {/* Titolo Ruolo */}
                          <h4 className="text-base font-bold text-white group-hover:text-purple-300 transition">
                            {opp.role_title}
                          </h4>

                          {/* Perché sei ideale */}
                          <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800/60">
                            {opp.why_you_fit}
                          </p>

                          {/* Sbloccato da GitHub */}
                          {opp.unlocked_by_github && opp.unlocked_by_github.length > 0 && (
                            <div className="space-y-1.5 pt-1">
                              <div className="text-[11px] font-semibold text-indigo-400 flex items-center gap-1.5">
                                <Code2 className="w-3.5 h-3.5" />
                                <span>Sbloccato dai tuoi Progetti:</span>
                              </div>
                              <div className="flex flex-wrap gap-1.5">
                                {opp.unlocked_by_github.map((proj, pidx) => (
                                  <span
                                    key={pidx}
                                    className="text-[11px] px-2 py-0.5 bg-indigo-950/70 text-indigo-300 border border-indigo-800/40 rounded font-mono"
                                  >
                                    {proj}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Top skills */}
                          {opp.top_skills && opp.top_skills.length > 0 && (
                            <div className="space-y-1 pt-1">
                              <div className="text-[11px] text-slate-400 font-semibold">
                                Competenze Chiave:
                              </div>
                              <div className="flex flex-wrap gap-1">
                                {opp.top_skills.map((sk, ski) => (
                                  <span
                                    key={ski}
                                    className="text-[10px] px-2 py-0.5 bg-slate-950 text-slate-300 rounded border border-slate-800"
                                  >
                                    {sk}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Azioni Card */}
                        <div className="pt-3 border-t border-slate-800/80 space-y-2">
                          <button
                            onClick={() => handleApplyRoleOpportunity(opp)}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-95 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/20 transition"
                          >
                            <span>🎯 Usa questo Ruolo per Adattare il CV</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>

                          {opp.search_query_suggested && (
                            <a
                              href={`https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(opp.search_query_suggested)}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-lg text-[11px] border border-slate-800 transition"
                            >
                              <Search className="w-3 h-3 text-blue-400" />
                              <span>Cerca offerte su LinkedIn</span>
                              <ExternalLink className="w-3 h-3 ml-0.5 text-slate-500" />
                            </a>
                          )}
                        </div>

                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}
