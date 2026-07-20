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
        url = "https://text.pollinations.ai/openai"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    @staticmethod
    def duckduckgo(prompt):
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                response = ddgs.chat(prompt)
                return response
        except:
            raise Exception("DuckDuckGo fallo")
    
    @staticmethod
    def get_response(prompt, model="openai"):
        providers = [
            ("Pollinations", lambda: IAProvider.pollinations(prompt, model)),
            ("DuckDuckGo", lambda: IAProvider.duckduckgo(prompt)),
        ]
        
        for name, func in providers:
            try:
                print(f"Intentando con {name}...")
                result = func()
                if result and len(result.strip()) > 10:
                    print(f"Exito con {name}")
                    return result
            except Exception as e:
                print(f"{name} fallo: {e}")
                time.sleep(1)
                continue
        
        return "Error: Todos los proveedores fallaron. Intenta de nuevo."

# ============================================================
# 3. FUNCIONES HANDLER PARA EL SERVIDOR
# ============================================================

def serve_kalm_ai_page():
    """Sirve la página HTML de Kalm AI desde el archivo views/kalm_ai.html"""
    try:
        views_dir = Path(__file__).parent.parent.parent / "views"
        html_file = views_dir / "kalm_ai.html"
        if html_file.exists():
            return html_file.read_text(encoding="utf-8")
        else:
            return "<h1>Error: kalm_ai.html no encontrado</h1>"
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

def handle_generar(data):
    """Maneja la generacion de trabajos/informes"""
    tema = data.get('tema', '').strip()
    modelo = data.get('modelo', 'openai')
    tipo = data.get('tipo', 'chat')
    
    if not tema:
        return {"error": "Tema vacio"}, 400
    
    if tipo == 'chat':
        prompt = f"""
        Escribe un trabajo academico completo sobre: {tema}
        Estructura: INTRODUCCION, INTRODUCTION (in English), DESARROLLO, CONCLUSIONES, BIBLIOGRAFIA
        """
    else:
        prompt = f"""
        Genera un informe ejecutivo sobre: {tema}
        Estructura: INTRODUCCION, PUNTOS CLAVE, CONCLUSIONES, RECOMENDACIONES
        """
    
    try:
        resultado = IAProvider.get_response(prompt, modelo)
        return {"resultado": resultado}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def handle_chat(data):
    """Maneja el chat libre"""
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')
    
    if not mensaje:
        return {"error": "Mensaje vacio"}, 400
    
    try:
        respuesta = IAProvider.get_response(mensaje, modelo)
        return {"respuesta": respuesta}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def handle_health():
    """Health check"""
    return {"status": "ok", "message": "Kalm AI running"}, 200
