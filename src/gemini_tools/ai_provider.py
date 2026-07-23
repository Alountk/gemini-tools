import os
import json
from abc import ABC, abstractmethod
from typing import List, Callable, Any
import google.generativeai as genai
from openai import OpenAI

class BaseAIProvider(ABC):
    """Base interface for AI providers with tool support."""
    
    @abstractmethod
    def run_with_tools(self, prompt: str, tools: List[Callable]) -> str:
        """Run a request and let the AI decide whether to call tools."""
        pass


# ---------------------------------------------------------------------------
# 1. Google Gemini provider
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
        # Enable automatic function execution in the Gemini SDK
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt)
        return response.text


# ---------------------------------------------------------------------------
# 2. Local AI provider (Ollama, LM Studio, vLLM) using OpenAI API
# ---------------------------------------------------------------------------
class LocalAIProvider(BaseAIProvider):
    def __init__(self, base_url: str = "http://localhost:11434/v1", model_name: str = "llama3.1"):
        self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model_name = model_name

    def run_with_tools(self, prompt: str, tools: List[Callable]) -> str:
        # 1. Convert Python functions to OpenAI-compatible JSON schemas
        tool_map = {func.__name__: func for func in tools}
        openai_tools = []
        
        # Basic mapping for the PDF tool MVP
        for func in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": func.__name__,
                    "description": func.__doc__ or "Local function",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nombre_archivo": {"type": "string", "description": "PDF filename"},
                            "titulo": {"type": "string", "description": "Main PDF title"},
                            "contenido_markdown": {"type": "string", "description": "Markdown content"}
                        },
                        "required": ["nombre_archivo", "titulo", "contenido_markdown"]
                    }
                }
            })

        messages = [{"role": "user", "content": prompt}]
        
        # 2. First call to the local AI
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 3. If the local model decides to call a function
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                if func_name in tool_map:
                    # Actual execution of the local function (PDF creation)
                    resultado = tool_map[func_name](**func_args)
                    return f"🤖 [Local AI] {resultado}"

        return response_message.content or "Processed without tool invocation."


# ---------------------------------------------------------------------------
# Factory: Load the provider configured in .env
# ---------------------------------------------------------------------------
def get_ai_provider() -> BaseAIProvider:
    provider_type = os.environ.get("AI_PROVIDER", "gemini").lower()
    
    if provider_type == "local":
        base_url = os.environ.get("LOCAL_AI_URL", "http://localhost:11434/v1")
        model = os.environ.get("LOCAL_AI_MODEL", "llama3.1")
        print(f"⚙️ Local AI mode ({model} at {base_url})")
        return LocalAIProvider(base_url=base_url, model_name=model)
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ Error: GEMINI_API_KEY was not found in the environment or .env")
        print("☁️ Google Gemini API mode")
        return GeminiProvider(api_key=api_key)