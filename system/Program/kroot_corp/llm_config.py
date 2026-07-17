import logging
from typing import Any, List, Optional, Iterator
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

logger = logging.getLogger(__name__)

class FallbackChatModel(BaseChatModel):
    """Modelo de chat que prueba múltiples APIs gratuitas sin key en cascada."""
    
    @property
    def _llm_type(self) -> str:
        return "fallback_free_llm"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        prompt = "\n".join([f"{m.type}: {m.content}" for m in messages])
        response_text = self._get_response_with_fallback(prompt)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response_text))])

    def _get_response_with_fallback(self, prompt: str) -> str:
        # Lista de proveedores a intentar en orden de prioridad
        providers = [
            ("DuckDuckGo AI", self._try_duckduckgo),
            ("Hugging Face (Zephyr)", self._try_huggingface),
            ("G4F (Bing/DuckDuckGo)", self._try_g4f_safe)
        ]

        for name, func in providers:
            try:
                logger.info(f"🔄 Intentando proveedor: {name}")
                result = func(prompt)
                if result and len(result.strip()) > 10:
                    logger.info(f"✅ Éxito con: {name}")
                    return result
                else:
                    logger.warning(f"⚠️ {name} devolvió una respuesta vacía o muy corta.")
            except Exception as e:
                logger.warning(f"⚠️ Fallo en {name}: {str(e)[:100]}...")
                continue

        raise Exception("Todos los proveedores gratuitos fallaron. Por favor, intenta de nuevo en unos minutos.")

    def _try_duckduckgo(self, prompt: str) -> str:
        """Proveedor 1: DuckDuckGo AI (Muy estable, sin key)"""
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            # Usamos la función de chat de DDGS
            response = ddgs.chat(prompt)
            return response

    def _try_huggingface(self, prompt: str) -> str:
        """Proveedor 2: Hugging Face Inference API (Modo no autenticado)"""
        from huggingface_hub import InferenceClient
        # Usamos un modelo pequeño y rápido que permite peticiones sin token
        client = InferenceClient(model="HuggingFaceH4/zephyr-7b-beta")
        response = client.text_generation(
            prompt, 
            max_new_tokens=500, 
            temperature=0.7,
            do_sample=True
        )
        return response

    def _try_g4f_safe(self, prompt: str) -> str:
        """Proveedor 3: G4F (Carga diferida para evitar crashes de importación)"""
        import g4f
        from g4f.Provider import DuckDuckGo, Bing
        
        # Forzamos solo proveedores estables, ignorando el resto
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            provider=DuckDuckGo, # Intentamos primero con DDG dentro de g4f
            timeout=45
        )
        return response

# Instancia global que usará CrewAI
llm_instance = FallbackChatModel()