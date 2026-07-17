import time
import logging
from app.agents import researcher_chain, writer_chain, critic_chain
from app.memory import guardar_aprendizaje, obtener_lessons_learned

logger = logging.getLogger(__name__)

def ejecutar_empresa(topico: str, update_status):
    logger.info("🏗️ Iniciando proceso de agentes personalizados...")
    
    lecciones = obtener_lessons_learned(topico)
    lecciones_txt = f"Evita estos errores pasados: {lecciones}" if lecciones else "No hay errores previos registrados."
    
    # Fase 1
    update_status("🔍 Fase 1: Investigando datos y tendencias...")
    investigacion = researcher_chain.invoke({"topico": topico, "lecciones_previas": lecciones_txt})
    investigacion_texto = investigacion.content if hasattr(investigacion, 'content') else str(investigacion)
    
    # Pausa de 5 segundos para liberar la cola de Pollinations (Anti-429)
    time.sleep(5)
    
    # Fase 2
    update_status("✍️ Fase 2: Redactando informe ejecutivo...")
    informe = writer_chain.invoke({"investigacion": investigacion_texto})
    informe_texto = informe.content if hasattr(informe, 'content') else str(informe)
    
    # Pausa de 5 segundos para liberar la cola de Pollinations (Anti-429)
    time.sleep(5)
    
    # Fase 3
    update_status("🔎 Fase 3: Revisión de calidad y veredicto final...")
    critica = critic_chain.invoke({"informe": informe_texto})
    critica_texto = critica.content if hasattr(critica, 'content') else str(critica)
    
    update_status("💾 Guardando aprendizaje y finalizando...")
    
    resultado_final = f"# 📊 INFORME EJECUTIVO: {topico.upper()}\n\n{informe_texto}\n\n---\n### 📝 Veredicto de Calidad (QA):\n{critica_texto}"
    
    guardar_aprendizaje(
        task_name=topico,
        feedback=critica_texto[:200],
        output=informe_texto[:500]
    )
    
    logger.info("✅ Proceso finalizado con éxito.")
    return resultado_final