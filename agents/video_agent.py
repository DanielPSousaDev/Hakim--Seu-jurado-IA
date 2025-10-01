# agents/video_agent.py
import os
import json
import asyncio # <--- ADICIONADO PARA ESPERA ASSÍNCRONA
from google import genai
from google.genai.errors import APIError
from core.utils import get_response_schema
from dotenv import load_dotenv, find_dotenv

# --- Configuração ---
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError(
        "A chave GEMINI_API_KEY não foi encontrada."
    )
client = genai.Client(api_key=API_KEY)

# --- Variáveis de Configuração ---
TIMEOUT_SECONDS = 300 # 5 minutos para processamento de arquivos grandes

async def run_video_analysis(file_path: str) -> dict:
    """Agente: Analisa evidências de vídeo e sua relevância jurídica, incluindo lógica de espera."""
    
    system_instruction = (
        "Você é o Agente de Vídeo do Hakim, um perito em análise de evidências audiovisuais. "
        "Avalie o conteúdo do vídeo, o contexto, a autenticidade e a relevância "
        "para um caso judicial. Dê uma pontuação de 0 a 100 para o valor probatório da evidência."
    )
    
    uploaded_file = None
    
    try:
        # 1. UPLOAD
        print(f"DEBUG: Iniciando upload do vídeo: {file_path}")
        uploaded_file = client.files.upload(file=file_path)
        print(f"DEBUG: Upload Gemini concluído. Nome do arquivo: {uploaded_file.name}")
        
        start_time = asyncio.get_event_loop().time()
        
        # 2. ESPERA PELO STATUS ACTIVE (CORREÇÃO DO ERRO FAILED_PRECONDITION)
        while uploaded_file.state != 'ACTIVE':
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > TIMEOUT_SECONDS:
                raise TimeoutError("O tempo limite de processamento do arquivo de vídeo foi excedido.")
            
            print(f"DEBUG: Arquivo em estado '{uploaded_file.state}'. Esperando 5 segundos...")
            await asyncio.sleep(5) # Espera 5 segundos de forma assíncrona

            # Atualiza o status do arquivo
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        print("DEBUG: Arquivo de vídeo está ativo e pronto para análise.")

        # 3. ANÁLISE
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, "Execute a análise pericial desta evidência de vídeo."],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=get_response_schema("Análise de Evidência Audiovisual (Vídeo)")
            ),
        )
        return json.loads(response.text)
    
    except TimeoutError as e:
        print(f"ERRO DE TIMEOUT no Video Agent: {e}")
        # Lançar como APIError para ser tratado no main.py
        raise APIError(f"Timeout: {e}") 
    except APIError as e:
        print(f"ERRO API GEMINI no Video Agent: {e}")
        raise e 
        
    finally:
        # 4. LIMPEZA
        if uploaded_file:
            client.files.delete(name=uploaded_file.name)