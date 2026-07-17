# 🏢 Empresa IA Autónoma (Kroot Corp)

<div align="center">
  <img src="https://github.com/calm291094-del/empresa-ia-kroot/blob/main/KrootCorp.png" alt="KrootCorp Logo" width="200">
  <br>
  <strong>
    Sistema multi-agente autónomo que actúa como una consultora de inteligencia artificial. Los agentes investigan, redactan informes, se critican entre sí y "aprenden" de sus errores pasados. 
    Diseñado específicamente para ser **100% gratuito, sin API Keys, y optimizado para ejecutarse en el plan gratuito de Render** sin consumir exceso de memoria RAM.
  </strong>
  <br>
  <em>Inspirado en Tensei Shitara Slime Datta Ken y Overlord</em>
</div>


---

## 🚀 Características Principales

- **Arquitectura Multi-Agente Personalizada:** Flujo secuencial de 3 roles (Investigador, Redactor Ejecutivo y Director de Calidad QA) orquestado con LangChain (LCEL), eliminando la sobrecarga de frameworks pesados.
- **LLM 100% Gratuito y Sin Keys:** Integración directa con **Pollinations.ai** mediante un wrapper personalizado con `requests`. Incluye lógica de **reintentos automáticos** y pausas estratégicas para evadir los límites de tasa (Error 429) en servidores.
- **Dashboard en Tiempo Real:** Interfaz moderna (Tailwind CSS) que muestra el progreso de las fases ("Investigando...", "Redactando...") y añade el informe final **sin necesidad de recargar la página** (AJAX Polling).
- **Aprendizaje Continuo Ligero:** Sistema de memoria basado en archivos JSON locales, diseñado para consumir menos de 5MB de RAM (a prueba de fallos en el tier gratuito de Render).
- **Seguridad:** Panel de control protegido con autenticación por sesiones.

---

## 🔐 Acceso al Panel de Control

- **URL:** `https://empresa-ia-kroot.onrender.com` *(o tu URL personalizada)*
- **Usuario:** `kroot`
- **Contraseña:** `K4815162342`

---

## 🛠️ Stack Tecnológico

| Categoría | Tecnología |
| :--- | :--- |
| **Backend** | FastAPI, Python 3.11 |
| **Orquestación** | LangChain (Custom LCEL Chains) |
| **Motor de IA** | Pollinations.ai (vía `requests` con reintentos) |
| **Memoria** | Persistencia local en JSON (Ultra-ligero) |
| **Frontend** | HTML5, Tailwind CSS, Vanilla JS (Polling en tiempo real) |
| **Despliegue** | Docker, Render (Free Tier) |

---

## ⚙️ ¿Cómo funciona el "Cerebro"?

El sistema no depende de librerías inestables. Utiliza un pipeline de 3 pasos con blindaje contra fallos:

1. **Fase 1 (Investigación):** El agente busca datos y consulta la memoria JSON para evitar errores cometidos en temas similares.
2. *⏸️ Pausa estratégica de 5s* (Para liberar la cola de peticiones del proveedor gratuito).
3. **Fase 2 (Redacción):** Transforma los datos crudos en un informe ejecutivo estructurado en Markdown.
4. *⏸️ Pausa estratégica de 5s*.
5. **Fase 3 (Control de Calidad):** Un agente QA revisa el informe, emite un veredicto y el resultado se guarda en la memoria JSON para el futuro.

*Nota: Si la API gratuita devuelve un error de límite de tasa (429), el sistema lo detecta, espera 5 segundos y reintenta la petición automáticamente hasta 3 veces sin colapsar.*

---

## 🚀 Despliegue en Render (Paso a Paso)

El proyecto está listo para desplegarse en un clic gracias a la configuración de Docker:

1. Haz Fork o clona este repositorio en tu cuenta de GitHub.
2. Ve a [Render.com](https://render.com/) y crea un nuevo **Web Service**.
3. Conecta tu repositorio de GitHub.
4. Render detectará automáticamente el archivo `render.yaml` y el `Dockerfile`.
5. Asegúrate de que el **Plan** seleccionado sea **Free** (el código está optimizado para los 512MB de RAM).
6. Haz clic en **Create Web Service**.

---

## ⚠️ Nota sobre las APIs Gratuitas

Este proyecto utiliza **Pollinations.ai**, un servicio de código abierto que no requiere registro ni claves. Sin embargo, al ser un recurso compartido y gratuito, puede experimentar picos de tráfico. 

La arquitectura de este proyecto incluye **mecanismos de defensa** (reintentos, pausas y validación de respuestas) para mitigar estos problemas. Si en un momento dado falla persistentemente, simplemente espera 1 o 2 minutos y vuelve a intentar la generación del informe.

---

## 📂 Estructura del Proyecto

empresa-ia-kroot/
├── app/
│   ├── main.py             # FastAPI, Auth y Endpoint de estado en vivo (/api/status)
│   ├── llm_config.py       # Motor de IA con reintentos automáticos (Anti-429)
│   ├── memory.py           # Sistema de aprendizaje ligero (JSON)
│   ├── agents.py           # Definición de las cadenas de LangChain (Investigador, Redactor, QA)
│   ├── crew.py             # Orquestador del flujo secuencial con pausas
│   └── templates/          # Plantillas HTML con Tailwind CSS y JS en tiempo real
├── Dockerfile              # Configuración de contenedor optimizada
├── render.yaml             # Blueprint de despliegue para Render
└── requirements.txt        # Dependencias ligeras y estables

⚡ Desarrollado con ❤️ para demostrar que la IA autónoma puede ser accesible, eficiente y gratuita. © 2026 Kroot Corp.

