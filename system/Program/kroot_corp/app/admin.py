from fastapi import FastAPI, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="kroot_super_secret_key_4815162342")
templates = Jinja2Templates(directory="app/templates")

USERS = {"kroot": "K4815162342"}
REPORT_HISTORY = [] 

# Estado en vivo de la tarea actual
ACTIVE_TASK = {
    "topico": "",
    "phase": "Esperando...",
    "estado": "Idle",
    "result": ""
}

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")
    return user

def tarea_en_background(topico: str):
    logger.info(f"🚀 INICIANDO AGENTES PARA: '{topico}'")
    
    # Función callback para que crew.py actualice la fase en tiempo real
    def update_status(phase: str):
        ACTIVE_TASK["phase"] = phase
        logger.info(f"📡 Estado actualizado: {phase}")

    ACTIVE_TASK["topico"] = topico
    ACTIVE_TASK["estado"] = "Procesando"
    ACTIVE_TASK["result"] = "Iniciando motores de IA..."
    ACTIVE_TASK["phase"] = "Preparando entorno..."
    
    try:
        from app.crew import ejecutar_empresa
        resultado = ejecutar_empresa(topico, update_status)
        
        ACTIVE_TASK["estado"] = "Éxito"
        ACTIVE_TASK["result"] = resultado
        ACTIVE_TASK["phase"] = "Completado"
        
        REPORT_HISTORY.append({"topico": topico, "resultado": resultado, "estado": "Éxito"})
        logger.info(f"✅ AGENTES TERMINARON CON ÉXITO PARA: '{topico}'")
                
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"❌ ERROR CRÍTICO EN AGENTES PARA '{topico}':\n{error_trace}")
        
        ACTIVE_TASK["estado"] = "Fallo"
        ACTIVE_TASK["result"] = f"Error: {str(e)}"
        ACTIVE_TASK["phase"] = "Fallido"
        
        REPORT_HISTORY.append({
            "topico": topico, 
            "resultado": f"Error: {str(e)}\n\n(Revisa los logs de Render para más detalles)", 
            "estado": "Fallo"
        })

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
async def get_status(user: str = Depends(get_current_user)):
    """Endpoint para que el frontend consulte el estado en tiempo real"""
    return ACTIVE_TASK

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) == password:
        request.session["user"] = username
        logger.info(f"✅ Usuario {username} ha iniciado sesión.")
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": "Credenciales inválidas"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user, 
        "reports": REPORT_HISTORY[::-1]
    })

@app.post("/run_crew")
async def run_crew(
    request: Request, 
    background_tasks: BackgroundTasks,
    topico: str = Form(...), 
    user: str = Depends(get_current_user)
):
    logger.info(f"📥 Petición recibida para ejecutar: '{topico}'")
    background_tasks.add_task(tarea_en_background, topico)
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)