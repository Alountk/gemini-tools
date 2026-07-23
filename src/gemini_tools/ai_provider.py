import os
import json
from abc import ABC, abstractmethod
from typing import List, Callable, Any
import google.generativeai as genai
from openai import OpenAI

class BaseAIProvider(ABC):
    """Interfaz base para proveedores de IA con soporte de herramientas."""
    
    @abstractmethod
    def run_with_tools(self, prompt: str, tools: List[Callable]) -> str:
        """Ejecuta una petición permitiendo que la IA decida invocar herramientas."""
        pass


# ---------------------------------------------------------------------------
# 1. Proveedor para Google Gemini
# ---------------------------------------------------------------------------
class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def run_with_tools(self, prompt: str, tools: List[Callable]) -> str:
        model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=tools
        )
        # Habilitar la ejecución automática de funciones en el SDK de Gemini
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt)
        return response.text


# ---------------------------------------------------------------------------
# 2. Proveedor para IA Local (Ollama, LM Studio, vLLM) usando API OpenAI
# ---------------------------------------------------------------------------
class LocalAIProvider(BaseAIProvider):
    def __init__(self, base_url: str = "http://localhost:11434/v1", model_name: str = "llama3.1"):
        self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model_name = model_name

    def run_with_tools(self, prompt: str, tools: List[Callable]) -> str:
        # 1. Convertir funciones de Python a esquemas JSON compatibles con OpenAI
        tool_map = {func.__name__: func for func in tools}
        openai_tools = []
        
        # Mapeo básico para el MVP de la herramienta de PDF
        for func in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": func.__name__,
                    "description": func.__doc__ or "Función local",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nombre_archivo": {"type": "string", "description": "Nombre del archivo PDF"},
                            "titulo": {"type": "string", "description": "Título principal del PDF"},
                            "contenido_markdown": {"type": "string", "description": "Contenido en Markdown"}
                        },
                        "required": ["nombre_archivo", "titulo", "contenido_markdown"]
                    }
                }
            })

        messages = [{"role": "user", "content": prompt}]
        
        # 2. Primera llamada a la IA local
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 3. Si el modelo local decide llamar a una función
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                if func_name in tool_map:
                    # Ejecución real de la función local (creación del PDF)
                    resultado = tool_map[func_name](**func_args)
                    return f"🤖 [IA Local] {resultado}"

        return response_message.content or "Procesado sin invocación de herramientas."


# ---------------------------------------------------------------------------
# Factory: Carga el proveedor configurado en el .env
# ---------------------------------------------------------------------------
def get_ai_provider() -> BaseAIProvider:
    provider_type = os.environ.get("AI_PROVIDER", "gemini").lower()
    
    if provider_type == "local":
        base_url = os.environ.get("LOCAL_AI_URL", "http://localhost:11434/v1")
        model = os.environ.get("LOCAL_AI_MODEL", "llama3.1")
        print(f"⚙️ Modo IA Local ({model} en {base_url})")
        return LocalAIProvider(base_url=base_url, model_name=model)
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ Error: No se encontró GEMINI_API_KEY en el entorno o .env")
        print("☁️ Modo Google Gemini API")
        return GeminiProvider(api_key=api_key)