#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALM AI - Handler para integrar en el servidor principal
SOLO CORREGIDO: DEVUELVE JSON EN LUGAR DE HTML
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
            print(f"[KalmAI] Instalando {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

instalar_dependencias()

# ============================================================
# 2. HTML (FALLBACK)
# ============================================================
def get_html_template():
    return """<html><body style="background:#0a0514;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
        <div style="text-align:center;"><h1 style="color:#da70d6;">🧠 Kalm AI</h1>
        <p style="color:#9370db;">Error: views/kalm_ai.html no encontrado</p></div>
    </body></html>"""

# ============================================================
# 3. PROVEEDORES DE IA
# ============================================================
class IAProvider:
    @staticmethod
    def pollinations(prompt, model="openai"):
        url = "https://text.pollinations.ai/openai"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
        try:
            print(f"[KalmAI] Llamando a Pollinations...")
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            if "choices" not in data or not data["choices"]:
                raise Exception("Respuesta sin choices")
            resultado = data["choices"][0]["message"]["content"]
            print(f"[KalmAI] Pollinations respondio con {len(resultado)} caracteres")
            return resultado
        except Exception as e:
            raise Exception(f"Pollinations fallo: {str(e)}")

    @staticmethod
    def duckduckgo(prompt):
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                response = ddgs.chat(prompt)
                return response
        except Exception as e:
            raise Exception(f"DuckDuckGo fallo: {str(e)}")

    @staticmethod
    def get_response(prompt, model="openai"):
        providers = [
            ("Pollinations", lambda: IAProvider.pollinations(prompt, model)),
            ("DuckDuckGo", lambda: IAProvider.duckduckgo(prompt)),
        ]
        for name, func in providers:
            try:
                print(f"[KalmAI] Intentando con {name}...")
                result = func()
                if result and len(result.strip()) > 10:
                    print(f"[KalmAI] Exito con {name}")
                    return result
            except Exception as e:
                print(f"[KalmAI] {name} fallo: {e}")
                time.sleep(1)
                continue
        return "Error: Todos los proveedores fallaron. Intenta de nuevo."

# ============================================================
# 4. FUNCIONES HANDLER - CORREGIDAS PARA DEVOLVER JSON
# ============================================================

def serve_kalm_ai_page():
    """Sirve la pagina HTML de Kalm AI desde views/kalm_ai.html"""
    try:
        views_dir = Path(__file__).parent.parent.parent / "views"
        html_file = views_dir / "kalm_ai.html"
        if html_file.exists():
            print("[KalmAI] Sirviendo desde views/kalm_ai.html")
            return html_file.read_text(encoding="utf-8")
        else:
            print("[KalmAI] views/kalm_ai.html no existe, usando fallback")
            return get_html_template()
    except Exception as e:
        print(f"[KalmAI] Error: {e}")
        return get_html_template()

def handle_generar(data):
    """Genera trabajos/informes - DEVUELVE JSON VALIDO"""
    tema = data.get('tema', '').strip()
    modelo = data.get('modelo', 'openai')
    tipo = data.get('tipo', 'chat')

    print(f"[KalmAI] generar: tema='{tema}'")

    if not tema:
        return {"error": "El tema no puede estar vacio"}, 400

    if tipo == 'chat':
        prompt = f"""Escribe un trabajo academico completo y profesional sobre: {tema}

ESTRUCTURA EXACTA:
## INTRODUCCION
## INTRODUCTION (in English)
## DESARROLLO
## CONCLUSIONES
## BIBLIOGRAFIA

El trabajo debe ser completo, bien estructurado, con lenguaje formal y academico."""
    else:
        prompt = f"""Genera un informe ejecutivo profesional sobre: {tema}

ESTRUCTURA EXACTA:
## INTRODUCCION
## PUNTOS CLAVE
## CONCLUSIONES
## RECOMENDACIONES

El informe debe ser ejecutivo, directo y orientado a la toma de decisiones."""

    try:
        resultado = IAProvider.get_response(prompt, modelo)
        print(f"[KalmAI] Resultado obtenido: {len(resultado)} caracteres")
        # ═══ ESTO ES LO QUE SE CORRIGIO: DEVOLVER JSON ═══
        return {"resultado": resultado}, 200
    except Exception as e:
        print(f"[KalmAI] Error: {e}")
        return {"error": str(e)}, 500

def handle_chat(data):
    """Chat libre - DEVUELVE JSON VALIDO"""
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')

    print(f"[KalmAI] chat: mensaje='{mensaje[:50]}...'")

    if not mensaje:
        return {"error": "El mensaje no puede estar vacio"}, 400

    try:
        respuesta = IAProvider.get_response(mensaje, modelo)
        print(f"[KalmAI] Respuesta obtenida: {len(respuesta)} caracteres")
        # ═══ ESTO ES LO QUE SE CORRIGIO: DEVOLVER JSON ═══
        return {"respuesta": respuesta}, 200
    except Exception as e:
        print(f"[KalmAI] Error: {e}")
        return {"error": str(e)}, 500

def handle_health():
    return {"status": "ok", "message": "Kalm AI running"}, 200
