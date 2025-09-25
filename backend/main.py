from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import tempfile
import shutil
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa nosso único agente
from agents.text_agent import TextAnalysisAgent

app = FastAPI(
    title="Jurado IA - Análise de Textos e Documentos",
    description="Sistema focado em análise de conteúdo textual usando IA.",
    version="2.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://seu-frontend.vercel.app"], # Lembre-se de adicionar sua URL da Vercel aqui
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o agente
text_agent = TextAnalysisAgent()

# --- Modelos Pydantic ---
class TextAnalysisRequest(BaseModel):
    text: str
    criteria: str = "Avaliação geral de qualidade"

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# --- Rotas da API ---

@app.get("/")
async def root():
    return {"message": "Jurado IA (Texto/PDF) - Online"}

@app.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text_route(request: TextAnalysisRequest):
    """Analisa um texto puro enviado via JSON."""
    try:
        result = text_agent.analyze(request.text, request.criteria)
        if "erro" in result:
             return AnalysisResponse(success=False, error=result["erro"])
        return AnalysisResponse(success=True, data=result)
    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))

@app.post("/analyze/document", response_model=AnalysisResponse)
async def analyze_document_route(file: UploadFile = File(...), criteria: str = Form("Avaliação geral")):
    """Faz o upload de um PDF, extrai o texto e o analisa."""
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")
    
    # Salva o arquivo PDF temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name
        
    try:
        result = text_agent.analyze_document(temp_path, criteria)
        if "erro" in result:
             return AnalysisResponse(success=False, error=result["erro"])
        return AnalysisResponse(success=True, data=result)
    finally:
        # Garante que o arquivo temporário seja sempre deletado
        os.unlink(temp_path)

# --- Entrypoint para rodar o servidor ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)