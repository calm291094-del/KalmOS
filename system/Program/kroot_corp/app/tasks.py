from crewai import Task
from app.agents import investigador, redactor, critico
from app.memory import obtener_lessons_learned

def crear_tareas(topico: str):
    lessons = obtener_lessons_learned(topico)
    
    tarea_investigacion = Task(
        description=f"Investiga a fondo sobre: '{topico}'. {f'Evita estos errores pasados: {lessons}' if lessons else ''}",
        expected_output="Una lista detallada con 5 puntos clave y datos reales.",
        agent=investigador
    )

    tarea_redaccion = Task(
        description="Redacta un informe ejecutivo profesional basado en la investigación.",
        expected_output="Un informe en Markdown con Introducción, Puntos Clave y Conclusiones.",
        agent=redactor,
        context=[tarea_investigacion]
    )

    tarea_critica = Task(
        description="Revisa el informe. Si es bueno, apruébalo. Si es malo, explica por qué.",
        expected_output="Un dictamen de calidad (APROBADO o RECHAZADO) con feedback.",
        agent=critico,
        context=[tarea_redaccion]
    )

    return [tarea_investigacion, tarea_redaccion, tarea_critica]