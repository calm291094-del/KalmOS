#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CHAT ACADÉMICO - VERSIÓN WEB BONITA (con soporte para proxy)
"""

import sys
import os
import threading
import time
import subprocess

# ============================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================
def instalar_dependencias():
    for pkg in ["flask", "flask-cors", "requests", "duckduckgo-search"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Instalando {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

instalar_dependencias()

# ============================================================
# 2. IMPORTAR MÓDULOS
# ============================================================
from flask import Flask, request, render_template_string, jsonify
from flask_cors import CORS
import requests
import time

# ============================================================
# 3. PROVEEDORES DE IA (Múltiples fallbacks)
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
        except Exception as e:
            raise Exception(f"DuckDuckGo: {e}")
    
    @staticmethod
    def huggingface(prompt):
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(model="HuggingFaceH4/zephyr-7b-beta")
            response = client.text_generation(prompt, max_new_tokens=500, temperature=0.7)
            return response
        except Exception as e:
            raise Exception(f"HuggingFace: {e}")
    
    @staticmethod
    def get_response(prompt, model="openai"):
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
        
        raise Exception("Todos los proveedores fallaron. Intenta de nuevo en unos minutos.")

# ============================================================
# 4. TEMPLATE HTML (Interfaz bonita con rutas relativas)
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Chat Académico</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0514 0%, #1a0033 50%, #2e0854 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
            color: #e6e6fa;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(26, 0, 51, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(106, 13, 173, 0.3);
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            overflow: hidden;
        }
        .header {
            padding: 25px 30px;
            background: linear-gradient(135deg, rgba(75, 0, 130, 0.4), rgba(106, 13, 173, 0.2));
            border-bottom: 1px solid rgba(106, 13, 173, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .header h1 {
            font-size: 24px;
            background: linear-gradient(135deg, #da70d6, #9370db);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header .status {
            font-size: 12px;
            color: #9370db;
            background: rgba(75, 0, 130, 0.3);
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid rgba(106, 13, 173, 0.3);
        }
        .controls {
            padding: 20px 30px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            background: rgba(10, 5, 20, 0.5);
            border-bottom: 1px solid rgba(106, 13, 173, 0.2);
        }
        .controls label {
            color: #9370db;
            font-size: 13px;
            font-weight: 500;
        }
        .controls select, .controls input {
            padding: 10px 15px;
            border-radius: 10px;
            border: 1px solid rgba(106, 13, 173, 0.3);
            background: rgba(10, 5, 20, 0.8);
            color: #e6e6fa;
            font-size: 14px;
            transition: all 0.3s;
            outline: none;
        }
        .controls select:focus, .controls input:focus {
            border-color: #da70d6;
            box-shadow: 0 0 20px rgba(218, 112, 214, 0.15);
        }
        .controls select {
            min-width: 120px;
            cursor: pointer;
        }
        .controls input {
            flex: 1;
            min-width: 200px;
        }
        .controls button {
            padding: 10px 24px;
            border-radius: 10px;
            border: none;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #6a0dad, #9370db);
            color: white;
            box-shadow: 0 4px 15px rgba(106, 13, 173, 0.4);
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(106, 13, 173, 0.6);
        }
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .btn-secondary {
            background: rgba(75, 0, 130, 0.3);
            color: #e6e6fa;
            border: 1px solid rgba(106, 13, 173, 0.3);
        }
        .btn-secondary:hover {
            background: rgba(75, 0, 130, 0.5);
        }
        .btn-success {
            background: linear-gradient(135deg, #008800, #00cc66);
            color: white;
        }
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 204, 102, 0.4);
        }
        .result-container {
            padding: 20px 30px;
            min-height: 400px;
            max-height: 600px;
            overflow-y: auto;
        }
        .result-container::-webkit-scrollbar {
            width: 6px;
        }
        .result-container::-webkit-scrollbar-track {
            background: rgba(10, 5, 20, 0.5);
            border-radius: 3px;
        }
        .result-container::-webkit-scrollbar-thumb {
            background: #6a0dad;
            border-radius: 3px;
        }
        .result-content {
            background: rgba(10, 5, 20, 0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(106, 13, 173, 0.15);
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.7;
            font-size: 14px;
            color: #d8bfd8;
        }
        .result-content .titulo {
            color: #da70d6;
            font-weight: bold;
            font-size: 1.1em;
        }
        .result-content .subtitulo {
            color: #9370db;
            font-weight: bold;
        }
        .result-content .error {
            color: #ff4444;
        }
        .result-content .exito {
            color: #00cc66;
        }
        .footer {
            padding: 15px 30px;
            border-top: 1px solid rgba(106, 13, 173, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            background: rgba(10, 5, 20, 0.3);
        }
        .footer .info {
            color: #6a0dad;
            font-size: 12px;
        }
        .footer .actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(106, 13, 173, 0.3);
            border-radius: 50%;
            border-top-color: #da70d6;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .provider-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
            background: rgba(106, 13, 173, 0.3);
            color: #9370db;
            border: 1px solid rgba(106, 13, 173, 0.2);
        }
        @media (max-width: 768px) {
            .header { padding: 15px 20px; }
            .header h1 { font-size: 18px; }
            .controls { padding: 15px 20px; }
            .controls input { min-width: 100px; }
            .result-container { padding: 15px 20px; min-height: 300px; max-height: 400px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Chat Académico</h1>
            <span class="status" id="status">🟢 Listo</span>
        </div>
        
        <div class="controls">
            <label for="modelo">Modelo:</label>
            <select id="modelo">
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
                <option value="gemini">Gemini</option>
                <option value="deepseek">DeepSeek</option>
                <option value="llama">Llama</option>
                <option value="mistral">Mistral</option>
            </select>
            
            <input type="text" id="tema" placeholder="Escribe el tema del trabajo académico..." />
            <button class="btn-primary" id="btn-generar">📝 Generar</button>
            <button class="btn-secondary" id="btn-chat">💬 Chat</button>
        </div>
        
        <div class="result-container" id="result-container">
            <div class="result-content" id="result-content">
                <span class="titulo">🤖 Chat Académico</span>
                <br><br>
                <span class="exito">✅ Sin API Key · Múltiples proveedores</span><br>
                <span class="exito">✅ Elige modelo y tema</span><br>
                <span class="exito">✅ Genera trabajos con estructura académica</span>
                <br><br>
                <span style="color:#9370db;">📝 Escribe un tema y pulsa "Generar"</span>
            </div>
        </div>
        
        <div class="footer">
            <span class="info">🔒 Pollinations · DuckDuckGo · Hugging Face</span>
            <div class="actions">
                <button class="btn-success" id="btn-export-txt">📄 Exportar TXT</button>
                <button class="btn-secondary" id="btn-limpiar">🗑️ Limpiar</button>
            </div>
        </div>
    </div>

    <script>
        let currentResult = '';
        let isGenerating = false;
        
        const statusEl = document.getElementById('status');
        const resultContent = document.getElementById('result-content');
        const temaInput = document.getElementById('tema');
        const btnGenerar = document.getElementById('btn-generar');
        const btnChat = document.getElementById('btn-chat');
        const btnExportTxt = document.getElementById('btn-export-txt');
        const btnLimpiar = document.getElementById('btn-limpiar');
        const modeloSelect = document.getElementById('modelo');
        
        // Usar rutas relativas para el proxy
        const API_BASE = '/api/chat';
        
        function setStatus(texto, tipo = 'info') {
            const colors = {
                'info': '#9370db',
                'success': '#00cc66',
                'error': '#ff4444',
                'loading': '#ffaa00'
            };
            statusEl.textContent = texto;
            statusEl.style.color = colors[tipo] || '#9370db';
        }
        
        function setLoading(loading) {
            isGenerating = loading;
            btnGenerar.disabled = loading;
            if (loading) {
                btnGenerar.innerHTML = '<span class="loading"></span> Generando...';
                setStatus('⏳ Generando...', 'loading');
            } else {
                btnGenerar.innerHTML = '📝 Generar';
            }
        }
        
        function appendResult(text, type = 'normal') {
            const classes = {
                'titulo': 'titulo',
                'subtitulo': 'subtitulo',
                'error': 'error',
                'exito': 'exito',
                'normal': ''
            };
            const cls = classes[type] || '';
            if (cls) {
                resultContent.innerHTML += `<span class="${cls}">${text}</span>`;
            } else {
                resultContent.innerHTML += text;
            }
            // Auto-scroll
            const container = document.getElementById('result-container');
            container.scrollTop = container.scrollHeight;
        }
        
        async function generarTrabajo() {
            const tema = temaInput.value.trim();
            if (!tema) {
                alert('Por favor, escribe un tema.');
                return;
            }
            if (isGenerating) return;
            
            const modelo = modeloSelect.value;
            setLoading(true);
            resultContent.innerHTML = '';
            appendResult(`📝 Generando trabajo sobre: ${tema}\n`, 'titulo');
            appendResult('='.repeat(40) + '\n\n', 'normal');
            
            try {
                const response = await fetch(`${API_BASE}/generar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tema, modelo })
                });
                const data = await response.json();
                
                if (data.error) {
                    appendResult(`\n❌ Error: ${data.error}\n`, 'error');
                    setStatus('❌ Error', 'error');
                } else {
                    // Formatear el resultado con colores
                    const lines = data.resultado.split('\n');
                    for (const line of lines) {
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
                    setStatus('✅ Listo', 'success');
                }
            } catch (error) {
                appendResult(`\n❌ Error de conexión: ${error.message}\n`, 'error');
                setStatus('❌ Error', 'error');
            }
            setLoading(false);
        }
        
        async function chatLibre() {
            const tema = temaInput.value.trim();
            if (!tema) {
                alert('Escribe un mensaje para la IA.');
                return;
            }
            if (isGenerating) return;
            
            const modelo = modeloSelect.value;
            setLoading(true);
            appendResult(`\n🧑 Tú: ${tema}\n`, 'subtitulo');
            appendResult(`🤖 IA: `, 'exito');
            
            try {
                const response = await fetch(`${API_BASE}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: tema, modelo })
                });
                const data = await response.json();
                
                if (data.error) {
                    appendResult(`❌ Error: ${data.error}\n`, 'error');
                } else {
                    appendResult(`${data.respuesta}\n\n`, 'normal');
                    setStatus('✅ Listo', 'success');
                }
            } catch (error) {
                appendResult(`❌ Error de conexión: ${error.message}\n`, 'error');
                setStatus('❌ Error', 'error');
            }
            temaInput.value = '';
            setLoading(false);
        }
        
        function exportarTxt() {
            if (!currentResult) {
                alert('No hay contenido para exportar. Genera un trabajo primero.');
                return;
            }
            const blob = new Blob([currentResult], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `trabajo_${new Date().toISOString().slice(0,19).replace(/[:-]/g, '')}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            setStatus('📄 Exportado', 'success');
        }
        
        function limpiar() {
            resultContent.innerHTML = `
                <span class="titulo">🤖 Chat Académico</span>
                <br><br>
                <span class="exito">✅ Listo para generar nuevos trabajos</span>
                <br><br>
                <span style="color:#9370db;">📝 Escribe un tema y pulsa "Generar"</span>
            `;
            currentResult = '';
            temaInput.value = '';
            setStatus('🗑️ Limpiado', 'info');
        }
        
        // Event listeners
        btnGenerar.addEventListener('click', generarTrabajo);
        btnChat.addEventListener('click', chatLibre);
        btnExportTxt.addEventListener('click', exportarTxt);
        btnLimpiar.addEventListener('click', limpiar);
        temaInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                generarTrabajo();
            }
        });
        
        console.log('🤖 Chat Académico - Interfaz cargada');
        console.log(`📡 API Base: ${API_BASE}`);
    </script>
</body>
</html>
"""

# ============================================================
# 5. SERVIDOR FLASK
# ============================================================
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar():
    data = request.json
    tema = data.get('tema', '').strip()
    modelo = data.get('modelo', 'openai')
    
    if not tema:
        return jsonify({'error': 'Tema vacío'}), 400
    
    prompt = f"""
    Escribe un trabajo académico completo sobre: {tema}
    
    Estructura EXACTA:
    ## INTRODUCCIÓN (en español)
    ## INTRODUCTION (in English)
    ## DESARROLLO
    ## CONCLUSIONES
    ## BIBLIOGRAFÍA
    """
    
    try:
        resultado = IAProvider.get_response(prompt, modelo)
        return jsonify({'resultado': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    mensaje = data.get('mensaje', '').strip()
    modelo = data.get('modelo', 'openai')
    
    if not mensaje:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    try:
        respuesta = IAProvider.get_response(mensaje, modelo)
        return jsonify({'respuesta': respuesta})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# 6. PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    
    if "--kalm" in sys.argv:
        print(f"🚀 Chat Académico Web iniciado en puerto {port}")
        print(f"http://localhost:{port}")
        sys.stdout.flush()
        
        def run():
            app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        app.run(host='0.0.0.0', port=port, debug=True)
