#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALM AI - Handler para integrar en el servidor principal
Sin Flask, sin WSGI, solo funciones HTTP
"""

import json
import time
import requests
import sys
import os
import subprocess

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
# 2. HTML TEMPLATE - COMPLETAMENTE REESCRITO
# ============================================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kalm AI - Chat and Kroot</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: linear-gradient(135deg, #0a0514 0%, #1a0033 50%, #2e0854 100%); font-family: 'Segoe UI', Tahoma, sans-serif; min-height: 100vh; padding: 20px; color: #e6e6fa; }
.container { max-width: 1000px; margin: 0 auto; background: rgba(26, 0, 51, 0.7); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(106, 13, 173, 0.3); box-shadow: 0 20px 60px rgba(0,0,0,0.5); overflow: hidden; }
.header { padding: 25px 30px; background: linear-gradient(135deg, rgba(75, 0, 130, 0.4), rgba(106, 13, 173, 0.2)); border-bottom: 1px solid rgba(106, 13, 173, 0.3); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.header h1 { font-size: 24px; background: linear-gradient(135deg, #da70d6, #9370db); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; align-items: center; gap: 10px; }
.header .status { font-size: 12px; color: #9370db; background: rgba(75, 0, 130, 0.3); padding: 6px 14px; border-radius: 20px; border: 1px solid rgba(106, 13, 173, 0.3); }
.tabs { display: flex; background: rgba(10, 5, 20, 0.5); border-bottom: 1px solid rgba(106, 13, 173, 0.2); }
.tab { padding: 12px 24px; cursor: pointer; color: #9370db; font-weight: 600; border-bottom: 3px solid transparent; transition: all 0.3s; }
.tab:hover { color: #da70d6; background: rgba(106, 13, 173, 0.1); }
.tab.active { color: #da70d6; border-bottom-color: #da70d6; }
.tab-content { display: none; padding: 20px 30px; }
.tab-content.active { display: block; }
.controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 15px; }
.controls label { color: #9370db; font-size: 13px; font-weight: 500; }
.controls select, .controls input { padding: 10px 15px; border-radius: 10px; border: 1px solid rgba(106, 13, 173, 0.3); background: rgba(10, 5, 20, 0.8); color: #e6e6fa; font-size: 14px; outline: none; }
.controls select:focus, .controls input:focus { border-color: #da70d6; box-shadow: 0 0 20px rgba(218, 112, 214, 0.15); }
.controls select { min-width: 120px; cursor: pointer; }
.controls input { flex: 1; min-width: 200px; }
.controls button { padding: 10px 24px; border-radius: 10px; border: none; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 8px; }
.btn-primary { background: linear-gradient(135deg, #6a0dad, #9370db); color: white; box-shadow: 0 4px 15px rgba(106, 13, 173, 0.4); }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(106, 13, 173, 0.6); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.btn-secondary { background: rgba(75, 0, 130, 0.3); color: #e6e6fa; border: 1px solid rgba(106, 13, 173, 0.3); }
.btn-secondary:hover { background: rgba(75, 0, 130, 0.5); }
.btn-success { background: linear-gradient(135deg, #008800, #00cc66); color: white; }
.btn-success:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 204, 102, 0.4); }
.result-container { padding: 15px; min-height: 350px; max-height: 500px; overflow-y: auto; background: rgba(10, 5, 20, 0.4); border-radius: 12px; border: 1px solid rgba(106, 13, 173, 0.1); }
.result-container::-webkit-scrollbar { width: 6px; }
.result-container::-webkit-scrollbar-track { background: rgba(10, 5, 20, 0.5); border-radius: 3px; }
.result-container::-webkit-scrollbar-thumb { background: #6a0dad; border-radius: 3px; }
.result-content { white-space: pre-wrap; word-wrap: break-word; line-height: 1.7; font-size: 14px; color: #d8bfd8; }
.result-content .titulo { color: #da70d6; font-weight: bold; font-size: 1.1em; }
.result-content .subtitulo { color: #9370db; font-weight: bold; }
.result-content .error { color: #ff4444; }
.result-content .exito { color: #00cc66; }
.footer { padding: 15px 30px; border-top: 1px solid rgba(106, 13, 173, 0.2); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; background: rgba(10, 5, 20, 0.3); }
.footer .info { color: #6a0dad; font-size: 12px; }
.footer .actions { display: flex; gap: 8px; flex-wrap: wrap; }
.loading { display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(106, 13, 173, 0.3); border-radius: 50%; border-top-color: #da70d6; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 768px) { .header { padding: 15px 20px; } .header h1 { font-size: 18px; } .controls { padding: 10px 15px; } .controls input { min-width: 100px; } .result-container { padding: 10px; min-height: 250px; max-height: 350px; } .tab { padding: 10px 16px; font-size: 14px; } }
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>Kalm AI</h1>
<span class="status" id="status">Ready</span>
</div>
<div class="tabs">
<div class="tab active" data-tab="chat" onclick="switchTab('chat')">Chat Academico</div>
<div class="tab" data-tab="kroot" onclick="switchTab('kroot')">Kroot Corp</div>
</div>
<div class="tab-content active" id="tab-chat">
<div class="controls">
<label>Modelo:</label>
<select id="chat-modelo">
<option value="openai">OpenAI</option>
<option value="claude">Claude</option>
<option value="gemini">Gemini</option>
<option value="deepseek">DeepSeek</option>
<option value="llama">Llama</option>
<option value="mistral">Mistral</option>
</select>
<input type="text" id="chat-tema" placeholder="Tema del trabajo academico...">
<button class="btn-primary" id="chat-generar">Generar</button>
<button class="btn-secondary" id="chat-chat">Chat</button>
</div>
<div class="result-container" id="chat-result">
<div class="result-content">
<span class="titulo">Chat Academico</span>
<br><br>
<span class="exito">Sin API Key - Multiples proveedores</span><br>
<span style="color:#9370db;">Escribe un tema y pulsa "Generar"</span>
</div>
</div>
</div>
<div class="tab-content" id="tab-kroot">
<div class="controls">
<label>Modelo:</label>
<select id="kroot-modelo">
<option value="openai">OpenAI</option>
<option value="claude">Claude</option>
<option value="gemini">Gemini</option>
<option value="deepseek">DeepSeek</option>
<option value="llama">Llama</option>
<option value="mistral">Mistral</option>
</select>
<input type="text" id="kroot-tema" placeholder="Tema del informe ejecutivo...">
<button class="btn-primary" id="kroot-generar">Generar Informe</button>
</div>
<div class="result-container" id="kroot-result">
<div class="result-content">
<span class="titulo">Kroot Corp IA</span>
<br><br>
<span class="exito">Genera informes ejecutivos</span><br>
<span style="color:#9370db;">Escribe un tema y pulsa "Generar Informe"</span>
</div>
</div>
</div>
<div class="footer">
<span class="info">Pollinations - DuckDuckGo</span>
<div class="actions">
<button class="btn-success" id="btn-export">Exportar TXT</button>
<button class="btn-secondary" id="btn-limpiar">Limpiar</button>
</div>
</div>
</div>
<script>
var currentResult = '';
var currentTab = 'chat';
var isGenerating = false;
var API_BASE = '/kalm-ai';

function switchTab(tab) {
    currentTab = tab;
    var tabs = document.querySelectorAll('.tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    var contents = document.querySelectorAll('.tab-content');
    for (var i = 0; i < contents.length; i++) {
        contents[i].classList.remove('active');
    }
    document.querySelector('.tab[data-tab=\"' + tab + '\"]').classList.add('active');
    document.getElementById('tab-' + tab).classList.add('active');
    document.getElementById('status').textContent = 'Ready - ' + (tab === 'chat' ? 'Chat' : 'Kroot');
}

function getResultContainer() {
    if (currentTab === 'chat') {
        return document.getElementById('chat-result');
    } else {
        return document.getElementById('kroot-result');
    }
}

function getTemaInput() {
    if (currentTab === 'chat') {
        return document.getElementById('chat-tema');
    } else {
        return document.getElementById('kroot-tema');
    }
}

function getModeloSelect() {
    if (currentTab === 'chat') {
        return document.getElementById('chat-modelo');
    } else {
        return document.getElementById('kroot-modelo');
    }
}

function setStatus(text, type) {
    var colors = { info: '#9370db', success: '#00cc66', error: '#ff4444', loading: '#ffaa00' };
    var el = document.getElementById('status');
    el.textContent = text;
    el.style.color = colors[type] || '#9370db';
}

function setLoading(loading) {
    isGenerating = loading;
    var btn;
    if (currentTab === 'chat') {
        btn = document.getElementById('chat-generar');
    } else {
        btn = document.getElementById('kroot-generar');
    }
    btn.disabled = loading;
    if (loading) {
        btn.innerHTML = 'Generando...';
        setStatus('Generando...', 'loading');
    } else {
        if (currentTab === 'chat') {
            btn.innerHTML = 'Generar';
        } else {
            btn.innerHTML = 'Generar Informe';
        }
    }
}

function appendResult(text, type) {
    var container = getResultContainer();
    var classes = { titulo: 'titulo', subtitulo: 'subtitulo', error: 'error', exito: 'exito', normal: '' };
    var cls = classes[type] || '';
    var content = container.querySelector('.result-content');
    if (cls) {
        content.innerHTML += '<span class=\"' + cls + '\">' + text + '</span>';
    } else {
        content.innerHTML += text;
    }
    container.scrollTop = container.scrollHeight;
}

function generar() {
    var tema = getTemaInput().value.trim();
    if (!tema) {
        alert('Escribe un tema.');
        return;
    }
    if (isGenerating) {
        return;
    }
    var modelo = getModeloSelect().value;
    var tipo = currentTab;
    setLoading(true);
    var container = getResultContainer();
    container.querySelector('.result-content').innerHTML = '';
    appendResult('Generando ' + (tipo === 'chat' ? 'trabajo' : 'informe') + ' sobre: ' + tema + '\n', 'titulo');
    appendResult('========================================\n\n', 'normal');
    var url = API_BASE + '/generar';
    var data = { tema: tema, modelo: modelo, tipo: tipo };
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            appendResult('\nError: ' + data.error + '\n', 'error');
            setStatus('Error', 'error');
        } else {
            var lines = data.resultado.split('\n');
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                if (line.startsWith('##') || line.startsWith('#')) {
                    appendResult(line + '\n', 'titulo');
                } else if (line.startsWith('**') || line.startsWith('*')) {
                    appendResult(line + '\n', 'subtitulo');
                } else if (line.startsWith('✅') || line.startsWith('📊') || line.startsWith('📝')) {
                    appendResult(line + '\n', 'exito');
                } else if (line.startsWith('❌')) {
                    appendResult(line + '\n', 'error');
                } else {
                    appendResult(line + '\n', 'normal');
                }
            }
            currentResult = data.resultado;
            setStatus('Listo', 'success');
        }
        setLoading(false);
    })
    .catch(function(error) {
        appendResult('\nError: ' + error.message + '\n', 'error');
        setStatus('Error', 'error');
        setLoading(false);
    });
}

function chatLibre() {
    var mensaje = getTemaInput().value.trim();
    if (!mensaje) {
        alert('Escribe un mensaje.');
        return;
    }
    if (isGenerating) {
        return;
    }
    var modelo = getModeloSelect().value;
    setLoading(true);
    appendResult('\nTu: ' + mensaje + '\n', 'subtitulo');
    appendResult('IA: ', 'exito');
    var url = API_BASE + '/chat';
    var data = { mensaje: mensaje, modelo: modelo };
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            appendResult('Error: ' + data.error + '\n', 'error');
        } else {
            appendResult(data.respuesta + '\n\n', 'normal');
            setStatus('Listo', 'success');
        }
        setLoading(false);
    })
    .catch(function(error) {
        appendResult('Error: ' + error.message + '\n', 'error');
        setStatus('Error', 'error');
        setLoading(false);
    });
    getTemaInput().value = '';
}

function exportarTxt() {
    if (!currentResult) {
        alert('No hay contenido para exportar.');
        return;
    }
    var blob = new Blob([currentResult], { type: 'text/plain' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    var timestamp = new Date().toISOString().slice(0,19).replace(/[:-]/g, '');
    a.download = currentTab + '_' + timestamp + '.txt';
    a.click();
    URL.revokeObjectURL(url);
    setStatus('Exportado', 'success');
}

function limpiar() {
    var container = getResultContainer();
    var content = container.querySelector('.result-content');
    var title = currentTab === 'chat' ? 'Chat Academico' : 'Kroot Corp IA';
    content.innerHTML = '<span class=\"titulo\">' + title + '</span><br><br><span class=\"exito\">Listo para generar</span><br><br><span style=\"color:#9370db;\">Escribe un tema y pulsa "Generar"</span>';
    currentResult = '';
    getTemaInput().value = '';
    setStatus('Limpiado', 'info');
}

document.getElementById('chat-generar').addEventListener('click', generar);
document.getElementById('chat-chat').addEventListener('click', chatLibre);
document.getElementById('kroot-generar').addEventListener('click', generar);
document.getElementById('btn-export').addEventListener('click', exportarTxt);
document.getElementById('btn-limpiar').addEventListener('click', limpiar);

var inputs = document.querySelectorAll('#chat-tema, #kroot-tema');
for (var i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            generar();
        }
    });
}

console.log('Kalm AI App cargada');
console.log('API: ' + API_BASE);
</script>
</body>
</html>"""

# ============================================================
# 3. PROVEEDORES DE IA
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
# 4. FUNCIONES HANDLER PARA EL SERVIDOR
# ============================================================

def serve_kalm_ai_page():
    """Sirve la página HTML de Kalm AI"""
    return HTML_TEMPLATE

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
