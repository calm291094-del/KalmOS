# 🏰 KALM OS v4.3

<div align="center">
  <img src="https://github.com/calm291094-del/KalmOS/blob/main/KalmOS.png" alt="KrootCorp Logo" width="200">
  <br>
  <strong> > KALM OS es un mini sistema operativo web que puedes ejecutar en la nube o localmente. Combina un escritorio con explorador de archivos, gestor de tareas, DNS, proxy inverso, juegos, herramientas profesionales y un entorno sandbox. </strong>
  <br>
  <em>Inspirado en Tensei Shitara Slime Datta Ken y Overlord, ademas de windows</em>
</div>


![KALM OS](https://img.shields.io/badge/version-4.3-purple)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Render](https://img.shields.io/badge/deploy-Render-orange)

## ✨ Características

- 🖥️ **Escritorio completo** con ventanas arrastrables y redimensionables
- 📁 **Explorador de archivos** para el disco virtual D:
- 📊 **Task Manager** con monitor de recursos (CPU, RAM, disco, red)
- 🌐 **Servidor DNS** integrado para dominios locales
- 🔒 **Proxy inverso** para enrutar servicios
- ⚙️ **Script Runner** con sandbox aislado
- 🎨 **Temas de color** (Oscuro, Claro, Morado, Azul, Verde, Rojo)
- 🎮 **Juegos**: Snake, Buscaminas, Sokoban, Blackjack, Ajedrez, Tetris, Conecta 4
- 🛠️ **Herramientas profesionales**: Info sistema, análisis disco, generador hash, escáner de puertos
- 🎵 **Reproductor de música** integrado
- 📝 **Bloc de notas** con guardado local
- 🕐 **Reloj mundial** con múltiples husos horarios
- 🧮 **Calculadora** científica
- 📄 **Visor de documentos** (PDF, imágenes, texto)
- 🌐 **Navegador interno** con marcadores

## 🚀 Despliegue en Render (Gratis)

### 1. Fork este repositorio

### 2. Crear un nuevo servicio en Render
```bash
# Render usará automáticamente el archivo render.yaml
```

3. Variables de entorno (opcional)
```bash
Variable	Valor por defecto
UI_PORT	8080
ROOT_USER	root
ROOT_PASS	Kalm*4815162342+-
USER_USER	user
USER_PASS	user*26
```

🖥️ Ejecución Local
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/kalm-os.git
cd kalm-os
```

# Instalar dependencias
```bash
pip install -r requirements.txt
```

# Ejecutar
```bash
python kalm.py
Accede a: http://localhost:8080
```

🐳 Docker
```bash
# Construir la imagen
docker build -t kalm-os .

# Ejecutar
docker run -p 8080:8080 -p 5353:5353 -p 8888:8888 kalm-os
```

🔐 Credenciales por defecto
Usuario	Contraseña
user	  user*26

📁 Estructura del Proyecto
text

kalm_os/
├── kalm.py              # Lanzador principal
├── system/              # Módulos del sistema
│   ├── config.py        # Configuración
│   ├── auth.py          # Autenticación
│   ├── dns_server.py    # DNS
│   ├── proxy.py         # Proxy inverso
│   ├── task_manager.py  # Task Manager
│   ├── script_runner.py # Ejecutor
│   ├── sandbox.py       # Sandbox
│   ├── web_server.py    # Servidor web
│   └── program/         # Scripts Python (juegos, herramientas)
├── views/               # HTML
├── static/              # CSS/JS
└── D/                   # Disco virtual

🛠️ Tecnologías
```bash
    Python 3.11

    HTML/CSS/JS vanilla

    psutil para monitoreo

    Servidor HTTP nativo
```

📝 Licencia
```bash
MIT
⚠️ Notas

    En Render, los archivos subidos se pierden al reiniciar el servicio

    Para persistencia, usa un servicio como Supabase o MongoDB

    El sandbox está optimizado para Linux (Render usa Ubuntu)
```

Hecho con ❤️ y mucho café ☕
