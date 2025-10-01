import os
import json
import asyncio
from google import genai
from google.genai.errors import APIError
from core.utils import get_response_schema
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("A chave GEMINI_API_KEY não foi encontrada.")
client = genai.Client(api_key=API_KEY)
TIMEOUT_SECONDS = 300 

async def run_audio_analysis(file_path: str, custom_instruction: str = None) -> dict:
    """Agente: Analisa evidências de áudio e sua relevância jurídica."""
    
    system_instruction = (
        "Você é o Agente de Áudio do Hakim, um perito em análise de evidências auditivas. "
        "Transcreva o áudio e avalie o conteúdo, o contexto, a autenticidade e a relevância "
        "para um caso judicial. Dê uma pontuação de 0 a 100 para o valor probatório da evidência."
    )
    
    if custom_instruction:
        system_instruction += f"\n\nInstrução Adicional do Usuário: {custom_instruction}"
        print(f"DEBUG: Aplicando instrução customizada: {custom_instruction}") # Log para debug
    
    uploaded_file = None
    
    try:
        uploaded_file = client.files.upload(file=file_path)
        print(f"DEBUG: Upload Gemini concluído. Nome do arquivo: {uploaded_file.name}")
        
        start_time = asyncio.get_event_loop().time()
        while uploaded_file.state != 'ACTIVE':
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > TIMEOUT_SECONDS:
                raise TimeoutError("O tempo limite de processamento do arquivo de áudio foi excedido.")
            
            await asyncio.sleep(5) 
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, "Execute a análise pericial desta evidência de áudio."],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=get_response_schema("Análise de Evidência Auditiva (Áudio)")
            ),
        )
        return json.loads(response.text)
    
    except Exception as e:
        raise APIError(f"Erro no processamento de áudio: {e}") 
        
    finally:
        if uploaded_file:
            client.files.delete(name=uploaded_file.name)
