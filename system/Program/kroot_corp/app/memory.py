import json
import os
import logging

logger = logging.getLogger(__name__)
MEMORY_FILE = "empresa_memoria.json"

def _cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Si el archivo está vacío, devolvemos un diccionario vacío
                if not content:
                    logger.warning("⚠️ Archivo de memoria vacío. Reiniciando memoria.")
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Archivo de memoria corrupto. Reiniciando: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Error inesperado al cargar memoria: {e}")
            return {}
    return {}

def _guardar_memoria(data):
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ Error al guardar memoria: {e}")

def guardar_aprendizaje(task_name: str, feedback: str, output: str):
    data = _cargar_memoria()
    if task_name not in data:
        data[task_name] = []
    
    data[task_name].append({
        "feedback": feedback, 
        "output_resumen": output[:300] 
    })
    
    # Mantenemos solo las últimas 5 lecciones para no inflar el archivo
    data[task_name] = data[task_name][-5:] 
    _guardar_memoria(data)

def obtener_lessons_learned(task_name: str) -> str:
    data = _cargar_memoria()
    lessons = data.get(task_name, [])
    if lessons:
        return "\n".join([f"- {l['feedback']}: {l['output_resumen']}" for l in lessons[-2:]])
    return ""