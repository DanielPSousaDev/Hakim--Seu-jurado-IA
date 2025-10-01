# core/utils.py
import magic
from google.genai import types

def detect_file_type(file_path: str) -> str:
    """Detecta o tipo MIME (MIME type) de um arquivo de forma robusta."""
    return magic.from_file(file_path, mime=True)

def get_response_schema(task_description: str) -> types.Schema:
    """Cria um esquema JSON forçado para a saída do Gemini."""
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "score": types.Schema(
                type=types.Type.INTEGER,
                description=f"A pontuação profissional de 0 a 100 para a {task_description}."
            ),
            "feedback": types.Schema(
                type=types.Type.STRING,
                description=f"O feedback jurídico detalhado sobre a {task_description} com sugestões."
            ),
        },
        required=["score", "feedback"]
    )