#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALM AI - Handler para integrar en el servidor principal
VERSION CORREGIDA v3.0 - CON STREAMING Y MEJOR MANEJO DE ERRORES
"""

import json
import time
import sys
import os
import subprocess
from pathlib import Path

# ============================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================
def instalar_dependencias():
    """Instala dependencias necesarias de forma silenciosa"""
    for pkg in ["requests", "duckduckgo-search"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"[KalmAI] Instalando {pkg}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg, "--quiet", "--no-warn-script-location"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"[KalmAI] {pkg} instalado correctamente")
            except subprocess.CalledProcessError as e:
                print(f"[KalmAI] Error instalando {pkg}: {e}")

instalar_dependencias()

import requests

# ============================================================
# 2. HTML FALLBACK
# ============================================================
def get_html_template():
    """HTML de emergencia si kalm_ai.html no existe"""
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Kalm AI - Error</title></head>
<body style="background:#0a0514;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;margin:0;">
<div style="text-align:center;max-width:500px;padding:20px;">
<h1 style="color:#da70d6;font-size:48px;margin-bottom:16px;">🧠 Kalm AI</h1>
<p style="color:#9370db;font-size:16px;margin-bottom:12px;">El archivo de interfaz no se encontró.</p>
<p style="color:#6a5acd;font-size:13px;">Verifica que <code style="background:rgba(106,13,173,0.3);padding:2px 6px;border-radius:3px;">views/kalm_ai.html</code> exista en tu proyecto.</p>
<p style="color:#4a3a6a;font-size:11px;margin-top:24px;">Kalm OS v4.3</p>
</div>
</body></html>"""


# ============================================================
# 3. PROVEEDORES DE IA
# ============================================================
class IAProvider:
    """Proveedores de IA con fallback automático y manejo robusto de errores"""

    @staticmethod
    def pollinations(prompt, model="openai", stream=False):
        url = "https://text.pollinations.ai/openai"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "KalmOS/4.3"
        }

        print(f"[KalmAI] Pollinations: modelo={model}, stream={stream}")

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60, stream=stream)

            # ═══ DETECTAR ERRORES HTTP (502, 503, etc.) ═══
            if response.status_code >= 400:
                error_body = ""
                try:
                    error_body = response.text[:500]
                except:
                    pass
                print(f"[KalmAI] Pollinations HTTP {response.status_code}: {error_body[:200]}")
                raise Exception(f"Pollinations HTTP {response.status_code}")

            # Verificar que es JSON, no HTML de error
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type and not stream:
                print(f"[KalmAI] Pollinations devolvió HTML en vez de JSON")
                raise Exception("Pollinations devolvió HTML (servidor en error)")

            if stream:
                return response
            else:
                data = response.json()
                if "choices" not in data or not data["choices"]:
                    raise Exception("Respuesta vacía de Pollinations")
                resultado = data["choices"][0]["message"]["content"]
                print(f"[KalmAI] Pollinations OK: {len(resultado)} chars")
                return resultado

        except requests.exceptions.Timeout:
            raise Exception("Timeout: Pollinations tardó demasiado")
        except requests.exceptions.ConnectionError:
            raise Exception("Sin conexión a Pollinations")
        except Exception as e:
            if "HTTP" in str(e) or "HTML" in str(e) or "Timeout" in str(e) or "Sin conexión" in str(e):
                raise
            raise Exception(f"Pollinations error: {str(e)}")

    @staticmethod
    def pollinations_stream(prompt, model="openai"):
        """Generator para streaming desde Pollinations"""
        try:
            response = IAProvider.pollinations(prompt, model, stream=True)
            full_text = ""

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue

                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        full_text += content
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

            if not full_text:
                raise Exception("Stream vacío de Pollinations")

            print(f"[KalmAI] Stream completado: {len(full_text)} chars")

        except requests.exceptions.Timeout:
            yield "\n\n⚠️ *Tiempo de espera agotado.*"
        except requests.exceptions.ConnectionError:
            raise Exception("Sin conexión a Pollinations")
        except Exception as e:
            # Si ya es un error conocido, relanzar
            if any(x in str(e) for x in ["HTTP", "HTML", "vacío", "Sin conexión"]):
                raise
            raise Exception(f"Stream error: {str(e)}")

    @staticmethod
    def duckduckgo(prompt):
        try:
            from duckduckgo_search import DDGS
            print(f"[KalmAI] DuckDuckGo fallback...")
            with DDGS() as ddgs:
                response = ddgs.chat(prompt)
                if response and len(response.strip()) > 10:
                    print(f"[KalmAI] DuckDuckGo OK: {len(response)} chars")
                    return response
                raise Exception("Respuesta vacía de DuckDuckGo")
        except ImportError:
            raise Exception("duckduckgo-search no disponible")
        except Exception as e:
            raise Exception(f"DuckDuckGo: {str(e)}")

    @staticmethod
    def get_response(prompt, model="openai"):
        """Obtiene respuesta con fallback automático"""
        # Lista de proveedores a intentar
        providers = [
            ("Pollinations", lambda: IAProvider.pollinations(prompt, model)),
            ("DuckDuckGo", lambda: IAProvider.duckduckgo(prompt)),
        ]

        errors = []
        for name, func in providers:
            try:
                print(f"[KalmAI] Intentando {name}...")
                result = func()
                if result and len(str(result).strip()) > 5:
                    print(f"[KalmAI] ✅ Éxito con {name}")
                    return str(result)
                else:
                    errors.append(f"{name}: respuesta vacía")
            except Exception as e:
                err_msg = str(e)
                errors.append(f"{name}: {err_msg}")
                print(f"[KalmAI] ❌ {name}: {err_msg}")
                time.sleep(1)
                continue

        # Si todos fallaron, intentar con modelo alternativo
        if model != "openai":
            try:
                print(f"[KalmAI] Último intento con modelo openai...")
                result = IAProvider.pollinations(prompt, "openai")
                if result and len(str(result).strip()) > 5:
                    return str(result)
            except:
                pass

        error_summary = " | ".join(errors[:3])
        return f"Lo siento, no pude generar una respuesta en este momento.\n\n**Detalles:** {error_summary}\n\nPor favor intenta de nuevo en unos segundos. Si el problema persiste, cambia el modelo en el selector superior."


# ============================================================
# 4. FUNCIONES HANDLER
# ============================================================

def serve_kalm_ai_page():
    """Sirve la página HTML de Kalm AI"""
    try:
        # Buscar en varias ubicaciones posibles
        possible_paths = [
            Path(__file__).parent.parent.parent / "views" / "kalm_ai.html",
            Path(__file__).parent.parent / "views" / "kalm_ai.html",
            Path("views") / "kalm_ai.html",
        ]

        for path in possible_paths:
            if path.exists():
                print(f"[KalmAI] Sirviendo HTML desde: {path}")
                return path.read_text(encoding="utf-8")

        # No encontrado - listar qué existe para debug
        views_dirs = [Path(__file__).parent.parent.parent / "views"]
        for vd in views_dirs:
            if vd.exists():
                files = [f.name for f in vd.iterdir() if f.suffix == '.html']
                print(f"[KalmAI] Archivos en {vd}: {files}")

        print("[KalmAI] ⚠️ kalm_ai.html NO encontrado en ninguna ruta")
        return get_html_template()

    except Exception as e:
        print(f"[KalmAI] Error leyendo HTML: {e}")
        return get_html_template()


def handle_generar(data):
    """Genera documentos/trabajos - Devuelve JSON válido"""
    tema = data.get('tema', '').strip()
    modelo = data.get('modelo', 'openai')
    tipo = data.get('tipo', 'academico')
    notas = data.get('notas', '').strip()

    print(f"[KalmAI] generar: tema='{tema[:80]}', tipo={tipo}")

    if not tema:
        return {"error": "El tema no puede estar vacío"}, 400

    # Construir prompt según tipo
    if tipo == 'academico':
        prompt = f"""Escribe un TRABAJO ACADÉMICO completo y profesional sobre: {tema}

ESTRUCTURA EXACTA QUE DEBES SEGUIR:

## 1. INTRODUCCIÓN
Presenta el tema, su relevancia y el objetivo del trabajo.

## 2. INTRODUCTION (English version)
Brief English version of the introduction.

## 3. DESARROLLO
Desarrolla el tema con profundidad, usando subtítulos cuando sea necesario.
Incluye datos, ejemplos y argumentos bien fundamentados.
{f'CONSIDERACIONES ADICIONALES: {notas}' if notas else ''}

## 4. CONCLUSIONES
Resume los puntos principales y presenta las conclusiones.

## 5. BIBLIOGRAFÍA
Lista de fuentes recomendadas (APA 7ma edición).

REGLAS:
- Lenguaje formal y académico
- Mínimo 800 palabras en el desarrollo
- Usa subtítulos para organizar
- Incluye citas cuando sea apropiado"""

    elif tipo == 'ejecutivo':
        prompt = f"""Genera un INFORME EJECUTIVO profesional sobre: {tema}

ESTRUCTURA EXACTA:

## RESUMEN EJECUTIVO
Máximo 200 palabras con lo esencial.

## CONTEXTO
Antecedentes y situación actual.

## ANÁLISIS
Puntos clave, datos relevantes y hallazgos.
{f'CONSIDERACIONES: {notas}' if notas else ''}

## CONCLUSIONES
Hallazgos principales.

## RECOMENDACIONES
Acciones concretas y priorizadas.

REGLAS:
- Directo y conciso
- Orientado a toma de decisiones
- Usar viñetas y números cuando sea posible"""

    elif tipo == 'resumen':
        prompt = f"""Haz un RESUMEN completo y estructurado sobre: {tema}
{f'Instrucciones adicionales: {notas}' if notas else ''}

Organiza el resumen con:
- Puntos clave en viñetas
- Ideas principales destacadas
- Conclusión breve
- Extensión: 300-500 palabras"""

    elif tipo == 'codigo':
        prompt = f"""Genera CÓDIGO completo y bien documentado para: {tema}
{f'Requisitos adicionales: {notas}' if notas else ''}

INCLUYE:
1. Explicación breve de la solución
2. Código completo con comentarios
3. Instrucciones de uso
4. Posibles mejoras

Usa el lenguaje más apropiado para la tarea. Si no se especifica, usa Python."""

    else:
        prompt = f"Genera contenido profesional sobre: {tema}\n{f'Notas: {notas}' if notas else ''}"

    try:
        resultado = IAProvider.get_response(prompt, modelo)
        print(f"[KalmAI] Documento generado: {len(resultado)} chars")
        return {"resultado": resultado}, 200
    except Exception as e:
        print(f"[KalmAI] Error generando: {e}")
        return {"error": f"Error al generar: {str(e)}"}, 500


def handle_chat(data):
    """Chat libre - Devuelve JSON válido"""
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')

    print(f"[KalmAI] chat: '{mensaje[:80]}...' modelo={modelo}")

    if not mensaje:
        return {"error": "El mensaje no puede estar vacío"}, 400

    try:
        respuesta = IAProvider.get_response(mensaje, modelo)
        print(f"[KalmAI] Respuesta chat: {len(respuesta)} chars")
        return {"respuesta": respuesta}, 200
    except Exception as e:
        print(f"[KalmAI] Error chat: {e}")
        return {"error": f"Error: {str(e)}"}, 500


def handle_chat_stream(data):
    """Generator para streaming de chat - Yields strings JSON"""
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')

    print(f"[KalmAI] chat/stream: '{mensaje[:80]}...' modelo={modelo}")

    if not mensaje:
        yield json.dumps({"error": "El mensaje no puede estar vacío"}, ensure_ascii=False)
        return

    try:
        # Intentar streaming con Pollinations
        for chunk in IAProvider.pollinations_stream(mensaje, modelo):
            yield json.dumps({"content": chunk}, ensure_ascii=False)
    except Exception as e:
        error_msg = str(e)
        print(f"[KalmAI] Stream falló, haciendo fallback: {error_msg}")

        # Fallback a non-streaming
        try:
            respuesta = IAProvider.get_response(mensaje, modelo)
            # Enviar como un solo chunk grande
            yield json.dumps({"content": respuesta}, ensure_ascii=False)
        except Exception as e2:
            yield json.dumps({"error": f"Error: {str(e2)}"}, ensure_ascii=False)


def handle_health():
    """Health check"""
    try:
        # Verificar que las dependencias funcionan
        import requests
        return {"status": "ok", "message": "Kalm AI running", "version": "3.0"}, 200
    except Exception as e:
        return {"status": "degraded", "message": f"Kalm AI partial: {str(e)}"}, 503
