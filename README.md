Jurado IA - Sistema de Análise de Conteúdo Multimodal

🌟 Visão Geral

O Jurado IA é uma aplicação web completa desenvolvida para automatizar a análise e pontuação de diversos tipos de conteúdo (documentos PDF, imagens, áudio e vídeo). Ele utiliza o modelo de Inteligência Artificial Google Gemini como seu motor de avaliação, retornando feedback detalhado e estruturado.

O projeto é composto por dois serviços:
Componente	Tecnologia	Porta Padrão	Função
Backend (API)	Python (FastAPI)	8000	Processa o upload de arquivos, interage com a API do Gemini e retorna análises JSON.
Frontend (Web UI)	React (Vite)	5173	Interface do usuário para upload e visualização dos resultados.

🛠️ Requisitos e Pré-requisitos

Para executar o sistema, você precisa ter instalado:
Requisito	Versão Mínima	Finalidade
Python	3.9	Ambiente de execução para o Backend.
Node.js / npm	18.x	Ambiente de execução e gerenciamento de pacotes para o Frontend.
Gemini API Key	N/A	Chave de acesso obtida no Google AI Studio. Essencial para o Backend.

📂 Estrutura de Pastas (Baseada no seu projeto)

Seu projeto tem uma estrutura onde o main.py e o ambiente virtual (.venv) estão na pasta raiz (IA_JURADA).

IA_JURADA (Raiz do Projeto)
├── .env                  ⬅️ Chave da API do Gemini
├── .venv/                ⬅️ Ambiente Virtual Python
├── agents/               
├── core/
├── hakim-jurado-front/        ⬅️ Pasta do Frontend (React)
│   ├── src/
│   ├── package.json
│   └── .env (URL do Backend)
├── main.py               ⬅️ Servidor FastAPI
├── README.md             (Este arquivo)
└── requirements.txt      

🚀 Instalação e Configuração

Siga os passos para configurar o ambiente Python (Backend) e Node (Frontend).

Passo 1: Configuração do Backend (Python)

Navegue para a pasta raiz do projeto (IA_JURADA):
    Bash

cd IA_JURADA

Crie e Ative o Ambiente Virtual (venv):
Bash

python -m venv .venv
# No Windows (PowerShell/CMD):
.\.venv\Scripts\activate
# No Linux/macOS (Bash/Zsh):
source .venv/bin/activate

Instale as Dependências do Python:
Bash

    pip install -r requirements.txt

    Configure a Chave de API do Gemini:
    Crie o arquivo .env na raiz do projeto (IA_JURADA) e adicione sua chave:

    # IA_JURADA/.env
    GEMINI_API_KEY=SUA_CHAVE_OBTIDA_DO_GOOGLE_AI_STUDIO_AQUI

Passo 2: Configuração do Frontend (React)

    Navegue para a pasta do Frontend (substitua hakim-jura... pelo nome correto da sua pasta React):
    Bash

cd hakim-jurado-front

Instale as Dependências do Node:
Bash

npm install



▶️ Como Executar o Sistema

Você deve iniciar o Backend e o Frontend em terminais separados.

1. Iniciar o Backend (Terminal 1)

Execute na raiz do projeto (IA_JURADA) com o ambiente virtual ativado:
Bash

uvicorn main:app --reload

    Verificação: O backend deve iniciar na porta 8000. Você pode confirmar o status acessando: http://127.0.0.1:8000/status.

2. Iniciar o Frontend (Terminal 2)

Execute na pasta do Frontend (sem o ambiente virtual Python ativado):
Bash

npm run dev

    Acesso: O frontend será servido em: http://localhost:5173.

🔍 Funcionalidades de Análise

O Jurado IA suporta dois modos principais:
Modo de Análise	Tipos de Arquivo Suportados	Descrição
Individual	PDF, Imagem, Áudio, Vídeo	Upload de um único arquivo para pontuação e feedback detalhado.
Competição	PDF, Imagem, Áudio, Vídeo	Upload de múltiplos arquivos (do mesmo tipo) para comparação, ranking e síntese final da competição.
