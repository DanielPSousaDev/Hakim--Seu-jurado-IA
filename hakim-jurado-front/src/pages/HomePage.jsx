import React, { useState } from 'react';
// 👇 CRUCIAL: Importa as funções de análise EXPORTADAS de App.jsx
import { SingleAnalysis, CompetitionAnalysis } from '../App.jsx'; 

function HomePage() {
  const [mode, setMode] = useState('single');
  
  return (
    <>
        {/* CONTEÚDO hero-section (Movido para cá) */}
        <section className="hero-section">
            <div className="container">
                <h1>Análise Jurídica com Inteligência Artificial</h1>
                <p className="subtitle">Obtenha feedback detalhado e pontuações profissionais para seus documentos e arquivos com a nossa poderosa IA.</p>
            </div>
        </section>
        {/* CONTEÚDO app-section (Movido para cá) */}
        <section className="app-section">
            <div className="container">
                <div className="mode-description-cards">
                    <div className="description-card"><h4>Análise Individual</h4><p>Faça o upload de um único arquivo para receber uma pontuação detalhada e um feedback completo da IA.</p></div>
                    <div className="description-card"><h4>Modo Competição</h4><p>Envie múltiplos arquivos e receba um ranking comparativo com uma análise final.</p></div>
                </div>
                <div className="main-content-card">
                    <nav className="nav-tabs">
                        <button onClick={() => setMode('single')} className={mode === 'single' ? 'active' : ''}>Análise Individual</button>
                        <button onClick={() => setMode('competition')} className={mode === 'competition' ? 'active' : ''}>Modo Competição</button>
                    </nav>
                    {/* Renderiza o componente de análise correto */}
                    {mode === 'single' ? <SingleAnalysis /> : <CompetitionAnalysis />}
                </div>
            </div>
        </section>
    </>
  );
}

export default HomePage;