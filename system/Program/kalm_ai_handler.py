#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALM AI - Handler para integrar en el servidor principal
VERSION CORREGIDA - DEVUELVE JSON VALIDO
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
# 2. HTML TEMPLATE
# ============================================================
def get_html_template():
    """Retorna el HTML de Kalm AI"""
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Kalm AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #0a0514 0%, #1a0033 50%, #2e0854 100%); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; padding: 20px; color: #e6e6fa; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(10,5,20,0.5); border-radius: 3px; }
        ::-webkit-scrollbar-thumb { background: #6a0dad; border-radius: 3px; }
        .app-container { max-width: 1000px; margin: 0 auto; background: rgba(26, 0, 51, 0.7); backdrop-filter: blur(20px); border-radius: 24px; border: 1px solid rgba(106, 13, 173, 0.25); box-shadow: 0 25px 80px rgba(0,0,0,0.6); overflow: hidden; min-height: 85vh; display: flex; flex-direction: column; }
        .app-header { padding: 20px 28px; background: linear-gradient(135deg, rgba(75,0,130,0.3), rgba(106,13,173,0.1)); border-bottom: 1px solid rgba(106,13,173,0.15); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
        .app-header .logo { display: flex; align-items: center; gap: 12px; }
        .app-header .logo-icon { font-size: 28px; background: linear-gradient(135deg, #6a0dad, #da70d6); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
        .app-header h1 { font-size: 20px; font-weight: 700; background: linear-gradient(135deg, #da70d6, #9370db); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .app-header .subtitle { font-size: 12px; color: #9370db; }
        .status-badge { display: flex; align-items: center; gap: 8px; padding: 5px 14px; border-radius: 20px; background: rgba(0,204,102,0.12); border: 1px solid rgba(0,204,102,0.25); font-size: 12px; color: #00cc66; }
        .status-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: #00cc66; animation: pulse 1.5s ease-in-out infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
        .tabs { display: flex; background: rgba(10,5,20,0.3); border-bottom: 1px solid rgba(106,13,173,0.1); padding: 0 16px; gap: 4px; flex-shrink: 0; flex-wrap: wrap; }
        .tab { padding: 12px 20px; cursor: pointer; color: #9370db; font-weight: 600; font-size: 13px; border-bottom: 3px solid transparent; transition: all 0.3s; display: flex; align-items: center; gap: 8px; user-select: none; }
        .tab:hover { color: #da70d6; background: rgba(106,13,173,0.08); }
        .tab.active { color: #da70d6; border-bottom-color: #da70d6; background: rgba(106,13,173,0.1); }
        .tab .badge { font-size: 9px; background: rgba(106,13,173,0.25); padding: 1px 8px; border-radius: 10px; color: #9370db; }
        .tab.active .badge { background: rgba(218,112,214,0.15); color: #da70d6; }
        .tab-content { display: none !important; flex: 1; flex-direction: column; }
        .tab-content.active { display: flex !important; }
        .controls-panel { padding: 14px 20px; background: rgba(10,5,20,0.25); border-bottom: 1px solid rgba(106,13,173,0.08); display: flex; flex-wrap: wrap; gap: 10px; align-items: center; flex-shrink: 0; }
        .controls-panel label { color: #9370db; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .controls-panel select { padding: 7px 12px; border-radius: 8px; border: 1px solid rgba(106,13,173,0.2); background: rgba(10,5,20,0.7); color: #e6e6fa; font-size: 13px; outline: none; cursor: pointer; min-width: 110px; }
        .controls-panel select:focus { border-color: #6a0dad; }
        .controls-panel input[type="text"] { flex: 1; min-width: 160px; padding: 7px 14px; border-radius: 8px; border: 1px solid rgba(106,13,173,0.2); background: rgba(10,5,20,0.7); color: #e6e6fa; font-size: 13px; outline: none; }
        .controls-panel input[type="text"]:focus { border-color: #6a0dad; }
        .controls-panel input[type="text"]::placeholder { color: #4b0082; }
        .btn { padding: 7px 18px; border-radius: 8px; border: none; font-weight: 600; font-size: 13px; cursor: pointer; transition: all 0.25s; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
        .btn-primary { background: linear-gradient(135deg, #6a0dad, #9370db); color: #fff; box-shadow: 0 4px 15px rgba(106,13,173,0.3); }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(106,13,173,0.5); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-secondary { background: rgba(75,0,130,0.2); color: #e6e6fa; border: 1px solid rgba(106,13,173,0.15); }
        .btn-secondary:hover { background: rgba(75,0,130,0.35); }
        .btn-success { background: linear-gradient(135deg, #008800, #00cc66); color: #fff; }
        .btn-success:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,204,102,0.3); }
        .btn-external { background: rgba(0,100,200,0.2); color: #4da6ff; border: 1px solid rgba(0,100,200,0.2); }
        .btn-external:hover { background: rgba(0,100,200,0.35); }
        .btn-sm { padding: 4px 12px; font-size: 11px; }
        .result-area { flex: 1; padding: 16px 20px; min-height: 280px; max-height: 480px; overflow-y: auto; background: rgba(0,0,0,0.12); margin: 0 14px 14px 14px; border-radius: 12px; border: 1px solid rgba(106,13,173,0.06); }
        .result-area .result-content { white-space: pre-wrap; word-wrap: break-word; line-height: 1.8; font-size: 14px; color: #d8bfd8; }
        .result-area .result-content .titulo { color: #da70d6; font-weight: 700; font-size: 1.1em; }
        .result-area .result-content .subtitulo { color: #9370db; font-weight: 600; }
        .result-area .result-content .error { color: #ff4444; }
        .result-area .result-content .exito { color: #00cc66; }
        .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 200px; text-align: center; color: #9370db; }
        .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
        .empty-state .title { font-size: 17px; font-weight: 600; color: #da70d6; }
        .empty-state .desc { font-size: 13px; margin-top: 4px; max-width: 380px; color: #6a0dad; }
        .app-footer { padding: 10px 20px; border-top: 1px solid rgba(106,13,173,0.1); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; background: rgba(10,5,20,0.15); flex-shrink: 0; }
        .app-footer .info { font-size: 11px; color: #6a0dad; }
        .app-footer .actions { display: flex; gap: 6px; flex-wrap: wrap; }
        .progress-container { height: 3px; background: rgba(106,13,173,0.12); border-radius: 2px; overflow: hidden; margin: 0 14px 2px 14px; opacity: 0; transition: opacity 0.4s; flex-shrink: 0; }
        .progress-container.active { opacity: 1; }
        .progress-container .progress-bar { height: 100%; width: 0%; background: linear-gradient(to right, #6a0dad, #da70d6); border-radius: 2px; transition: width 0.5s ease; }
        @media (max-width: 768px) { .app-header { padding: 14px 16px; } .app-header h1 { font-size: 17px; } .tabs { padding: 0 10px; overflow-x: auto; flex-wrap: nowrap; } .tab { padding: 10px 14px; font-size: 12px; white-space: nowrap; } .controls-panel { padding: 10px 14px; } .controls-panel input[type="text"] { min-width: 100px; font-size: 12px; } .result-area { padding: 12px 14px; margin: 0 10px 10px 10px; min-height: 200px; max-height: 350px; } .btn { font-size: 12px; padding: 6px 12px; } }
        @media (max-width: 480px) { body { padding: 10px; } .app-header .logo-icon { width: 34px; height: 34px; font-size: 18px; } .app-header h1 { font-size: 15px; } .controls-panel { flex-direction: column; align-items: stretch; } .controls-panel input[type="text"] { min-width: unset; } .controls-panel .btn-group { display: flex; gap: 6px; flex-wrap: wrap; } .controls-panel .btn-group .btn { flex: 1; justify-content: center; } .result-area { min-height: 160px; max-height: 280px; } }
    </style>
</head>
<body>
<div class="app-container">
    <header class="app-header">
        <div class="logo"><div class="logo-icon">🧠</div><div><h1>Kalm AI</h1><span class="subtitle">Asistente Inteligente</span></div></div>
        <div class="status-badge"><span class="dot"></span><span id="status-text">Listo</span></div>
    </header>
    <div class="tabs">
        <div class="tab active" data-tab="chat" onclick="switchTab('chat')">💬 Chat Academico <span class="badge">IA</span></div>
        <div class="tab" data-tab="kroot" onclick="switchTab('kroot')">🏢 Kroot Corp <span class="badge">Empresarial</span></div>
        <div class="tab" data-tab="external" onclick="switchTab('external')">🌐 Externos <span class="badge">Web</span></div>
    </div>
    <div class="progress-container" id="progress-container"><div class="progress-bar" id="progress-bar"></div></div>
    <div class="tab-content active" id="tab-chat">
        <div class="controls-panel">
            <label>Modelo</label>
            <select id="chat-modelo">
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
                <option value="gemini">Gemini</option>
                <option value="deepseek">DeepSeek</option>
                <option value="llama">Llama</option>
                <option value="mistral">Mistral</option>
            </select>
            <input type="text" id="chat-tema" placeholder="Tema del trabajo academico..." />
            <div class="btn-group">
                <button class="btn btn-primary" id="chat-generar">Generar</button>
                <button class="btn btn-secondary" id="chat-chat">Chat</button>
            </div>
        </div>
        <div class="result-area" id="chat-result"><div class="empty-state"><div class="icon">📚</div><div class="title">Chat Academico</div><div class="desc">Escribe un tema y pulsa "Generar" para crear un trabajo academico.</div></div></div>
    </div>
    <div class="tab-content" id="tab-kroot">
        <div class="controls-panel">
            <label>Modelo</label>
            <select id="kroot-modelo">
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
                <option value="gemini">Gemini</option>
                <option value="deepseek">DeepSeek</option>
                <option value="llama">Llama</option>
                <option value="mistral">Mistral</option>
            </select>
            <input type="text" id="kroot-tema" placeholder="Tema del informe ejecutivo..." />
            <div class="btn-group"><button class="btn btn-primary" id="kroot-generar">Generar Informe</button></div>
        </div>
        <div class="result-area" id="kroot-result"><div class="empty-state"><div class="icon">🏢</div><div class="title">Kroot Corp IA</div><div class="desc">Genera informes ejecutivos profesionales.</div></div></div>
    </div>
    <div class="tab-content" id="tab-external">
        <div class="controls-panel"><label>🌐 Acceso a IAs externas</label><span style="color:#9370db;font-size:13px;">Abre en nueva pestaña</span></div>
        <div style="padding:16px 20px;flex:1;">
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">
                <div style="background:rgba(10,5,20,0.4);border-radius:12px;padding:20px;border:1px solid rgba(106,13,173,0.15);">
                    <div style="font-size:32px;margin-bottom:10px;">🔵</div>
                    <h3 style="color:#da70d6;margin-bottom:6px;">DeepSeek</h3>
                    <p style="color:#9370db;font-size:13px;margin-bottom:12px;">IA avanzada con razonamiento profundo.</p>
                    <button class="btn btn-external" onclick="window.open('https://chat.deepseek.com/a/chat/','_blank')">Abrir DeepSeek</button>
                </div>
                <div style="background:rgba(10,5,20,0.4);border-radius:12px;padding:20px;border:1px solid rgba(106,13,173,0.15);">
                    <div style="font-size:32px;margin-bottom:10px;">🟣</div>
                    <h3 style="color:#da70d6;margin-bottom:6px;">Qwen AI</h3>
                    <p style="color:#9370db;font-size:13px;margin-bottom:12px;">IA de Alibaba Cloud.</p>
                    <button class="btn btn-external" onclick="window.open('https://chat.qwen.ai/c/','_blank')">Abrir Qwen</button>
                </div>
                <div style="background:rgba(10,5,20,0.4);border-radius:12px;padding:20px;border:1px solid rgba(106,13,173,0.15);">
                    <div style="font-size:32px;margin-bottom:10px;">🤖</div>
                    <h3 style="color:#da70d6;margin-bottom:6px;">Pollinations AI</h3>
                    <p style="color:#9370db;font-size:13px;margin-bottom:12px;">IA integrada en Kalm OS.</p>
                    <button class="btn btn-secondary" onclick="switchTab('chat')">Usar Pollinations</button>
                </div>
            </div>
            <div style="margin-top:16px;padding:12px 16px;background:rgba(0,100,200,0.08);border-radius:8px;border:1px solid rgba(0,100,200,0.15);">
                <p style="color:#9370db;font-size:12px;">💡 <b>Consejo:</b> DeepSeek y Qwen son servicios externos. Pollinations AI esta integrado directamente.</p>
            </div>
        </div>
    </div>
    <footer class="app-footer">
        <span class="info">Pollinations AI · DuckDuckGo · Sin API Key</span>
        <div class="actions">
            <button class="btn btn-success btn-sm" id="btn-export">Exportar</button>
            <button class="btn btn-secondary btn-sm" id="btn-limpiar">Limpiar</button>
        </div>
    </footer>
</div>
<script>
    var currentResult = '';
    var currentTab = 'chat';
    var isGenerating = false;
    var API_BASE = '/kalm-ai';

    function $(id) { return document.getElementById(id); }

    function switchTab(tab) {
        currentTab = tab;
        document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
        var tabEl = document.querySelector('.tab[data-tab="' + tab + '"]');
        if (tabEl) tabEl.classList.add('active');
        document.querySelectorAll('.tab-content').forEach(function(c) {
            c.classList.remove('active');
            c.style.display = 'none';
        });
        var contentEl = $('tab-' + tab);
        if (contentEl) {
            contentEl.classList.add('active');
            contentEl.style.display = 'flex';
        }
        setStatus('Listo', 'info');
        setProgress(0);
    }

    function setStatus(text, type) {
        type = type || 'info';
        var colors = { info: '#9370db', success: '#00cc66', error: '#ff4444', loading: '#ffaa00' };
        var el = $('status-text');
        if (el) {
            el.textContent = text;
            el.style.color = colors[type] || '#9370db';
        }
        var dot = document.querySelector('.dot');
        if (dot) {
            dot.style.background = type === 'error' ? '#ff4444' : type === 'loading' ? '#ffaa00' : '#00cc66';
        }
    }

    function setProgress(pct) {
        var container = $('progress-container');
        var bar = $('progress-bar');
        if (!container || !bar) return;
        if (pct > 0) {
            container.classList.add('active');
            bar.style.width = Math.min(pct, 100) + '%';
        } else {
            container.classList.remove('active');
            bar.style.width = '0%';
        }
    }

    function appendResult(text, type) {
        type = type || 'normal';
        var container = currentTab === 'chat' ? $('chat-result') : $('kroot-result');
        if (!container) return;
        var classes = { titulo: 'titulo', subtitulo: 'subtitulo', error: 'error', exito: 'exito', normal: '' };
        var cls = classes[type] || '';
        var content = container.querySelector('.result-content');
        if (!content) {
            content = document.createElement('div');
            content.className = 'result-content';
            container.innerHTML = '';
            container.appendChild(content);
        }
        if (cls) {
            content.innerHTML += '<span class="' + cls + '">' + text + '</span>';
        } else {
            content.innerHTML += text;
        }
        container.scrollTop = container.scrollHeight;
    }

    function clearResult() {
        var container = currentTab === 'chat' ? $('chat-result') : $('kroot-result');
        if (!container) return;
        var icon = currentTab === 'chat' ? '📚' : '🏢';
        var title = currentTab === 'chat' ? 'Chat Academico' : 'Kroot Corp IA';
        var desc = currentTab === 'chat' 
            ? 'Escribe un tema y pulsa "Generar" para crear un trabajo academico.'
            : 'Genera informes ejecutivos profesionales.';
        container.innerHTML = '<div class="empty-state"><div class="icon">' + icon + '</div><div class="title">' + title + '</div><div class="desc">' + desc + '</div></div>';
        currentResult = '';
        setProgress(0);
    }

    function generar() {
        var input = currentTab === 'chat' ? $('chat-tema') : $('kroot-tema');
        if (!input) return;
        var tema = input.value.trim();
        if (!tema) { alert('Escribe un tema.'); return; }
        if (isGenerating) return;

        var modelo = (currentTab === 'chat' ? $('chat-modelo') : $('kroot-modelo')).value;
        var tipo = currentTab;
        var btn = currentTab === 'chat' ? $('chat-generar') : $('kroot-generar');

        isGenerating = true;
        btn.disabled = true;
        btn.innerHTML = 'Generando...';
        setProgress(10);
        setStatus('Generando...', 'loading');

        var container = currentTab === 'chat' ? $('chat-result') : $('kroot-result');
        container.innerHTML = '<div class="result-content"></div>';
        appendResult('Generando ' + (tipo === 'chat' ? 'trabajo academico' : 'informe ejecutivo') + ' sobre: "' + tema + '"\n', 'titulo');
        appendResult('========================================\n\n', 'normal');

        fetch(API_BASE + '/generar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tema: tema, modelo: modelo, tipo: tipo })
        })
        .then(function(response) {
            if (!response.ok) throw new Error('Error ' + response.status);
            return response.json();
        })
        .then(function(data) {
            setProgress(95);
            if (data.error) {
                appendResult('\nError: ' + data.error + '\n', 'error');
                setStatus('Error', 'error');
            } else {
                var lines = data.resultado.split('\n');
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    if (line.startsWith('##') || line.startsWith('#')) appendResult(line + '\n', 'titulo');
                    else if (line.startsWith('**') || line.startsWith('*')) appendResult(line + '\n', 'subtitulo');
                    else if (line.match(/^[✅📊📝📌🔹]/)) appendResult(line + '\n', 'exito');
                    else if (line.startsWith('❌')) appendResult(line + '\n', 'error');
                    else appendResult(line + '\n', 'normal');
                }
                currentResult = data.resultado;
                setStatus('Listo', 'success');
                setProgress(100);
                setTimeout(function() { setProgress(0); }, 1000);
            }
        })
        .catch(function(error) {
            appendResult('\nError: ' + error.message + '\n', 'error');
            setStatus('Error', 'error');
            setProgress(0);
        })
        .finally(function() {
            isGenerating = false;
            btn.disabled = false;
            btn.innerHTML = currentTab === 'chat' ? 'Generar' : 'Generar Informe';
        });
    }

    function chatLibre() {
        var input = $('chat-tema');
        if (!input) return;
        var mensaje = input.value.trim();
        if (!mensaje) { alert('Escribe un mensaje.'); return; }
        if (isGenerating) return;

        var modelo = $('chat-modelo').value;
        var btn = $('chat-chat');

        isGenerating = true;
        btn.disabled = true;
        btn.innerHTML = 'Pensando...';
        setStatus('Pensando...', 'loading');
        setProgress(20);

        var container = $('chat-result');
        if (!container.querySelector('.result-content')) {
            container.innerHTML = '<div class="result-content"></div>';
        }
        appendResult('\nTu: ' + mensaje + '\n', 'subtitulo');
        appendResult('IA: ', 'exito');

        fetch(API_BASE + '/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensaje: mensaje, modelo: modelo })
        })
        .then(function(response) {
            if (!response.ok) throw new Error('Error ' + response.status);
            return response.json();
        })
        .then(function(data) {
            setProgress(80);
            if (data.error) {
                appendResult('Error: ' + data.error + '\n', 'error');
                setStatus('Error', 'error');
            } else {
                appendResult(data.respuesta + '\n\n', 'normal');
                setStatus('Listo', 'success');
                setProgress(100);
                setTimeout(function() { setProgress(0); }, 800);
            }
        })
        .catch(function(error) {
            appendResult('Error: ' + error.message + '\n', 'error');
            setStatus('Error', 'error');
            setProgress(0);
        })
        .finally(function() {
            isGenerating = false;
            btn.disabled = false;
            btn.innerHTML = 'Chat';
            input.value = '';
        });
    }

    function exportarTxt() {
        if (!currentResult) { alert('No hay contenido para exportar.'); return; }
        var blob = new Blob([currentResult], { type: 'text/plain;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        var timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
        a.download = currentTab + '_' + timestamp + '.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        setStatus('Exportado', 'success');
    }

    function limpiar() {
        clearResult();
        var input = currentTab === 'chat' ? $('chat-tema') : $('kroot-tema');
        if (input) input.value = '';
        setStatus('Limpiado', 'info');
        setProgress(0);
    }

    // Event listeners
    document.addEventListener('DOMContentLoaded', function() {
        $('chat-generar').addEventListener('click', generar);
        $('chat-chat').addEventListener('click', chatLibre);
        $('kroot-generar').addEventListener('click', generar);
        $('btn-export').addEventListener('click', exportarTxt);
        $('btn-limpiar').addEventListener('click', limpiar);
        
        document.querySelectorAll('#chat-tema, #kroot-tema').forEach(function(el) {
            el.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    generar();
                }
            });
        });
    });

    window.switchTab = switchTab;
    window.generar = generar;
    window.chatLibre = chatLibre;
    window.exportarTxt = exportarTxt;
    window.limpiar = limpiar;
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
# 4. FUNCIONES HANDLER
# ============================================================

def serve_kalm_ai_page():
    """Sirve la pagina HTML de Kalm AI"""
    try:
        views_dir = Path(__file__).parent.parent.parent / "views"
        html_file = views_dir / "kalm_ai.html"
        if html_file.exists():
            print("[KalmAI] Sirviendo desde views/kalm_ai.html")
            return html_file.read_text(encoding="utf-8")
        else:
            print("[KalmAI] Usando template interno")
            return get_html_template()
    except Exception as e:
        print(f"[KalmAI] Error: {e}")
        return get_html_template()

def handle_generar(data):
    """Genera trabajos/informes"""
    tema = data.get('tema', '').strip()
    modelo = data.get('modelo', 'openai')
    tipo = data.get('tipo', 'chat')
    
    print(f"[KalmAI] generar: tema='{tema}', modelo='{modelo}', tipo='{tipo}'")
    
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
        return {"resultado": resultado}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def handle_chat(data):
    """Chat libre"""
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')
    
    print(f"[KalmAI] chat: mensaje='{mensaje[:50]}...'")
    
    if not mensaje:
        return {"error": "El mensaje no puede estar vacio"}, 400
    
    try:
        respuesta = IAProvider.get_response(mensaje, modelo)
        return {"respuesta": respuesta}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def handle_health():
    return {"status": "ok", "message": "Kalm AI running"}, 200
