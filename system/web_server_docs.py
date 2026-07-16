"""Visor de documentos integrado en el navegador - Sin descargas"""
import base64
import mimetypes
from pathlib import Path
from datetime import datetime
import json

class DocumentViewer:
    """Genera HTML para visualizar documentos sin descargarlos"""
    
    @staticmethod
    def generate_pdf_viewer(pdf_path):
        """Genera HTML para ver un PDF"""
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return f"""<html><body><h1 style="color:red">Error: {e}</h1></body></html>"""
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📄 {pdf_path.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; background: #0a0514; font-family: 'Segoe UI', sans-serif; }}
        .container {{ width: 100%; height: 100%; display: flex; flex-direction: column; }}
        .toolbar {{
            background: linear-gradient(to right, #1a0033, #2e0854);
            padding: 8px 16px;
            border-bottom: 1px solid #6a0dad;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 48px;
            flex-shrink: 0;
        }}
        .toolbar h3 {{ color: #da70d6; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 50%; }}
        .toolbar .actions {{ display: flex; gap: 6px; flex-wrap: wrap; }}
        .toolbar button {{
            background: #4b0082;
            color: #fff;
            border: 1px solid #9370db;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }}
        .toolbar button:hover {{ background: #6a0dad; }}
        .toolbar .btn-close {{ background: #8b0000; border-color: #ff0000; }}
        .toolbar .btn-close:hover {{ background: #cc0000; }}
        .pdf-viewer {{
            flex: 1;
            background: #1a1a2e;
            overflow: auto;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }}
        .pdf-viewer embed {{
            width: 100%;
            height: 100%;
            min-height: 600px;
            border: none;
            border-radius: 4px;
        }}
        @media (max-width: 768px) {{
            .toolbar h3 {{ font-size: 11px; max-width: 40%; }}
            .toolbar button {{ font-size: 10px; padding: 3px 8px; }}
            .pdf-viewer embed {{ min-height: 400px; }}
        }}
        @media (max-width: 480px) {{
            .toolbar {{ padding: 6px 10px; }}
            .toolbar h3 {{ font-size: 10px; max-width: 30%; }}
            .toolbar button {{ font-size: 9px; padding: 2px 6px; }}
            .pdf-viewer embed {{ min-height: 300px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="toolbar">
            <h3>📄 {pdf_path.name}</h3>
            <div class="actions">
                <button onclick="window.print()">🖨️ Imprimir</button>
                <button onclick="window.close()" class="btn-close">✕ Cerrar</button>
            </div>
        </div>
        <div class="pdf-viewer">
            <embed src="data:application/pdf;base64,{pdf_data}" type="application/pdf">
        </div>
    </div>
</body>
</html>'''
    
    @staticmethod
    def generate_text_viewer(text_path):
        """Genera HTML para ver un archivo de texto"""
        try:
            content = text_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return f"""<html><body><h1 style="color:red">Error: {e}</h1></body></html>"""
        
        if len(content) > 100000:
            content = content[:100000] + "\n\n... (archivo truncado)"
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📝 {text_path.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; background: #0a0514; font-family: 'Segoe UI', monospace; }}
        .container {{ width: 100%; height: 100%; display: flex; flex-direction: column; background: #0a0a1a; }}
        .toolbar {{
            background: linear-gradient(to right, #1a0033, #2e0854);
            padding: 8px 16px;
            border-bottom: 1px solid #6a0dad;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 48px;
            flex-shrink: 0;
        }}
        .toolbar h3 {{ color: #da70d6; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 50%; }}
        .toolbar .info {{ color: #9370db; font-size: 12px; }}
        .toolbar .btn-close {{
            background: #8b0000;
            border: 1px solid #ff0000;
            color: #fff;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }}
        .toolbar .btn-close:hover {{ background: #cc0000; }}
        .content {{
            flex: 1;
            padding: 16px;
            overflow: auto;
            background: #0a0a1a;
            color: #e6e6fa;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.6;
        }}
        @media (max-width: 768px) {{
            .content {{ font-size: 12px; padding: 10px; }}
            .toolbar h3 {{ font-size: 12px; max-width: 40%; }}
            .toolbar .info {{ font-size: 10px; }}
        }}
        @media (max-width: 480px) {{
            .content {{ font-size: 10px; padding: 8px; }}
            .toolbar {{ padding: 6px 10px; }}
            .toolbar h3 {{ font-size: 10px; max-width: 30%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="toolbar">
            <h3>📝 {text_path.name}</h3>
            <span class="info">{len(content)} caracteres • <button onclick="window.close()" class="btn-close">✕ Cerrar</button></span>
        </div>
        <div class="content">{content}</div>
    </div>
</body>
</html>'''
    
    @staticmethod
    def generate_image_viewer(image_path):
        """Genera HTML para ver una imagen"""
        try:
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return f"""<html><body><h1 style="color:red">Error: {e}</h1></body></html>"""
        
        ext = image_path.suffix.lower()[1:]
        mime = {
            'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png',
            'gif': 'gif', 'bmp': 'bmp', 'webp': 'webp',
            'svg': 'svg+xml', 'ico': 'x-icon'
        }.get(ext, ext)
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🖼️ {image_path.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; background: #0a0514; font-family: 'Segoe UI', sans-serif; }}
        .container {{ width: 100%; height: 100%; display: flex; flex-direction: column; }}
        .toolbar {{
            background: linear-gradient(to right, #1a0033, #2e0854);
            padding: 8px 16px;
            border-bottom: 1px solid #6a0dad;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 48px;
            flex-shrink: 0;
        }}
        .toolbar h3 {{ color: #da70d6; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 50%; }}
        .toolbar .btn-close {{
            background: #8b0000;
            border: 1px solid #ff0000;
            color: #fff;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }}
        .toolbar .btn-close:hover {{ background: #cc0000; }}
        .image-container {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #0a0a1a;
            padding: 16px;
        }}
        .image-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 0 50px rgba(106,13,173,0.3);
        }}
        @media (max-width: 768px) {{
            .toolbar h3 {{ font-size: 12px; max-width: 40%; }}
            .image-container {{ padding: 10px; }}
        }}
        @media (max-width: 480px) {{
            .toolbar {{ padding: 6px 10px; }}
            .toolbar h3 {{ font-size: 10px; max-width: 30%; }}
            .image-container {{ padding: 6px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="toolbar">
            <h3>🖼️ {image_path.name}</h3>
            <div>
                <button onclick="window.close()" class="btn-close">✕ Cerrar</button>
            </div>
        </div>
        <div class="image-container">
            <img src="data:image/{mime};base64,{img_data}" alt="{image_path.name}">
        </div>
    </div>
</body>
</html>'''