#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALM AI - Handler para integrar en el servidor principal
VERSIÓN MEJORADA CON LOGS Y MANEJO DE ERRORES
"""

import json
import time
import requests
import sys
import os
import subprocess
import traceback
from pathlib import Path

# ============================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================
def instalar_dependencias():
    for pkg in ["requests", "duckduckgo-search"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Instalando {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

instalar_dependencias()

# ============================================================
# 2. LOGGING
# ============================================================
def log(msg, level="INFO"):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] [KalmAI] {msg}")
    sys.stdout.flush()

# ============================================================
# 3. PROVEEDORES DE IA (MEJORADOS)
# ============================================================
class IAProvider:
    @staticmethod
    def pollinations(prompt, model="openai"):
        """Proveedor Pollinations AI - Gratuito, sin API key"""
        url = "https://text.pollinations.ai/openai"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
        
        log(f"🌐 Llamando a Pollinations con modelo {model}...", "DEBUG")
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if "choices" not in data or not data["choices"]:
            raise Exception("Respuesta de Pollinations sin choices")
        
        return data["choices"][0]["message"]["content"]
    
    @staticmethod
    def duckduckgo(prompt):
        """Proveedor DuckDuckGo AI - Gratuito"""
        log("🦆 Llamando a DuckDuckGo AI...", "DEBUG")
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                response = ddgs.chat(prompt)
                return response
        except ImportError:
            raise Exception("DuckDuckGo no disponible")
        except Exception as e:
            raise Exception(f"DuckDuckGo falló: {e}")
    
    @staticmethod
    def get_response(prompt, model="openai"):
        """Obtiene respuesta de múltiples proveedores con fallback"""
        providers = [
            ("Pollinations", lambda: IAProvider.pollinations(prompt, model)),
            ("DuckDuckGo", lambda: IAProvider.duckduckgo(prompt)),
        ]
        
        errors = []
        for name, func in providers:
            try:
                log(f"🔄 Intentando con {name}...", "INFO")
                result = func()
                if result and len(result.strip()) > 10:
                    log(f"✅ Éxito con {name}", "INFO")
                    return result
            except Exception as e:
                error_msg = f"{name} falló: {str(e)}"
                log(f"❌ {error_msg}", "WARN")
                errors.append(error_msg)
                time.sleep(1)
                continue
        
        # Si todos fallan, devolver un error detallado
        error_summary = "\n".join(errors)
        return f"❌ Error: Todos los proveedores fallaron.\nDetalles:\n{error_summary}\n\n💡 Sugerencia: Intenta de nuevo en unos minutos."

# ============================================================
# 4. FUNCIONES HANDLER PARA EL SERVIDOR
# ============================================================

def serve_kalm_ai_page():
    """Sirve la página HTML de Kalm AI desde views/kalm_ai.html"""
    try:
        views_dir = Path(__file__).parent.parent.parent / "views"
        html_file = views_dir / "kalm_ai.html"
        if html_file.exists():
            log(f"📄 Sirviendo kalm_ai.html desde {html_file}", "DEBUG")
            return html_file.read_text(encoding="utf-8")
        else:
            log(f"❌ kalm_ai.html no encontrado en {html_file}", "ERROR")
            return """
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"><title>Kalm AI</title></head>
            <body style="background:#0a0514;color:#e6e6fa;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;">
                <h1 style="color:#da70d6;">🧠 Kalm AI</h1>
                <p style="color:#9370db;">Error: kalm_ai.html no encontrado</p>
                <p style="color:#6a0dad;font-size:12px;">Asegúrate de que el archivo existe en views/kalm_ai.html</p>
            </body>
            </html>
            """
    except Exception as e:
        log(f"❌ Error sirviendo kalm_ai.html: {e}", "ERROR")
        return f"<h1>Error: {str(e)}</h1>"

def handle_generar(data):
    """Maneja la generación de trabajos/informes"""
    tema = data.get('tema', '').strip()
    modelo = data.get('modelo', 'openai')
    tipo = data.get('tipo', 'chat')
    
    log(f"📝 Generando {tipo} sobre: '{tema}' con modelo {modelo}", "INFO")
    
    if not tema:
        return {"error": "El tema no puede estar vacío"}, 400
    
    # Prompts optimizados
    if tipo == 'chat':
        prompt = f"""Escribe un trabajo académico completo y profesional sobre el siguiente tema:

TEMA: {tema}

ESTRUCTURA EXACTA (usa estos títulos):
## INTRODUCCIÓN
### Contexto y relevancia del tema

## INTRODUCTION (in English)
### Context and relevance in English

## DESARROLLO
### Análisis detallado del tema
### Puntos clave y argumentos
### Evidencia y ejemplos

## CONCLUSIONES
### Resumen de hallazgos
### Implicaciones y reflexiones finales

## BIBLIOGRAFÍA
### Fuentes consultadas (formato APA)

El trabajo debe ser completo, bien estructurado, con un lenguaje formal y académico. Incluye ejemplos concretos y análisis profundos.
"""
    else:
        prompt = f"""Genera un informe ejecutivo profesional y completo sobre el siguiente tema:

TEMA: {tema}

ESTRUCTURA EXACTA:
## INTRODUCCIÓN
### Contexto y objetivo del informe

## PUNTOS CLAVE
### 5-7 puntos fundamentales con análisis detallado

## CONCLUSIONES
### Hallazgos principales y su importancia

## RECOMENDACIONES
### Acciones concretas basadas en el análisis

El informe debe ser ejecutivo, directo, con lenguaje formal y orientado a la toma de decisiones. Incluye datos relevantes y argumentos sólidos.
"""
    
    try:
        log(f"⏳ Enviando prompt a IA...", "DEBUG")
        resultado = IAProvider.get_response(prompt, modelo)
        log(f"✅ Respuesta obtenida ({len(resultado)} caracteres)", "INFO")
        return {"resultado": resultado}, 200
    except Exception as e:
        log(f"❌ Error en handle_generar: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        return {"error": f"Error interno: {str(e)}"}, 500

def handle_chat(data):
    """Maneja el chat libre"""
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')
    
    log(f"💬 Chat con modelo {modelo}: '{mensaje[:50]}...'", "INFO")
    
    if not mensaje:
        return {"error": "El mensaje no puede estar vacío"}, 400
    
    try:
        log(f"⏳ Enviando chat a IA...", "DEBUG")
        respuesta = IAProvider.get_response(mensaje, modelo)
        log(f"✅ Chat respuesta obtenida ({len(respuesta)} caracteres)", "INFO")
        return {"respuesta": respuesta}, 200
    except Exception as e:
        log(f"❌ Error en handle_chat: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        return {"error": f"Error interno: {str(e)}"}, 500

def handle_health():
    """Health check"""
    return {"status": "ok", "message": "Kalm AI running"}, 200
