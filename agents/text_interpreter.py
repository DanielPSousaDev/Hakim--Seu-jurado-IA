# agents/text_interpreter.py
import os
import json
from google import genai
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

async def run_text_analysis(file_path: str) -> dict:
    """Agente: Interpreta documentos (texto/PDF) e analisa a clareza jurídica."""
    
    system_instruction = (
        "Você é o Agente Intérprete de Teste do Hakim. Sua especialidade é análise de documentos jurídicos. "
        "Avalie o documento (petição, contrato, tese) em termos de clareza, coerência e consistência legal. "
        "Forneça uma pontuação de 0 a 100 e um feedback detalhado, focando na estrutura e persuasão jurídica."
    )
    
    uploaded_file = client.files.upload(file=file_path)
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, "Execute a análise jurídica completa deste documento."],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=get_response_schema("Análise de Clareza e Consistência Jurídica")
            ),
        )
        return json.loads(response.text)
    finally:
        client.files.delete(name=uploaded_file.name)