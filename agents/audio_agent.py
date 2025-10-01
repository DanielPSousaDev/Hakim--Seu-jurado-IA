# agents/audio_agent.py (APLIQUE ESTA LÓGICA EM TODOS OS SEUS AGENTES)
import os
import json
import asyncio
from google import genai
from google.genai.errors import APIError
from core.utils import get_response_schema
from dotenv import load_dotenv, find_dotenv

# --- Configuração (Mantenha inalterada) ---
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("A chave GEMINI_API_KEY não foi encontrada.")
client = genai.Client(api_key=API_KEY)
TIMEOUT_SECONDS = 300 

# NOVO: Adicione custom_instruction na assinatura da função
async def run_audio_analysis(file_path: str, custom_instruction: str = None) -> dict:
    """Agente: Analisa evidências de áudio e sua relevância jurídica."""
    
    system_instruction = (
        "Você é o Agente de Áudio do Hakim, um perito em análise de evidências auditivas. "
        "Transcreva o áudio e avalie o conteúdo, o contexto, a autenticidade e a relevância "
        "para um caso judicial. Dê uma pontuação de 0 a 100 para o valor probatório da evidência."
    )
    
    # LÓGICA CRÍTICA: Adicionar a instrução customizada
    if custom_instruction:
        system_instruction += f"\n\nInstrução Adicional do Usuário: {custom_instruction}"
        print(f"DEBUG: Aplicando instrução customizada: {custom_instruction}") # Log para debug
    
    uploaded_file = None
    
    try:
        # 1. UPLOAD
        uploaded_file = client.files.upload(file=file_path)
        print(f"DEBUG: Upload Gemini concluído. Nome do arquivo: {uploaded_file.name}")
        
        # 2. ESPERA PELO STATUS ACTIVE (Melhora a resiliência)
        start_time = asyncio.get_event_loop().time()
        while uploaded_file.state != 'ACTIVE':
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > TIMEOUT_SECONDS:
                raise TimeoutError("O tempo limite de processamento do arquivo de áudio foi excedido.")
            
            await asyncio.sleep(5) 
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        # 3. ANÁLISE (usando a system_instruction atualizada)
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
        # 4. LIMPEZA
        if uploaded_file:
            client.files.delete(name=uploaded_file.name)