// KALM OS v4.3 - Reproductor de Música Moderno v2.0

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
    isLoading: false,
    shuffle: false,
    repeat: false,
    history: []
};

// ═══ PLAYLIST DE DEMOSTRACIÓN ═══
const DEMO_PLAYLIST = [
    { 
        name: 'Beethoven - Sonata No. 8 (Pathétique)', 
        artist: 'Beethoven',
        url: 'https://upload.wikimedia.org/wikipedia/commons/5/5d/Beethoven_-_Sonata_No._8_%28Path%C3%A9tique%29_in_C_minor_Op._13%2C_2nd_movement.ogg',
        isDemo: true,
        cover: '🎵'
    },
    { 
        name: 'Grieg - Peer Gynt Suite No. 1 (Morning)', 
        artist: 'Grieg',
        url: 'https://upload.wikimedia.org/wikipedia/commons/6/6c/Grieg_-_Peer_Gynt_Suite_No._1_%28movement_1%29.ogg',
        isDemo: true,
        cover: '🎶'
    },
    { 
        name: 'Bach - Brandenburg Concerto No. 1', 
        artist: 'Bach',
        url: 'https://upload.wikimedia.org/wikipedia/commons/9/98/Bach_-_Brandenburg_Concerto_No._1_in_F_Major_BWV_1046_%281st_movement%29.ogg',
        isDemo: true,
        cover: '🎻'
    }
];

// ═══ FUNCIÓN PRINCIPAL DE CARGA ═══
function loadMusicFiles() {
    const status = document.getElementById('music-status');
    const playlistDiv = document.getElementById('music-playlist');
    
    if (musicPlayer.isLoading) return;
    musicPlayer.isLoading = true;
    
    updateStatus('⏳ Cargando canciones...', '#ffaa00');
    
    if (playlistDiv) {
        playlistDiv.innerHTML = `
            <div style="color:#9370db;text-align:center;padding:30px;">
                <div style="font-size:32px;margin-bottom:10px;">🎵</div>
                <div style="font-size:13px;">Cargando tu música...</div>
            </div>
        `;
    }

    // Establecer playlist de demostración como base
    musicPlayer.playlist = DEMO_PLAYLIST.map(track => ({ ...track }));
    
    // Intentar cargar archivos locales
    fetch('/api/music/list')
        .then(r => r.ok ? r.json() : Promise.reject('Error en la respuesta'))
        .then(data => {
            if (data.ok && data.files && data.files.length > 0) {
                const validFiles = data.files.filter(f => f.size > 50000);
                
                if (validFiles.length > 0) {
                    const localFiles = validFiles.map(f => ({
                        name: f.name.replace(/\.[^.]+$/, ''),
                        artist: 'Local',
                        path: f.path,
                        url: f.url,
                        isDemo: false,
                        size: f.size,
                        cover: '📁'
                    }));
                    
                    musicPlayer.playlist = [...localFiles, ...DEMO_PLAYLIST];
                    updateStatus(`🎵 ${localFiles.length} locales + ${DEMO_PLAYLIST.length} demo`, '#00cc66');
                } else {
                    updateStatus('⚠️ Solo modo demo (archivos pequeños)', '#ffaa00');
                }
            } else {
                updateStatus('🎵 Modo Demo', '#ffaa00');
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
            updateStatus('🎵 Modo Demo (sin conexión)', '#ffaa00');
            if (musicPlayer.playlist.length > 0) selectTrack(0);
        });
}

// ═══ FUNCIONES DE ESTADO Y UI ═══
function updateStatus(text, color = '#9370db') {
    const status = document.getElementById('music-status');
    if (status) {
        status.textContent = text;
        status.style.color = color;
    }
}

function updateInfo(text, color = '#d8bfd8') {
    const info = document.getElementById('music-info');
    if (info) {
        info.textContent = text;
        info.style.color = color;
    }
}

function updateProgress(percent) {
    const bar = document.getElementById('music-progress');
    if (bar) bar.style.width = Math.min(percent, 100) + '%';
}

function updateTime(current, total) {
    const timeEl = document.getElementById('music-time');
    const durationEl = document.getElementById('music-duration');
    if (timeEl) timeEl.textContent = current || '0:00';
    if (durationEl) durationEl.textContent = total || '0:00';
}

function formatTime(seconds) {
    if (!seconds || isNaN(seconds) || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ═══ ACTUALIZAR PLAYLIST UI ═══
function updatePlaylistUI() {
    const playlistDiv = document.getElementById('music-playlist');
    if (!playlistDiv) return;

    if (musicPlayer.playlist.length === 0) {
        playlistDiv.innerHTML = `
            <div style="color:#9370db;text-align:center;padding:30px;">
                <div style="font-size:32px;margin-bottom:10px;">🎵</div>
                <div style="font-size:13px;">No hay canciones disponibles</div>
            </div>
        `;
        return;
    }

    let html = '';
    const current = musicPlayer.currentTrack;
    
    musicPlayer.playlist.forEach((track, index) => {
        const isActive = index === current;
        const isPlaying = isActive && musicPlayer.isPlaying;
        const isDemo = track.isDemo || false;
        const bgColor = isActive ? 'rgba(106,13,173,0.3)' : 'transparent';
        const borderColor = isActive ? '#da70d6' : 'transparent';
        const textColor = isPlaying ? '#da70d6' : (isActive ? '#e6e6fa' : '#9370db');
        const icon = isPlaying ? '▶️' : (isActive ? '⏸️' : (isDemo ? '☁️' : '🎵'));
        const cover = track.cover || (isDemo ? '🎵' : '📁');
        
        html += `
            <div class="playlist-item" data-index="${index}"
                style="
                    padding: 10px 14px;
                    margin: 4px 0;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    background: ${bgColor};
                    border-left: 3px solid ${borderColor};
                    transition: all 0.25s ease;
                "
                onclick="selectTrack(${index})"
                onmouseover="this.style.background='rgba(75,0,130,0.25)'"
                onmouseout="this.style.background='${bgColor}'">
                <span style="font-size:18px;width:30px;text-align:center;">${cover}</span>
                <span style="flex:1;color:${textColor};font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    ${icon} ${track.name}
                </span>
                <span style="font-size:11px;color:#6a0dad;">
                    ${track.artist || (isDemo ? 'Demo' : 'Local')}
                </span>
                <span style="font-size:10px;color:#4b0082;">${isDemo ? '☁️' : '📁'}</span>
            </div>
        `;
    });
    
    playlistDiv.innerHTML = html;
    
    // Scroll al elemento activo
    setTimeout(() => {
        const activeItem = playlistDiv.querySelector(`.playlist-item[data-index="${current}"]`);
        if (activeItem) {
            activeItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }, 100);
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
    musicPlayer.duration = 0;

    const track = musicPlayer.playlist[index];
    
    console.log(`🎵 Seleccionando: ${track.name}`);
    updateInfo(`⏳ Cargando: ${track.name}...`, '#ffaa00');
    updateProgress(0);
    updateTime('0:00', '0:00');

    // Crear nuevo audio
    const audio = new Audio();
    audio.src = track.url;
    audio.volume = musicPlayer.volume / 100;
    audio.crossOrigin = 'anonymous';
    musicPlayer.audio = audio;

    // ═══ EVENTOS DEL AUDIO ═══
    audio.addEventListener('loadedmetadata', function() {
        musicPlayer.duration = this.duration;
        updateTime(formatTime(0), formatTime(this.duration));
        updateInfo(`⏸️ ${track.name} (${formatTime(this.duration)})`, '#d8bfd8');
        updateProgress(0);
        console.log(`📊 Duración: ${this.duration}s`);
    });

    audio.addEventListener('timeupdate', function() {
        if (this.duration > 0 && !isNaN(this.duration)) {
            const pct = (this.currentTime / this.duration) * 100;
            updateProgress(pct);
            updateTime(formatTime(this.currentTime), formatTime(this.duration));
        }
    });

    audio.addEventListener('canplaythrough', function() {
        console.log('✅ Audio listo');
        updateInfo(`⏸️ ${track.name} (listo)`, '#d8bfd8');
        autoPlay();
    });

    audio.addEventListener('play', function() {
        musicPlayer.isPlaying = true;
        updateInfo(`▶️ ${track.name}`, '#da70d6');
        updatePlaylistUI();
        document.querySelector('.btn-play')?.classList.add('playing');
    });

    audio.addEventListener('pause', function() {
        musicPlayer.isPlaying = false;
        updateInfo(`⏸️ ${track.name}`, '#9370db');
        updatePlaylistUI();
        document.querySelector('.btn-play')?.classList.remove('playing');
    });

    audio.addEventListener('error', function(e) {
        const errorMsg = this.error ? this.error.message : 'Error desconocido';
        console.error('❌ Error de audio:', errorMsg);
        updateInfo(`❌ Error: ${track.name}`, '#ff4444');
        musicPlayer.isPlaying = false;
        updatePlaylistUI();
        
        // Reintentar o saltar
        if (track.isDemo) {
            setTimeout(() => selectTrack(index), 2000);
        } else {
            setTimeout(() => musicNext(), 3000);
        }
    });

    audio.addEventListener('ended', function() {
        console.log('⏹️ Canción terminada');
        musicPlayer.isPlaying = false;
        if (musicPlayer.repeat) {
            selectTrack(musicPlayer.currentTrack);
        } else {
            setTimeout(() => musicNext(), 500);
        }
    });

    updatePlaylistUI();
}

// ═══ AUTO-REPRODUCIR ═══
function autoPlay() {
    if (!musicPlayer.audio) return;
    musicPlayer.audio.play()
        .then(() => {
            console.log('▶️ Reproduciendo automáticamente');
        })
        .catch(err => {
            console.log('⏸️ Autoplay bloqueado, esperando interacción');
            updateInfo('▶️ Click para reproducir', '#9370db');
        });
}

// ═══ CONTROLES PRINCIPALES ═══
function musicPlay() {
    if (!musicPlayer.audio) {
        if (musicPlayer.playlist.length > 0) {
            selectTrack(musicPlayer.currentTrack || 0);
        } else {
            loadMusicFiles();
        }
        return;
    }

    if (musicPlayer.isPlaying) {
        musicPlayer.audio.pause();
    } else {
        musicPlayer.audio.play()
            .then(() => {
                musicPlayer.isPlaying = true;
                updatePlaylistUI();
            })
            .catch(err => {
                console.error('❌ Error:', err);
                updateInfo('❌ Error al reproducir', '#ff4444');
            });
    }
}

function musicPause() {
    if (musicPlayer.audio && musicPlayer.isPlaying) {
        musicPlayer.audio.pause();
    }
}

function musicNext() {
    if (musicPlayer.playlist.length === 0) {
        loadMusicFiles();
        return;
    }
    let nextIndex;
    if (musicPlayer.shuffle) {
        do {
            nextIndex = Math.floor(Math.random() * musicPlayer.playlist.length);
        } while (nextIndex === musicPlayer.currentTrack && musicPlayer.playlist.length > 1);
    } else {
        nextIndex = (musicPlayer.currentTrack + 1) % musicPlayer.playlist.length;
    }
    selectTrack(nextIndex);
}

function musicPrev() {
    if (musicPlayer.playlist.length === 0) return;
    if (musicPlayer.audio && musicPlayer.audio.currentTime > 3) {
        selectTrack(musicPlayer.currentTrack);
    } else {
        const prevIndex = (musicPlayer.currentTrack - 1 + musicPlayer.playlist.length) % musicPlayer.playlist.length;
        selectTrack(prevIndex);
    }
}

function musicShuffle() {
    musicPlayer.shuffle = !musicPlayer.shuffle;
    const btn = document.querySelector('.btn-shuffle');
    if (btn) {
        btn.style.color = musicPlayer.shuffle ? '#da70d6' : '#9370db';
        btn.style.borderColor = musicPlayer.shuffle ? '#da70d6' : 'transparent';
    }
    updateInfo(`🔀 Shuffle ${musicPlayer.shuffle ? 'activado' : 'desactivado'}`, '#ffaa00');
    setTimeout(() => {
        if (musicPlayer.isPlaying && musicPlayer.playlist[musicPlayer.currentTrack]) {
            updateInfo(`▶️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`, '#da70d6');
        }
    }, 1000);
}

function musicRepeat() {
    musicPlayer.repeat = !musicPlayer.repeat;
    const btn = document.querySelector('.btn-repeat');
    if (btn) {
        btn.style.color = musicPlayer.repeat ? '#da70d6' : '#9370db';
        btn.style.borderColor = musicPlayer.repeat ? '#da70d6' : 'transparent';
    }
    updateInfo(`🔁 Repetición ${musicPlayer.repeat ? 'activada' : 'desactivada'}`, '#ffaa00');
    setTimeout(() => {
        if (musicPlayer.isPlaying && musicPlayer.playlist[musicPlayer.currentTrack]) {
            updateInfo(`▶️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`, '#da70d6');
        }
    }, 1000);
}

function musicVolumeUp() {
    musicPlayer.volume = Math.min(100, musicPlayer.volume + 10);
    if (musicPlayer.audio) {
        musicPlayer.audio.volume = musicPlayer.volume / 100;
    }
    updateVolumeUI();
}

function musicVolumeDown() {
    musicPlayer.volume = Math.max(0, musicPlayer.volume - 10);
    if (musicPlayer.audio) {
        musicPlayer.audio.volume = musicPlayer.volume / 100;
    }
    updateVolumeUI();
}

function updateVolumeUI() {
    updateInfo(`🔊 Volumen: ${musicPlayer.volume}%`, '#ffaa00');
    const volBar = document.querySelector('.volume-bar');
    if (volBar) volBar.style.width = musicPlayer.volume + '%';
    setTimeout(() => {
        if (musicPlayer.isPlaying && musicPlayer.playlist[musicPlayer.currentTrack]) {
            updateInfo(`▶️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`, '#da70d6');
        } else if (musicPlayer.playlist[musicPlayer.currentTrack]) {
            updateInfo(`⏸️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`, '#9370db');
        }
    }, 1200);
}

// ═══ FUNCIONES DE PROGRESO (Click en barra) ═══
function seekTo(e) {
    if (!musicPlayer.audio || !musicPlayer.duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX || e.touches?.[0]?.clientX || 0) - rect.left;
    const pct = Math.max(0, Math.min(1, x / rect.width));
    const newTime = pct * musicPlayer.duration;
    musicPlayer.audio.currentTime = newTime;
    updateProgress(pct * 100);
    updateTime(formatTime(newTime), formatTime(musicPlayer.duration));
}

// ═══ INICIALIZAR ═══
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 Inicializando reproductor moderno...');
    
    const win = document.getElementById('win-music');
    if (win) {
        const observer = new MutationObserver(() => {
            if (win.style.display !== 'none') {
                if (!musicPlayer.isLoaded && !musicPlayer.isLoading) {
                    console.log('📂 Ventana abierta, cargando música...');
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

    // Configurar barra de progreso clickeable
    const progressContainer = document.querySelector('.progress-container');
    if (progressContainer) {
        progressContainer.addEventListener('click', seekTo);
        progressContainer.addEventListener('touchstart', function(e) {
            seekTo(e);
        });
    }
});

// ═══ EXPORTAR ═══
window.musicPlay = musicPlay;
window.musicPause = musicPause;
window.musicNext = musicNext;
window.musicPrev = musicPrev;
window.musicVolumeUp = musicVolumeUp;
window.musicVolumeDown = musicVolumeDown;
window.musicShuffle = musicShuffle;
window.musicRepeat = musicRepeat;
window.selectTrack = selectTrack;
window.loadMusicFiles = loadMusicFiles;

console.log('🎵 Reproductor Moderno v2.0 cargado');
console.log('📌 Características: Shuffle, Repeat, progreso interactivo');
