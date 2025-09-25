import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../App.css'; 

function AboutPage() {
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.className = '';
    document.body.classList.add(`${savedTheme}-theme`);
  }, []);

  return (
    <div className="App-wrapper">
       <nav className="top-nav">
        <div className="container">
          <Link to="/" className="logo-link">
            <span className="logo">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" viewBox="0 0 16 16"><path d="M8 1a2.5 2.5 0 0 1 2.5 2.5V4h-5v-.5A2.5 2.5 0 0 1 8 1zM3.5 5a1 1 0 0 0-1 1v1.5a.5.5 0 0 1-1 0V6a2 2 0 0 1 2-2h1a.5.5 0 0 1 0 1h-1zM11.5 4h1a2 2 0 0 1 2 2v1.5a.5.5 0 0 1-1 0V6a1 1 0 0 0-1-1h-1a.5.5 0 0 1 0-1z"/><path d="M9.5 7a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0v-1a.5.5 0 0 1 .5-.5zm-3 0a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0v-1a.5.5 0 0 1 .5-.5z"/><path d="M2 9.5a3.5 3.5 0 0 0 3.5 3.5h7A3.5 3.5 0 0 0 16 9.5v-2a3.5 3.5 0 0 0-3.5-3.5h-7A3.5 3.5 0 0 0 2 7.5v2zm3.5-2.5a2.5 2.5 0 0 1 2.5-2.5h7a2.5 2.5 0 0 1 2.5 2.5v2a2.5 2.5 0 0 1-2.5-2.5h-7a2.5 2.5 0 0 1-2.5-2.5v-2z"/></svg>
              Jurado IA
            </span>
          </Link>
          <div className="nav-links">
            <Link to="/">Início</Link>
            <Link to="/sobre">Sobre</Link>
            <div className="theme-switch-placeholder"></div>
          </div>
        </div>
      </nav>
      <main className="container about-page">
        <h2>Democratizando a Análise de Elite</h2>
        <p className="about-subtitle">
          Nossa missão no Jurado IA é fornecer feedback instantâneo, objetivo e com a profundidade de um especialista, 
          transformando a maneira como criadores, profissionais e empresas avaliam e aprimoram seu conteúdo.
        </p>
        <div className="about-content">
          <h3>Para Quem é o Jurado IA?</h3>
          <div className="features-grid">
            <div className="feature-card">
              <i className="fas fa-paint-brush"></i>
              <h4>Criadores de Conteúdo</h4>
              <p>Receba uma segunda opinião imparcial sobre seus vídeos, podcasts, designs e textos.</p>
            </div>
            <div className="feature-card">
              <i className="fas fa-briefcase"></i>
              <h4>Profissionais de Marketing</h4>
              <p>Compare diferentes versões de campanhas e tome decisões baseadas em dados.</p>
            </div>
            <div className="feature-card">
              <i className="fas fa-graduation-cap"></i>
              <h4>Estudantes e Acadêmicos</h4>
              <p>Aprimore a qualidade de seus trabalhos, teses e apresentações com um feedback estruturado.</p>
            </div>
            <div className="feature-card">
              <i className="fas fa-rocket"></i>
              <h4>Startups e Empreendedores</h4>
              <p>Refine seu pitch deck. Nossa IA analisa a clareza, coesão e design da sua apresentação.</p>
            </div>
          </div>
        </div>
        <Link to="/" className="cta-button">
          Voltar para a Análise
        </Link>
      </main>
    </div>
  );
}

export default AboutPage;