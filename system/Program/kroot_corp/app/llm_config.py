import logging
import urllib.parse
import time
import random
import requests
from typing import Any, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

logger = logging.getLogger(__name__)

class PollinationsChatModel(BaseChatModel):
    model: str = "openai"
    
    @property
    def _llm_type(self) -> str:
        return "pollinations_free_chat"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        prompt = "\n".join([f"{m.type}: {m.content}" for m in messages])
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                encoded_prompt = urllib.parse.quote(prompt)
                seed = random.randint(1, 10000)
                url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&seed={seed}&json=false"
                
                logger.info(f"🔄 Consultando a Pollinations.ai (Intento {attempt + 1}/{max_retries})...")
                
                response = requests.get(url, timeout=60)
                
                if response.status_code == 429:
                    logger.warning("⚠️ Límite de tasa (429) detectado. Esperando 5 segundos...")
                    time.sleep(5)
                    continue
                    
                if response.status_code == 200:
                    text = response.text.strip()
                    if len(text) > 15:
                        logger.info("✅ Respuesta recibida con éxito.")
                        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])
                    else:
                        raise Exception("La respuesta de la IA fue demasiado corta.")
                else:
                    raise Exception(f"Error HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ Error final al consultar Pollinations: {str(e)}")
                    raise Exception(f"Fallo en la IA gratuita tras {max_retries} intentos: {str(e)}")
                
                logger.warning(f"⚠️ Intento {attempt + 1} falló: {str(e)[:80]}... Reintentando en 5s.")
                time.sleep(5)

llm_instance = PollinationsChatModel()