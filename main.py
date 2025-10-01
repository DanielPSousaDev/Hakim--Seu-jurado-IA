import os
import io
import json
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any

# 💡 CRÍTICO: Importa e carrega variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv() 

# ===============================================================================
# CONFIGURAÇÃO DO GOOGLE GEMINI
# ===============================================================================

# 💡 Agora, os.getenv irá encontrar a chave carregada pelo load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    from google import genai
    from google.genai.errors import APIError
    
    # Inicializa o cliente Gemini, passando a chave explicitamente se encontrada
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        client_status = "initialized"
    else:
        client = None
        client_status = "error - Chave GEMINI_API_KEY não encontrada no .env ou ambiente."
    
    MODEL_NAME = "gemini-2.5-flash" 
except ImportError:
    client = None
    client_status = "error - Biblioteca 'google-genai' não instalada."
except Exception as e:
    client = None
    client_status = f"error - Falha na inicialização: {e}"

# ===============================================================================
# CONFIGURAÇÃO DO FASTAPI E CORS
# ===============================================================================

app = FastAPI(title="Jurado IA - Gemini Backend")

# ⚠️ CONFIGURAÇÃO DE CORS
origins = [
    "http://localhost:5173",  # Front-end React
    "http://127.0.0.1:5173",
    # Adicione a URL de produção aqui quando fizer o deploy
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CRÍTICO: ROTEADOR DE API para aplicar o prefixo /api em todas as rotas abaixo.
api_router = APIRouter(prefix="/api")

# ===============================================================================
# SCHEMAS DE RESPOSTA (Pydantic)
# ===============================================================================

class AnalysisData(BaseModel):
    pontuacao: int
    pontuacao_maxima: int = 100
    feedback: str
    pontos_fortes: List[str]
    pontos_melhoria: List[str]
    veredicto: str

class CompetitionAnalysisItem(AnalysisData):
    content_name: str
    posicao: int = 0
    medalha: str = ""

class CompetitionSynthesis(BaseModel):
    pontuacao_final: float
    veredicto_geral: str
    recomendacao: str

class CompetitionResult(BaseModel):
    analises_individuais: List[CompetitionAnalysisItem]
    sintese_final: CompetitionSynthesis

class APIResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None

# ===============================================================================
# FUNÇÕES CORE DO GEMINI
# ===============================================================================

def generate_prompt(file_type: str, criteria: str, custom_instruction: str = None) -> str:
    base_prompt = (
        f"Você é um Jurado IA especializado em análise e avaliação de conteúdo. "
        f"Sua tarefa é avaliar o conteúdo de {file_type} com base nos seguintes critérios: '{criteria}'. "
        "Sua resposta DEVE ser um objeto JSON Python, formatado exatamente conforme o esquema 'AnalysisData'. "
        "Não inclua nenhum texto ou formatação fora do JSON. "
        "O JSON DEVE ser retornado diretamente. "
    )
    if custom_instruction:
        base_prompt += f"Instrução Adicional: {custom_instruction}. Incorpore esta instrução na sua análise."
    return base_prompt

async def analyze_with_gemini(file_bytes: bytes, file_mime: str, prompt: str) -> str:
    """Envia o arquivo e o prompt para o Gemini."""
    if not client:
        raise HTTPException(status_code=503, detail=f"Serviço Gemini indisponível: {client_status}")

    file_part = genai.types.Part.from_bytes(
        data=file_bytes,
        mime_type=file_mime
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, file_part],
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalysisData,
            ),
        )
        return response.text
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Erro na API Gemini: {e}")
    except Exception as e:
        # Tenta pegar a resposta raw caso haja erro de parse
        raw_response = getattr(response, 'text', 'N/A')
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}. Resposta da IA: {raw_response}")


# ===============================================================================
# ROTAS INDIVIDUAIS (PREFIXO /api JÁ APLICADO)
# ===============================================================================

@api_router.post("/analyze/document", response_model=APIResponse)
async def analyze_document_route(
    file: UploadFile = File(...), 
    criteria: str = Form(...),
    custom_instruction: str = Form(None)
):
    """Análise de documentos (PDF)."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Apenas PDF é suportado para documentos.")
        
    file_bytes = await file.read()
    prompt = generate_prompt("documento PDF", criteria, custom_instruction)
    
    analysis_result_json_str = await analyze_with_gemini(file_bytes, file.content_type, prompt)
    
    try:
        data = AnalysisData.model_validate_json(analysis_result_json_str)
        return APIResponse(success=True, data=data.model_dump())
    except ValidationError:
        return APIResponse(success=False, error="Falha ao processar a resposta da IA. Formato JSON inválido. Resposta crua da IA: " + analysis_result_json_str)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@api_router.post("/analyze/image", response_model=APIResponse)
async def analyze_image_route(
    file: UploadFile = File(...), 
    criteria: str = Form(...),
    custom_instruction: str = Form(None)
):
    """Análise de Imagens."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Apenas Imagens são suportadas.")
        
    file_bytes = await file.read()
    prompt = generate_prompt("imagem", criteria, custom_instruction)
    analysis_result_json_str = await analyze_with_gemini(file_bytes, file.content_type, prompt)
    
    try:
        data = AnalysisData.model_validate_json(analysis_result_json_str)
        return APIResponse(success=True, data=data.model_dump())
    except ValidationError:
        return APIResponse(success=False, error="Falha ao processar a resposta da IA. Formato JSON inválido. Resposta crua da IA: " + analysis_result_json_str)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@api_router.post("/analyze/audio", response_model=APIResponse)
async def analyze_audio_route(
    file: UploadFile = File(...), 
    criteria: str = Form(...),
    custom_instruction: str = Form(None)
):
    """Análise de Áudio."""
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Apenas Áudio é suportado.")
        
    file_bytes = await file.read()
    prompt = generate_prompt("arquivo de áudio (transcreva e avalie)", criteria, custom_instruction)
    analysis_result_json_str = await analyze_with_gemini(file_bytes, file.content_type, prompt)
    
    try:
        data = AnalysisData.model_validate_json(analysis_result_json_str)
        return APIResponse(success=True, data=data.model_dump())
    except ValidationError:
        return APIResponse(success=False, error="Falha ao processar a resposta da IA. Formato JSON inválido. Resposta crua da IA: " + analysis_result_json_str)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@api_router.post("/analyze/video", response_model=APIResponse)
async def analyze_video_route(
    file: UploadFile = File(...), 
    criteria: str = Form(...),
    custom_instruction: str = Form(None)
):
    """Análise de Vídeo."""
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Apenas Vídeo é suportado.")
        
    file_bytes = await file.read()
    prompt = generate_prompt("vídeo (transcreva, descreva o conteúdo e avalie)", criteria, custom_instruction)
    analysis_result_json_str = await analyze_with_gemini(file_bytes, file.content_type, prompt)
    
    try:
        data = AnalysisData.model_validate_json(analysis_result_json_str)
        return APIResponse(success=True, data=data.model_dump())
    except ValidationError:
        return APIResponse(success=False, error="Falha ao processar a resposta da IA. Formato JSON inválido. Resposta crua da IA: " + analysis_result_json_str)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# ===============================================================================
# ROTA DE COMPARAÇÃO (MULTIPLOS ARQUIVOS)
# ===============================================================================

@api_router.post("/analyze/multiple", response_model=APIResponse)
async def analyze_multiple_route(
    files: List[UploadFile] = File(...), 
    criteria: str = Form(...)
):
    """Análise comparativa de múltiplos arquivos."""
    if not client:
        raise HTTPException(status_code=503, detail=f"Serviço Gemini indisponível: {client_status}")

    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    # 1. Analisar individualmente e coletar resultados
    individual_results = []
    contents_for_synthesis = []
    
    for file in files:
        file_bytes = await file.read()
        file_mime = file.content_type
        
        # Gera o prompt para análise individual (sem instrução customizada aqui)
        individual_prompt = generate_prompt(f"arquivo de tipo {file.content_type}", criteria)
        
        try:
            # Reusa a função de análise individual, mas precisa de um esquema temporário para evitar conflito
            # Geramos a resposta JSON puro para depois validar no escopo da função
            
            # --- Início: Análise Individual ---
            if not client:
                raise HTTPException(status_code=503, detail=f"Serviço Gemini indisponível: {client_status}")

            file_part = genai.types.Part.from_bytes(data=file_bytes, mime_type=file_mime)

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[individual_prompt, file_part],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AnalysisData,
                ),
            )
            analysis_result_json_str = response.text
            # --- Fim: Análise Individual ---

            data = AnalysisData.model_validate_json(analysis_result_json_str)
            
            # Prepara o resultado individual e o conteúdo para a síntese
            individual_results.append(CompetitionAnalysisItem(
                content_name=file.filename,
                **data.model_dump()
            ))
            
            contents_for_synthesis.append(
                f"Análise do item '{file.filename}' (Pontuação: {data.pontuacao}/{data.pontuacao_maxima}): "
                f"Feedback principal: {data.feedback}. "
                f"Veredicto: {data.veredicto}\n"
            )
            
        except Exception as e:
            print(f"Erro ao analisar o arquivo {file.filename}: {e}")
            individual_results.append(CompetitionAnalysisItem(
                content_name=file.filename,
                pontuacao=0,
                feedback="Falha na análise individual.",
                pontos_fortes=[],
                pontos_melhoria=["O arquivo não pôde ser processado."],
                veredicto="Inconclusivo."
            ))

    # 2. Gera o prompt de Síntese
    synthesis_prompt = (
        f"Você recebeu as análises individuais de múltiplos itens baseadas no critério: '{criteria}'. "
        "Seu objetivo é criar uma Síntese da Competição com base nos dados fornecidos. "
        "Calcule a pontuação final média de todos os itens. "
        "Forneça um veredicto geral sobre a qualidade do grupo e uma recomendação. "
        "Sua resposta DEVE ser um objeto JSON Python, formatado exatamente conforme o esquema 'CompetitionSynthesis'. "
        "Dados para Síntese:\n"
        + "".join(contents_for_synthesis)
    )

    # 3. Envia para o Gemini para a Síntese (apenas texto)
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[synthesis_prompt],
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CompetitionSynthesis,
            ),
        )
        synthesis_data = CompetitionSynthesis.model_validate_json(response.text)
    except Exception as e:
        # Cria uma síntese de fallback se a IA falhar
        avg_score = sum(i.pontuacao for i in individual_results) / len(individual_results) if individual_results else 0
        synthesis_data = CompetitionSynthesis(
            pontuacao_final=round(avg_score, 2),
            veredicto_geral="A síntese da competição falhou. Ocorreu um erro ao processar a resposta final da IA.",
            recomendacao=f"Revisar os resultados individuais. Erro: {e}"
        )

    # 4. Compila o resultado final
    final_result = CompetitionResult(
        analises_individuais=[item.model_dump() for item in individual_results],
        sintese_final=synthesis_data.model_dump()
    )

    return APIResponse(success=True, data=final_result.model_dump())

# ===============================================================================
# INCLUSÃO DO ROUTER PRINCIPAL E ROTA DE STATUS
# ===============================================================================

# 💡 FINAL: Inclui o api_router no app principal para ativar o prefixo /api
app.include_router(api_router)

@app.get("/status")
def get_status():
    """Verifica se o servidor está rodando e o Gemini está configurado."""
    return {"status": "ok", "service": "FastAPI", "gemini_client": client_status}