#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KROOT CORP - VERSIÓN WEB BONITA
Interfaz moderna en el navegador interno de Kalm OS
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
# 4. TEMPLATE HTML (Interfaz bonita para Kroot Corp)
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Kroot Corp IA</title>
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
        .controls select { min-width: 120px; cursor: pointer; }
        .controls input { flex: 1; min-width: 200px; }
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
        .btn-secondary:hover { background: rgba(75, 0, 130, 0.5); }
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
        .result-container::-webkit-scrollbar { width: 6px; }
        .result-container::-webkit-scrollbar-track { background: rgba(10, 5, 20, 0.5); border-radius: 3px; }
        .result-container::-webkit-scrollbar-thumb { background: #6a0dad; border-radius: 3px; }
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
        .result-content .titulo { color: #da70d6; font-weight: bold; font-size: 1.1em; }
        .result-content .subtitulo { color: #9370db; font-weight: bold; }
        .result-content .error { color: #ff4444; }
        .result-content .exito { color: #00cc66; }
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
        .footer .info { color: #6a0dad; font-size: 12px; }
        .footer .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(106, 13, 173, 0.3);
            border-radius: 50%;
            border-top-color: #da70d6;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
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
            <h1>🏢 Kroot Corp IA</h1>
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
            
            <input type="text" id="tema" placeholder="Escribe el tema del informe ejecutivo..." />
            <button class="btn-primary" id="btn-generar">📝 Generar Informe</button>
        </div>
        
        <div class="result-container" id="result-container">
            <div class="result-content" id="result-content">
                <span class="titulo">🏢 Kroot Corp IA</span>
                <br><br>
                <span class="exito">✅ Sin API Key · Múltiples proveedores</span><br>
                <span class="exito">✅ Genera informes ejecutivos</span>
                <br><br>
                <span style="color:#9370db;">📝 Escribe un tema y pulsa "Generar Informe"</span>
            </div>
        </div>
        
        <div class="footer">
            <span class="info">🔒 Pollinations · DuckDuckGo</span>
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
        const btnExportTxt = document.getElementById('btn-export-txt');
        const btnLimpiar = document.getElementById('btn-limpiar');
        const modeloSelect = document.getElementById('modelo');
        
        function setStatus(texto, tipo = 'info') {
            const colors = { 'info': '#9370db', 'success': '#00cc66', 'error': '#ff4444', 'loading': '#ffaa00' };
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
                btnGenerar.innerHTML = '📝 Generar Informe';
            }
        }
        
        function appendResult(text, type = 'normal') {
            const classes = { 'titulo': 'titulo', 'subtitulo': 'subtitulo', 'error': 'error', 'exito': 'exito', 'normal': '' };
            const cls = classes[type] || '';
            if (cls) { resultContent.innerHTML += `<span class="${cls}">${text}</span>`; }
            else { resultContent.innerHTML += text; }
            document.getElementById('result-container').scrollTop = document.getElementById('result-container').scrollHeight;
        }
        
        async function generarInforme() {
            const tema = temaInput.value.trim();
            if (!tema) { alert('Escribe un tema.'); return; }
            if (isGenerating) return;
            
            const modelo = modeloSelect.value;
            setLoading(true);
            resultContent.innerHTML = '';
            appendResult(`📝 Generando informe sobre: ${tema}\n`, 'titulo');
            appendResult('='.repeat(40) + '\n\n', 'normal');
            
            try {
                const response = await fetch('/generar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tema, modelo })
                });
                const data = await response.json();
                
                if (data.error) {
                    appendResult(`\n❌ Error: ${data.error}\n`, 'error');
                    setStatus('❌ Error', 'error');
                } else {
                    const lines = data.resultado.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('##') || line.startsWith('#')) { appendResult(line + '\n', 'titulo'); }
                        else if (line.startsWith('**') || line.startsWith('*')) { appendResult(line + '\n', 'subtitulo'); }
                        else if (line.startsWith('✅') || line.startsWith('📊') || line.startsWith('📝')) { appendResult(line + '\n', 'exito'); }
                        else if (line.startsWith('❌')) { appendResult(line + '\n', 'error'); }
                        else { appendResult(line + '\n', 'normal'); }
                    }
                    currentResult = data.resultado;
                    setStatus('✅ Listo', 'success');
                }
            } catch (error) {
                appendResult(`\n❌ Error: ${error.message}\n`, 'error');
                setStatus('❌ Error', 'error');
            }
            setLoading(false);
        }
        
        function exportarTxt() {
            if (!currentResult) { alert('No hay contenido para exportar.'); return; }
            const blob = new Blob([currentResult], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `informe_${new Date().toISOString().slice(0,19).replace(/[:-]/g, '')}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            setStatus('📄 Exportado', 'success');
        }
        
        function limpiar() {
            resultContent.innerHTML = `
                <span class="titulo">🏢 Kroot Corp IA</span>
                <br><br>
                <span class="exito">✅ Listo para generar nuevos informes</span>
                <br><br>
                <span style="color:#9370db;">📝 Escribe un tema y pulsa "Generar Informe"</span>
            `;
            currentResult = '';
            temaInput.value = '';
            setStatus('🗑️ Limpiado', 'info');
        }
        
        btnGenerar.addEventListener('click', generarInforme);
        btnExportTxt.addEventListener('click', exportarTxt);
        btnLimpiar.addEventListener('click', limpiar);
        temaInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); generarInforme(); } });
        
        console.log('🏢 Kroot Corp - Interfaz cargada');
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
    
    # Fase 1: Investigación
    prompt_inv = f"Investiga a fondo sobre '{tema}'. Da 5 puntos clave y datos relevantes."
    inv = IAProvider.get_response(prompt_inv, modelo)
    
    # Fase 2: Informe
    prompt_inf = f"Basado en: {inv}\n\nRedacta un informe ejecutivo profesional con: Introducción, Puntos Clave, Conclusiones y Recomendaciones."
    informe = IAProvider.get_response(prompt_inf, modelo)
    
    # Fase 3: QA
    prompt_qa = f"Revisa este informe y da feedback: {informe}"
    qa = IAProvider.get_response(prompt_qa, modelo)
    
    resultado = f"""📊 INFORME EJECUTIVO: {tema.upper()}
{'=' * 50}

{informe}

{'=' * 50}
📝 VEREDICTO DE CALIDAD:
{qa}
{'=' * 50}"""
    
    return jsonify({'resultado': resultado})

# ============================================================
# 6. PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    
    if "--kalm" in sys.argv:
        print(f"🚀 Kroot Corp Web iniciado en puerto {port}")
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