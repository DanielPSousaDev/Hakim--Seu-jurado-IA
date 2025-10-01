# agents/image_agent.py
import os
import json
from google import genai
from google.genai.errors import APIError # Importa o erro da API para melhor debug
from core.utils import get_response_schema
from dotenv import load_dotenv, find_dotenv

# --- Carregamento e Verificação Robusta do .env ---
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)

# 🚨 VERIFICAÇÃO CRÍTICA
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise EnvironmentError(
        "A chave GEMINI_API_KEY não foi encontrada ou está vazia no seu arquivo .env. "
        "Verifique se o arquivo .env está na pasta raiz e se a chave está correta."
    )
# ----------------------------------------------------

client = genai.Client(api_key=API_KEY)

async def run_image_analysis(file_path: str) -> dict:
    """Agente: Analisa evidências visuais (imagens/fotos) e sua relevância jurídica."""
    
    system_instruction = (
        "Você é o Agente de Imagem do Hakim, um perito em análise de evidências visuais. "
        "Avalie a autenticidade, o contexto, a probabilidade de manipulação e a relevância da imagem "
        "para um caso judicial. Dê uma pontuação de 0 a 100 para o valor probatório da evidência."
    )
    
    uploaded_file = client.files.upload(file=file_path)
    
    # ADICIONADO: Log de debug para confirmar o upload
    print(f"DEBUG: Upload Gemini bem-sucedido. Nome do arquivo: {uploaded_file.name}")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, "Execute a análise pericial desta evidência de imagem."],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=get_response_schema("Análise de Evidência Visual (Imagem)")
            ),
        )
        return json.loads(response.text)
    
    except APIError as e:
        print(f"ERRO API GEMINI no Image Agent: {e}")
        raise e # Re-lança o erro para ser capturado no main.py
        
    finally:
        client.files.delete(name=uploaded_file.name)