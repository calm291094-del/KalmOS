// KALM OS v4.3 - Reproductor de Música REAL (CORREGIDO)

let musicPlayer = {
    isPlaying: false,
    currentTrack: 0,
    playlist: [],
    volume: 70,
    progress: 0,
    duration: 0,
    audio: null,
    progressInterval: null,
    isLoaded: false,
    isLoading: false
};

// ═══ FORMATOS SOPORTADOS ═══
const SUPPORTED_FORMATS = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.webm'];

// ═══ CARGAR CANCIONES DESDE D:/Music/ ═══
function loadMusicFiles() {
    const status = document.getElementById('music-status');
    const playlistDiv = document.getElementById('music-playlist');
    
    // Evitar recargas múltiples
    if (musicPlayer.isLoading) return;
    musicPlayer.isLoading = true;
    
    if (status) {
        status.textContent = '⏳ Cargando canciones...';
        status.style.color = '#ffaa00';
    }
    
    if (playlistDiv) {
        playlistDiv.innerHTML = `
            <div style="color:#9370db;text-align:center;padding:20px;">
                ⏳ Buscando archivos de música en D:/Music/...
            </div>
        `;
    }

    fetch('/api/music/list')
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(data => {
            console.log('📥 Respuesta /api/music/list:', data);
            
            if (data.ok && data.files && data.files.length > 0) {
                musicPlayer.playlist = data.files.map(f => ({
                    name: f.name,
                    path: f.path,
                    url: f.url
                }));
                musicPlayer.isLoaded = true;
                musicPlayer.isLoading = false;
                
                console.log(`🎵 ${musicPlayer.playlist.length} canciones cargadas:`, 
                           musicPlayer.playlist.map(f => f.name));
                
                updatePlaylistUI();
                if (status) {
                    status.textContent = `🎵 ${musicPlayer.playlist.length} canciones cargadas`;
                    status.style.color = '#00cc66';
                }
                
                // Seleccionar primera canción automáticamente
                if (musicPlayer.playlist.length > 0) {
                    selectTrack(0);
                }
            } else {
                // No hay archivos - mostrar mensaje y usar modo demo
                musicPlayer.isLoaded = true;
                musicPlayer.isLoading = false;
                
                if (status) {
                    status.textContent = '📂 No hay canciones en D:/Music/';
                    status.style.color = '#9370db';
                }
                
                // Crear playlist de demostración con canciones online
                createDemoPlaylist();
            }
        })
        .catch(err => {
            console.error('❌ Error cargando música:', err);
            musicPlayer.isLoading = false;
            
            if (status) {
                status.textContent = '❌ Error cargando canciones';
                status.style.color = '#ff4444';
            }
            
            // Si falla la carga, usar modo demo
            createDemoPlaylist();
        });
}

// ═══ PLAYLIST DE DEMOSTRACIÓN (SI NO HAY ARCHIVOS) ═══
function createDemoPlaylist() {
    console.log('🎵 Usando playlist de demostración...');
    
    // Canciones de muestra (dominios públicos / libres)
    musicPlayer.playlist = [
        { 
            name: '🎵 SoundHelix - Song 1', 
            url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
            isDemo: true
        },
        { 
            name: '🎵 SoundHelix - Song 2', 
            url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3',
            isDemo: true
        },
        { 
            name: '🎵 SoundHelix - Song 3', 
            url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
            isDemo: true
        },
        { 
            name: '🎵 SoundHelix - Song 4', 
            url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3',
            isDemo: true
        }
    ];
    
    musicPlayer.isLoaded = true;
    updatePlaylistUI();
    
    const status = document.getElementById('music-status');
    if (status) {
        status.textContent = '🎵 Modo Demo - Archivos de ejemplo';
        status.style.color = '#ffaa00';
    }
    
    if (musicPlayer.playlist.length > 0) {
        selectTrack(0);
    }
}

// ═══ ACTUALIZAR PLAYLIST UI ═══
function updatePlaylistUI() {
    const playlistDiv = document.getElementById('music-playlist');
    if (!playlistDiv) return;

    if (musicPlayer.playlist.length === 0) {
        playlistDiv.innerHTML = `
            <div style="color:#9370db;text-align:center;padding:20px;">
                🎵 No hay canciones disponibles<br>
                <span style="font-size:11px;">Sube archivos .mp3, .wav, .ogg a D:/Music/</span>
            </div>
        `;
        return;
    }

    let html = '';
    musicPlayer.playlist.forEach((track, index) => {
        const isActive = index === musicPlayer.currentTrack;
        const isPlaying = isActive && musicPlayer.isPlaying;
        const isDemo = track.isDemo || false;
        
        html += `
            <div style="
                padding: 8px 12px;
                margin: 3px 0;
                border-radius: 4px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: ${isActive ? 'rgba(106,13,173,0.35)' : 'transparent'};
                border-left: 3px solid ${isActive ? '#da70d6' : 'transparent'};
                transition: all 0.2s;
                hover: background: rgba(75,0,130,0.2);
            " onclick="selectTrack(${index})">
                <span style="color:${isPlaying ? '#da70d6' : (isActive ? '#e6e6fa' : '#9370db')};">
                    ${isPlaying ? '▶️' : (isActive ? '⏸️' : (isDemo ? '☁️' : '🎵'))} 
                    ${track.name}
                </span>
                <span style="font-size:10px;color:#6a0dad;">${index + 1}</span>
            </div>
        `;
    });
    playlistDiv.innerHTML = html;
}

// ═══ SELECCIONAR CANCIÓN ═══
function selectTrack(index) {
    if (index < 0 || index >= musicPlayer.playlist.length) {
        console.warn('⚠️ Índice fuera de rango:', index);
        return;
    }

    // Detener reproducción actual
    if (musicPlayer.audio) {
        musicPlayer.audio.pause();
        musicPlayer.audio = null;
    }
    if (musicPlayer.progressInterval) {
        clearInterval(musicPlayer.progressInterval);
        musicPlayer.progressInterval = null;
    }

    musicPlayer.currentTrack = index;
    musicPlayer.isPlaying = false;
    musicPlayer.progress = 0;

    const track = musicPlayer.playlist[index];
    const info = document.getElementById('music-info');
    const status = document.getElementById('music-status');
    
    console.log(`🎵 Seleccionando: ${track.name} (${track.url})`);
    
    if (info) {
        info.textContent = `⏳ Cargando: ${track.name}...`;
        info.style.color = '#ffaa00';
    }

    // Crear nuevo audio
    const audio = new Audio();
    audio.src = track.url;
    audio.volume = musicPlayer.volume / 100;
    musicPlayer.audio = audio;

    // ═══ EVENTOS DEL AUDIO ═══
    audio.addEventListener('loadstart', function() {
        console.log('🔄 Cargando audio...');
        if (info) {
            info.textContent = `⏳ Cargando: ${track.name}...`;
            info.style.color = '#ffaa00';
        }
    });

    audio.addEventListener('loadedmetadata', function() {
        musicPlayer.duration = this.duration;
        updateDurationUI();
        console.log(`📊 Duración: ${this.duration} segundos`);
        if (info) {
            info.textContent = `⏸️ ${track.name} (${formatTime(this.duration)})`;
            info.style.color = '#d8bfd8';
        }
        // Actualizar barra de progreso
        const progressBar = document.getElementById('music-progress');
        if (progressBar) progressBar.style.width = '0%';
    });

    audio.addEventListener('timeupdate', function() {
        if (this.duration > 0 && !isNaN(this.duration)) {
            const pct = (this.currentTime / this.duration) * 100;
            const progressBar = document.getElementById('music-progress');
            if (progressBar) progressBar.style.width = Math.min(pct, 100) + '%';
            
            const timeDisplay = document.getElementById('music-time');
            if (timeDisplay) {
                timeDisplay.textContent = formatTime(this.currentTime);
            }
        }
    });

    audio.addEventListener('canplaythrough', function() {
        console.log('✅ Audio listo para reproducir');
        if (info) {
            info.textContent = `⏸️ ${track.name} (listo)`;
            info.style.color = '#d8bfd8';
        }
        // Auto-reproducir
        audio.play()
            .then(() => {
                musicPlayer.isPlaying = true;
                if (info) {
                    info.textContent = `▶️ ${track.name}`;
                    info.style.color = '#da70d6';
                }
                updatePlaylistUI();
                console.log('▶️ Reproduciendo:', track.name);
            })
            .catch(err => {
                console.warn('⚠️ Autoplay bloqueado:', err);
                if (info) {
                    info.textContent = `⏸️ ${track.name} (click play para reproducir)`;
                    info.style.color = '#9370db';
                }
                musicPlayer.isPlaying = false;
                updatePlaylistUI();
            });
    });

    audio.addEventListener('error', function(e) {
        const errorCode = this.error ? this.error.code : 'desconocido';
        const errorMsg = this.error ? this.error.message : 'Error desconocido';
        console.error('❌ Error reproduciendo:', errorCode, errorMsg);
        console.error('   URL:', this.src);
        
        if (info) {
            info.textContent = `❌ Error: ${track.name} (${errorMsg})`;
            info.style.color = '#ff4444';
        }
        musicPlayer.isPlaying = false;
        updatePlaylistUI();
        
        // Si es un error 404, sugerir que el archivo no existe
        if (errorCode === 4) { // MEDIA_ERR_SRC_NOT_SUPPORTED
            if (status) {
                status.textContent = '❌ Archivo no encontrado o formato no soportado';
                status.style.color = '#ff4444';
            }
        }
    });

    audio.addEventListener('ended', function() {
        console.log('⏹️ Canción terminada');
        musicPlayer.isPlaying = false;
        if (musicPlayer.progressInterval) {
            clearInterval(musicPlayer.progressInterval);
            musicPlayer.progressInterval = null;
        }
        if (info) {
            info.textContent = `⏹️ ${track.name} - Terminado`;
            info.style.color = '#9370db';
        }
        // Auto-siguiente después de 1 segundo
        setTimeout(() => musicNext(), 1000);
    });

    updatePlaylistUI();
    updateDurationUI();
}

// ═══ FORMATO DE TIEMPO ═══
function formatTime(seconds) {
    if (!seconds || isNaN(seconds) || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ═══ ACTUALIZAR DURACIÓN UI ═══
function updateDurationUI() {
    const durationDisplay = document.getElementById('music-duration');
    if (durationDisplay) {
        durationDisplay.textContent = formatTime(musicPlayer.duration);
    }
}

// ═══ REPRODUCIR ═══
function musicPlay() {
    const info = document.getElementById('music-info');
    if (!musicPlayer.audio) {
        if (musicPlayer.playlist.length > 0) {
            selectTrack(musicPlayer.currentTrack || 0);
        } else {
            if (info) info.textContent = '❌ No hay canciones cargadas';
            loadMusicFiles();
        }
        return;
    }

    musicPlayer.audio.play()
        .then(() => {
            musicPlayer.isPlaying = true;
            const track = musicPlayer.playlist[musicPlayer.currentTrack];
            if (info && track) {
                info.textContent = `▶️ ${track.name}`;
                info.style.color = '#da70d6';
            }
            updatePlaylistUI();
        })
        .catch(err => {
            console.error('❌ Error reproduciendo:', err);
            if (info) info.textContent = '❌ Error al reproducir';
        });
}

// ═══ PAUSAR ═══
function musicPause() {
    if (!musicPlayer.audio) return;
    musicPlayer.audio.pause();
    musicPlayer.isPlaying = false;
    const track = musicPlayer.playlist[musicPlayer.currentTrack];
    const info = document.getElementById('music-info');
    if (info && track) {
        info.textContent = `⏸️ ${track.name}`;
        info.style.color = '#9370db';
    }
    updatePlaylistUI();
}

// ═══ SIGUIENTE ═══
function musicNext() {
    if (musicPlayer.playlist.length === 0) {
        loadMusicFiles();
        return;
    }
    const nextIndex = (musicPlayer.currentTrack + 1) % musicPlayer.playlist.length;
    selectTrack(nextIndex);
}

// ═══ ANTERIOR ═══
function musicPrev() {
    if (musicPlayer.playlist.length === 0) return;
    const prevIndex = (musicPlayer.currentTrack - 1 + musicPlayer.playlist.length) % musicPlayer.playlist.length;
    selectTrack(prevIndex);
}

// ═══ VOLUMEN ═══
function musicVolumeUp() {
    musicPlayer.volume = Math.min(100, musicPlayer.volume + 10);
    if (musicPlayer.audio) {
        musicPlayer.audio.volume = musicPlayer.volume / 100;
    }
    const info = document.getElementById('music-info');
    if (info) {
        info.textContent = `🔊 Volumen: ${musicPlayer.volume}%`;
        info.style.color = '#ffaa00';
        setTimeout(() => {
            if (musicPlayer.isPlaying && musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `▶️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
                info.style.color = '#da70d6';
            } else if (musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `⏸️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
                info.style.color = '#9370db';
            }
        }, 1500);
    }
}

function musicVolumeDown() {
    musicPlayer.volume = Math.max(0, musicPlayer.volume - 10);
    if (musicPlayer.audio) {
        musicPlayer.audio.volume = musicPlayer.volume / 100;
    }
    const info = document.getElementById('music-info');
    if (info) {
        info.textContent = `🔉 Volumen: ${musicPlayer.volume}%`;
        info.style.color = '#ffaa00';
        setTimeout(() => {
            if (musicPlayer.isPlaying && musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `▶️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
                info.style.color = '#da70d6';
            } else if (musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `⏸️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
                info.style.color = '#9370db';
            }
        }, 1500);
    }
}

// ═══ INICIALIZAR ═══
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 Inicializando reproductor de música...');
    
    const win = document.getElementById('win-music');
    if (win) {
        // Cargar canciones al abrir la ventana
        const observer = new MutationObserver(() => {
            if (win.style.display !== 'none') {
                if (!musicPlayer.isLoaded && !musicPlayer.isLoading) {
                    console.log('📂 Ventana de música abierta, cargando canciones...');
                    loadMusicFiles();
                }
            }
        });
        observer.observe(win, { attributes: true, attributeFilter: ['style'] });

        // Si la ventana ya está visible, cargar
        setTimeout(() => {
            if (win.style.display !== 'none' && !musicPlayer.isLoaded && !musicPlayer.isLoading) {
                loadMusicFiles();
            }
        }, 500);
    }
});

// ═══ EXPORTAR ═══
window.musicPlay = musicPlay;
window.musicPause = musicPause;
window.musicNext = musicNext;
window.musicPrev = musicPrev;
window.musicVolumeUp = musicVolumeUp;
window.musicVolumeDown = musicVolumeDown;
window.selectTrack = selectTrack;
window.loadMusicFiles = loadMusicFiles;

console.log('🎵 Reproductor de música real cargado correctamente');