// KALM OS v4.3 - Reproductor de Música REAL (CON DIAGNÓSTICO)

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

// ═══ PLAYLIST DE DEMOSTRACIÓN (URLs CONFIRMADAS) ═══
const DEMO_PLAYLIST = [
    { 
        name: '🎵 Classical - Beethoven', 
        url: 'https://upload.wikimedia.org/wikipedia/commons/5/5d/Beethoven_-_Sonata_No._8_%28Path%C3%A9tique%29_in_C_minor_Op._13%2C_2nd_movement.ogg',
        isDemo: true
    },
    { 
        name: '🎵 Classical - Grieg', 
        url: 'https://upload.wikimedia.org/wikipedia/commons/6/6c/Grieg_-_Peer_Gynt_Suite_No._1_%28movement_1%29.ogg',
        isDemo: true
    },
    { 
        name: '🎵 Classical - Bach', 
        url: 'https://upload.wikimedia.org/wikipedia/commons/9/98/Bach_-_Brandenburg_Concerto_No._1_in_F_Major_BWV_1046_%281st_movement%29.ogg',
        isDemo: true
    }
];

// ═══ CARGAR CANCIONES DESDE D:/Music/ ═══
function loadMusicFiles() {
    const status = document.getElementById('music-status');
    const playlistDiv = document.getElementById('music-playlist');
    
    if (musicPlayer.isLoading) return;
    musicPlayer.isLoading = true;
    
    if (status) {
        status.textContent = '⏳ Cargando canciones...';
        status.style.color = '#ffaa00';
    }
    
    if (playlistDiv) {
        playlistDiv.innerHTML = `
            <div style="color:#9370db;text-align:center;padding:20px;">
                ⏳ Buscando archivos de música...
            </div>
        `;
    }

    // Primero, establecer la playlist de demostración como base
    musicPlayer.playlist = DEMO_PLAYLIST.map(track => ({ ...track }));
    
    // Luego intentar cargar archivos locales
    fetch('/api/music/list')
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(data => {
            console.log('📥 Respuesta /api/music/list:', data);
            
            if (data.ok && data.files && data.files.length > 0) {
                // FILTRAR ARCHIVOS VÁLIDOS (más de 50KB)
                const validFiles = data.files.filter(f => f.size > 50000);
                console.log(`📁 Archivos válidos: ${validFiles.length} de ${data.files.length}`);
                
                if (validFiles.length > 0) {
                    const localFiles = validFiles.map(f => ({
                        name: f.name,
                        path: f.path,
                        url: f.url,
                        isDemo: false,
                        size: f.size
                    }));
                    
                    musicPlayer.playlist = [...localFiles, ...DEMO_PLAYLIST];
                    
                    const localCount = localFiles.length;
                    if (status) {
                        status.textContent = `🎵 ${localCount} canciones locales + ${DEMO_PLAYLIST.length} demo`;
                        status.style.color = '#00cc66';
                    }
                } else {
                    if (status) {
                        status.textContent = `⚠️ Archivos locales corruptos (${data.files.length} archivos < 50KB)`;
                        status.style.color = '#ffaa00';
                    }
                }
            } else {
                if (status) {
                    status.textContent = '🎵 Modo Demo - Sin archivos locales válidos';
                    status.style.color = '#ffaa00';
                }
                console.log('🎵 Usando solo playlist de demostración');
            }
            
            musicPlayer.isLoaded = true;
            musicPlayer.isLoading = false;
            updatePlaylistUI();
            
            if (musicPlayer.playlist.length > 0) {
                selectTrack(0);
            }
        })
        .catch(err => {
            console.error('❌ Error cargando música:', err);
            musicPlayer.isLoading = false;
            
            musicPlayer.playlist = DEMO_PLAYLIST.map(track => ({ ...track }));
            musicPlayer.isLoaded = true;
            updatePlaylistUI();
            
            if (status) {
                status.textContent = '🎵 Modo Demo (error de conexión)';
                status.style.color = '#ffaa00';
            }
            
            if (musicPlayer.playlist.length > 0) {
                selectTrack(0);
            }
        });
}

// ═══ ACTUALIZAR PLAYLIST UI ═══
function updatePlaylistUI() {
    const playlistDiv = document.getElementById('music-playlist');
    if (!playlistDiv) return;

    if (musicPlayer.playlist.length === 0) {
        playlistDiv.innerHTML = `
            <div style="color:#9370db;text-align:center;padding:20px;">
                🎵 No hay canciones disponibles
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
            " onclick="selectTrack(${index})"
            onmouseover="this.style.background='rgba(75,0,130,0.2)'"
            onmouseout="this.style.background='${isActive ? 'rgba(106,13,173,0.35)' : 'transparent'}'">
                <span style="color:${isPlaying ? '#da70d6' : (isActive ? '#e6e6fa' : '#9370db')};">
                    ${isPlaying ? '▶️' : (isActive ? '⏸️' : (isDemo ? '☁️' : '🎵'))} 
                    ${track.name}
                </span>
                <span style="font-size:10px;color:#6a0dad;">${isDemo ? 'demo' : '📁'}</span>
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
    
    console.log(`🎵 Seleccionando: ${track.name}`);
    console.log(`   URL: ${track.url}`);
    console.log(`   Tipo: ${track.isDemo ? 'Demo' : 'Local'}`);
    
    if (info) {
        info.textContent = `⏳ Cargando: ${track.name}...`;
        info.style.color = '#ffaa00';
    }

    // Crear nuevo audio
    const audio = new Audio();
    audio.src = track.url;
    audio.volume = musicPlayer.volume / 100;
    audio.crossOrigin = 'anonymous';
    musicPlayer.audio = audio;

    // ═══ EVENTOS DEL AUDIO ═══
    audio.addEventListener('loadedmetadata', function() {
        musicPlayer.duration = this.duration;
        updateDurationUI();
        console.log(`📊 Duración: ${this.duration} segundos`);
        if (info) {
            info.textContent = `⏸️ ${track.name} (${formatTime(this.duration)})`;
            info.style.color = '#d8bfd8';
        }
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
                console.warn('⚠️ Autoplay bloqueado:', err.message);
                if (info) {
                    info.textContent = `⏸️ ${track.name} (click ▶️ para reproducir)`;
                    info.style.color = '#9370db';
                }
                musicPlayer.isPlaying = false;
                updatePlaylistUI();
            });
    });

    audio.addEventListener('error', function(e) {
        const errorCode = this.error ? this.error.code : 'desconocido';
        const errorMsg = this.error ? this.error.message : 'Error desconocido';
        
        console.error('❌ ERROR DE AUDIO:');
        console.error('   Código:', errorCode);
        console.error('   Mensaje:', errorMsg);
        console.error('   URL:', this.src);
        console.error('   Canción:', track.name);
        console.error('   Es demo:', track.isDemo);
        
        if (info) {
            info.textContent = `❌ Error: ${track.name}`;
            info.style.color = '#ff4444';
        }
        
        musicPlayer.isPlaying = false;
        updatePlaylistUI();
        
        // Saltar a la siguiente canción después de 3 segundos
        if (!track.isDemo) {
            setTimeout(() => {
                console.log('⏭️ Saltando a la siguiente canción...');
                musicNext();
            }, 3000);
        } else {
            // Si es demo, intentar de nuevo (puede ser CORS)
            setTimeout(() => {
                console.log('🔄 Reintentando demo...');
                selectTrack(index);
            }, 2000);
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
        const observer = new MutationObserver(() => {
            if (win.style.display !== 'none') {
                if (!musicPlayer.isLoaded && !musicPlayer.isLoading) {
                    console.log('📂 Ventana de música abierta, cargando canciones...');
                    loadMusicFiles();
                }
            }
        });
        observer.observe(win, { attributes: true, attributeFilter: ['style'] });

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

console.log('🎵 Reproductor de música cargado correctamente');
console.log('📌 Modo: Demo + Archivos locales (filtrados por tamaño)');
