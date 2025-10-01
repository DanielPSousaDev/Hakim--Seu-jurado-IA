import React, { useState, useEffect } from 'react';
import axios from 'axios';
// 👇 CRUCIAL: Importar Link e Outlet para o roteamento funcionar
import { Link, Outlet } from 'react-router-dom'; 
import './App.css';

// --- ÍCONE DO ROBÔ (SVG Embutido) ---
const RobotIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" viewBox="0 0 16 16">
    <path d="M8 1a2.5 2.5 0 0 1 2.5 2.5V4h-5v-.5A2.5 2.5 0 0 1 8 1zM3.5 5a1 1 0 0 0-1 1v1.5a.5.5 0 0 1-1 0V6a2 2 0 0 1 2-2h1a.5.5 0 0 1 0 1h-1zM11.5 4h1a2 2 0 0 1 2 2v1.5a.5.5 0 0 1-1 0V6a1 1 0 0 0-1-1h-1a.5.5 0 0 1 0-1z"/>
    <path d="M9.5 7a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0v-1a.5.5 0 0 1 .5-.5zm-3 0a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0v-1a.5.5 0 0 1 .5-.5z"/>
    <path d="M2 9.5a3.5 3.5 0 0 0 3.5 3.5h7A3.5 3.5 0 0 0 16 9.5v-2a3.5 3.5 0 0 0-3.5-3.5h-7A3.5 3.5 0 0 0 2 7.5v2zm3.5-2.5a2.5 2.5 0 0 1 2.5-2.5h7a2.5 2.5 0 0 1 2.5 2.5v2a2.5 2.5 0 0 1-2.5-2.5h-7a2.5 2.5 0 0 1-2.5-2.5v-2z"/>
  </svg>
);

// --- Componentes Auxiliares de Exibição (Sem Alterações) ---
function ResultsDisplay({ result }) {
  if (!result) return null;
  if (result.detail || result.erro) { return <div className="results-container error-message">Erro na análise: {result.detail || result.erro}</div>; } 
  return (
    <div className="results-card">
      <h2>Resultado da Análise 📊</h2>
      <div className="score"><strong>Pontuação:</strong> {result.pontuacao || 'N/A'} / {result.pontuacao_maxima || 100}</div>
      <p><strong>Feedback:</strong> {result.feedback}</p>
      <div className="details">
        <div className="fortes"><h3>Pontos Fortes:</h3><ul>{result.pontos_fortes?.map((point, index) => <li key={index}>{point}</li>)}</ul></div>
        <div className="melhoria"><h3>Pontos de Melhoria:</h3><ul>{result.pontos_melhoria?.map((point, index) => <li key={index}>{point}</li>)}</ul></div>
      </div>
      <p className="verdict"><strong>Resumo:</strong> {result.veredicto}</p>
    </div>
  );
}

function CompetitionResultsDisplay({ result }) {
  if (!result) return null;
  const { analises_individuais = [], sintese_final = {} } = result;
  return (
    <div className="results-container">
      <div className="results-card synthesis-card">
        <h2>Síntese da Competição 🏆</h2>
        <div className="score"><strong>Pontuação Final (Média):</strong> {sintese_final.pontuacao_final?.toFixed(2) || 'N/A'}</div>
        <p><strong>Veredicto Geral:</strong> {sintese_final.veredicto_geral}</p>
        <p><strong>Recomendação:</strong> {sintese_final.recomendacao}</p>
      </div>
      <h2>Ranking Individual</h2>
      {analises_individuais.map((item, index) => (
        <div key={index} className="results-card-small">
          <h3>{item.posicao || index + 1}. {item.content_name} ({item.pontuacao} / {item.pontuacao_maxima || 100}) {item.medalha}</h3>
          <p><strong>Veredicto:</strong> {item.veredicto}</p>
        </div>
      ))}
    </div>
  );
}

// 👇 CRUCIAL: Exportar as funções para serem usadas em HomePage.jsx
export function SingleAnalysis() {
  const [file, setFile] = useState(null);
  const [criteria, setCriteria] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [fileName, setFileName] = useState('');
  const setFileAndName = (file, name) => { setFile(file); setFileName(name); setResult(null); setError(''); };
  const handleFileChange = (e) => { const selectedFile = e.target.files[0]; if (selectedFile) { setFileAndName(selectedFile, selectedFile.name); } };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) { setError('Por favor, selecione um arquivo.'); return; }
    setIsLoading(true); setError(''); setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('criteria', criteria || 'Análise geral de qualidade');
    
    let endpoint = '';
    const fileType = file.type;
    
    if (fileType.startsWith('image/')) { endpoint = '/analyze/image'; }
    else if (fileType.startsWith('audio/')) { endpoint = '/analyze/audio'; }
    else if (fileType.startsWith('video/')) { endpoint = '/analyze/video'; }
    else if (fileType === 'application/pdf') { endpoint = '/analyze/document'; }
    else { setError(`Tipo de arquivo "${fileType}" não suportado.`); setIsLoading(false); return; }
    
    // 👇 CRÍTICO: CORREÇÃO DO URL PARA INCLUIR /api
    const backendUrl = `${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/api${endpoint}`;
    
    try {
      const response = await axios.post(backendUrl, formData);
      if (response.data.success) { 
          setResult(response.data.data); 
      }
      else { setError(response.data.error || response.data.detail || 'Ocorreu um erro na análise.'); }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro de conexão com o servidor. O back-end está rodando?';
      setError(errorMsg);
    } finally { setIsLoading(false); }
  };

  return (
    <div className="tab-content">
      <div className="tab-header"><i className="fas fa-user-edit"></i><h3>Análise Individual</h3></div>
      <p>Faça o upload de um arquivo para uma análise detalhada.</p>
      
      <form onSubmit={handleSubmit}>
        <label htmlFor="single-file-upload" className="upload-area"><i className="fas fa-cloud-upload-alt"></i><p>{fileName || 'Clique para fazer o upload ou arraste e solte'}</p><span>Suporta: Imagens, Áudio, Vídeo e PDF</span></label>
        <input id="single-file-upload" type="file" onChange={handleFileChange} accept="image/*,audio/*,video/*,.pdf" />

        <div className="criteria-input">
            <label htmlFor="criteria-single">Critérios de Avaliação</label>
            <input id="criteria-single" type="text" value={criteria} onChange={(e) => setCriteria(e.target.value)} placeholder="Análise geral de qualidade" />
        </div>
        
        <button type="submit" className="main-button" disabled={isLoading || !file}>
            {isLoading ? 'Analisando...' : 'Analisar Arquivo'}
        </button>
      </form>
      {error && <p className="error-message">{error}</p>}
      {isLoading && (<div className="loading-overlay"><div className="loader"></div><p>Analisando com Gemini...</p><span>Isso pode levar alguns segundos.</span></div>)}
      <ResultsDisplay result={result} />
    </div>
  );
}

// 👇 CRUCIAL: Exportar a função para ser usada em HomePage.jsx
export function CompetitionAnalysis() {
  const [files, setFiles] = useState([]);
  const [criteria, setCriteria] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const handleFileChange = (e) => { setFiles([...e.target.files]); setResult(null); setError(''); };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) { setError('Por favor, selecione pelo menos um arquivo.'); return; }
    setIsLoading(true); setError(''); setResult(null);
    
    const formData = new FormData();
    files.forEach(file => { formData.append('files', file); });
    formData.append('criteria', criteria || 'Avaliação comparativa de qualidade');

    // 👇 CRÍTICO: CORREÇÃO DO URL PARA INCLUIR /api
    const backendUrl = `${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/api/analyze/multiple`;
    
    try {
      const response = await axios.post(backendUrl, formData);
      if (response.data.success) {
        const sortedData = response.data.data;
        sortedData.analises_individuais.sort((a, b) => (b.pontuacao || 0) - (a.pontuacao || 0));
        sortedData.analises_individuais.forEach((item, index) => {
          item.posicao = index + 1;
          if (index === 0) item.medalha = '🥇';
          if (index === 1) item.medalha = '🥈';
          if (index === 2) item.medalha = '🥉';
        });
        setResult(sortedData);
      } else { setError(response.data.error || response.data.detail || 'Ocorreu um erro na análise.'); }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro de conexão com o servidor. O back-end está rodando?';
      setError(errorMsg);
    } finally { setIsLoading(false); }
  };
  
  return (
    <div className="tab-content">
      <div className="tab-header"><i className="fas fa-users"></i><h3>Modo Competição</h3></div>
      <p>Faça o upload de múltiplos arquivos para compará-los e obter uma síntese final.</p>
      <form onSubmit={handleSubmit}>
        <label htmlFor="multi-file-upload" className="upload-area"><i className="fas fa-cloud-upload-alt"></i><p>{files.length > 0 ? `${files.length} arquivos selecionados` : 'Clique para fazer o upload ou arraste e solte'}</p><span>Suporta: Imagens, Áudio, Vídeo e PDF</span></label>
        <input id="multi-file-upload" type="file" multiple onChange={handleFileChange} accept="image/*,audio/*,video/*,.pdf" />
        <div className="file-list">{files.map((file, index) => (<span key={index} className="file-tag">{file.name}</span>))}</div>
        <div className="criteria-input"><label htmlFor="criteria-competition">Critérios da Competição</label><input id="criteria-competition" type="text" value={criteria} onChange={(e) => setCriteria(e.target.value)} placeholder="Avaliação comparativa de qualidade" /></div>
        <button type="submit" className="main-button" disabled={isLoading || files.length === 0}>{isLoading ? 'Analisando...' : `Analisar ${files.length} Itens`}</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      {isLoading && (<div className="loading-overlay"><div className="loader"></div><p>Analisando com Gemini...</p><span>Isso pode levar alguns segundos.</span></div>)}
      <CompetitionResultsDisplay result={result} />
    </div>
  );
}


// O componente App AGORA É APENAS O LAYOUT (sem conteúdo de página)
function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.body.className = '';
    document.body.classList.add(`${theme}-theme`);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="App">
        <nav className="top-nav">
            <div className="container">
                {/* CRÍTICO: Usar Link para roteamento interno */}
                <Link to="/" className="logo-link">
                    <span className="logo"><RobotIcon /> Jurado IA</span>
                </Link>
                <div className="nav-links">
                    {/* CRÍTICO: Usar Link para roteamento interno */}
                    <Link to="/">Início</Link>
                    <Link to="/sobre">Sobre</Link>
                    <div className="theme-switch-wrapper">
                        <label className="theme-switch" htmlFor="theme-checkbox">
                            <input type="checkbox" id="theme-checkbox" checked={theme === 'dark'} onChange={toggleTheme}/>
                            <div className="slider"><div className="icon-wrapper"><i className="fas fa-sun"></i><i className="fas fa-moon"></i></div></div>
                        </label>
                    </div>
                </div>
            </div>
        </nav>
        <main>
            {/* 👇 CRÍTICO: O <Outlet /> renderiza o conteúdo da rota (HomePage ou AboutPage) */}
            <Outlet /> 
        </main>
    </div>
  );
}

export default App;