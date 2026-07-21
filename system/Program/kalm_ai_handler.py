#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALM AI - Handler para integrar en el servidor principal
"""

import json
import time
import requests
import sys
import os
import subprocess
from pathlib import Path

# ============================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================
def instalar_dependencias():
    for pkg in ["requests", "duckduckgo-search"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"Instalando {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

instalar_dependencias()

# ============================================================
# 2. PROVEEDORES DE IA
# ============================================================
class IAProvider:
    @staticmethod
    def pollinations(prompt, model="openai"):
        """Pollinations AI - Gratuito, sin API key"""
        url = "https://text.pollinations.ai/openai"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise Exception("Respuesta sin choices")
            
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            raise Exception("Timeout conectando con Pollinations")
        except Exception as e:
            raise Exception(f"Pollinations falló: {str(e)}")
    
    @staticmethod
    def duckduckgo(prompt):
        """DuckDuckGo AI - Gratuito"""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                response = ddgs.chat(prompt)
                return response
        except Exception as e:
            raise Exception(f"DuckDuckGo falló: {str(e)}")
    
    @staticmethod
    def get_response(prompt, model="openai"):
        """Obtiene respuesta de múltiples proveedores"""
        providers = [
            ("Pollinations", lambda: IAProvider.pollinations(prompt, model)),
            ("DuckDuckGo", lambda: IAProvider.duckduckgo(prompt)),
        ]
        
        for name, func in providers:
            try:
                print(f"🔄 Intentando con {name}...")
                result = func()
                if result and len(result.strip()) > 10:
                    print(f"✅ Éxito con {name}")
                    return result
            except Exception as e:
                print(f"❌ {name} falló: {e}")
                time.sleep(1)
                continue
        
        return "❌ Error: Todos los proveedores fallaron. Intenta de nuevo."

# ============================================================
# 3. FUNCIONES HANDLER
# ============================================================

def serve_kalm_ai_page():
    """Sirve la página HTML de Kalm AI"""
    try:
        views_dir = Path(__file__).parent.parent.parent / "views"
        html_file = views_dir / "kalm_ai.html"
        if html_file.exists():
            return html_file.read_text(encoding="utf-8")
        else:
            return """
            <html><body style="background:#0a0514;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
                <div style="text-align:center;">
                    <h1 style="color:#da70d6;">🧠 Kalm AI</h1>
                    <p style="color:#9370db;">Error: kalm_ai.html no encontrado</p>
                </div>
            </body></html>
            """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

def handle_generar(data):
    """Genera trabajos/informes"""
    tema = data.get('tema', '').strip()
    modelo = data.get('modelo', 'openai')
    tipo = data.get('tipo', 'chat')
    
    if not tema:
        return {"error": "Tema vacío"}, 400
    
    if tipo == 'chat':
        prompt = f"""Escribe un trabajo académico completo sobre: {tema}
        Estructura:
        ## INTRODUCCIÓN
        ## INTRODUCTION (in English)
        ## DESARROLLO
        ## CONCLUSIONES
        ## BIBLIOGRAFÍA
        """
    else:
        prompt = f"""Genera un informe ejecutivo sobre: {tema}
        Estructura:
        ## INTRODUCCIÓN
        ## PUNTOS CLAVE
        ## CONCLUSIONES
        ## RECOMENDACIONES
        """
    
    try:
        print(f"📝 Generando: {tema[:50]}...")
        resultado = IAProvider.get_response(prompt, modelo)
        return {"resultado": resultado}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def handle_chat(data):
    """Chat libre"""
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')
    
    if not mensaje:
        return {"error": "Mensaje vacío"}, 400
    
    try:
        print(f"💬 Chat: {mensaje[:50]}...")
        respuesta = IAProvider.get_response(mensaje, modelo)
        return {"respuesta": respuesta}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def handle_health():
    """Health check"""
    return {"status": "ok", "message": "Kalm AI running"}, 200
