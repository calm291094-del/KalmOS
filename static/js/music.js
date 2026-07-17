// KALM OS v4.3 - Reproductor de Música REAL

let musicPlayer = {
    isPlaying: false,
    currentTrack: 0,
    playlist: [],
    volume: 70,
    progress: 0,
    duration: 0,
    audio: null,
    progressInterval: null,
    isLoaded: false
};

// ═══ CARGAR CANCIONES DESDE D:/Music/ ═══
function loadMusicFiles() {
    const status = document.getElementById('music-status');
    if (status) {
        status.textContent = '⏳ Cargando canciones...';
        status.style.color = '#ffaa00';
    }

    fetch('/api/music/list')
        .then(r => {
            if (!r.ok) throw new Error('Error cargando música');
            return r.json();
        })
        .then(data => {
            if (data.ok && data.files && data.files.length > 0) {
                musicPlayer.playlist = data.files.map(f => ({
                    name: f.name,
                    path: f.path,
                    url: f.url
                }));
                musicPlayer.isLoaded = true;
                updatePlaylistUI();
                if (status) {
                    status.textContent = `🎵 ${musicPlayer.playlist.length} canciones cargadas`;
                    status.style.color = '#00cc66';
                }
                // Seleccionar primera canción
                if (musicPlayer.playlist.length > 0) {
                    selectTrack(0);
                }
            } else {
                musicPlayer.playlist = [];
                musicPlayer.isLoaded = true;
                updatePlaylistUI();
                if (status) {
                    status.textContent = '📂 No hay canciones en D:/Music/';
                    status.style.color = '#9370db';
                }
            }
        })
        .catch(err => {
            console.error('❌ Error cargando música:', err);
            if (status) {
                status.textContent = '❌ Error cargando canciones';
                status.style.color = '#ff4444';
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
                🎵 No hay canciones en D:/Music/<br>
                <span style="font-size:11px;">Sube archivos .mp3, .wav, .ogg, .flac</span>
            </div>
        `;
        return;
    }

    let html = '';
    musicPlayer.playlist.forEach((track, index) => {
        const isActive = index === musicPlayer.currentTrack;
        const isPlaying = isActive && musicPlayer.isPlaying;
        html += `
            <div style="
                padding: 6px 10px;
                margin: 2px 0;
                border-radius: 4px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: ${isActive ? 'rgba(106,13,173,0.3)' : 'transparent'};
                border-left: 3px solid ${isActive ? '#da70d6' : 'transparent'};
                transition: all 0.2s;
                hover: background: rgba(75,0,130,0.2);
            " onclick="selectTrack(${index})">
                <span style="color:${isPlaying ? '#da70d6' : (isActive ? '#e6e6fa' : '#9370db')}">
                    ${isPlaying ? '▶️' : (isActive ? '⏸️' : '🎵')} ${track.name}
                </span>
                <span style="font-size:10px;color:#6a0dad;">${index + 1}</span>
            </div>
        `;
    });
    playlistDiv.innerHTML = html;
}

// ═══ SELECCIONAR CANCIÓN ═══
function selectTrack(index) {
    if (index < 0 || index >= musicPlayer.playlist.length) return;

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
    if (info) {
        info.textContent = `⏸️ ${track.name}`;
    }

    // Crear nuevo audio
    const audio = new Audio(track.url);
    audio.volume = musicPlayer.volume / 100;
    musicPlayer.audio = audio;

    // Escuchar eventos
    audio.addEventListener('loadedmetadata', function() {
        musicPlayer.duration = this.duration;
        updateDurationUI();
    });

    audio.addEventListener('timeupdate', function() {
        if (this.duration > 0) {
            const pct = (this.currentTime / this.duration) * 100;
            const progressBar = document.getElementById('music-progress');
            if (progressBar) progressBar.style.width = Math.min(pct, 100) + '%';
            const timeDisplay = document.getElementById('music-time');
            if (timeDisplay) {
                const mins = Math.floor(this.currentTime / 60);
                const secs = Math.floor(this.currentTime % 60);
                timeDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
            }
        }
    });

    audio.addEventListener('ended', function() {
        musicPlayer.isPlaying = false;
        if (musicPlayer.progressInterval) {
            clearInterval(musicPlayer.progressInterval);
            musicPlayer.progressInterval = null;
        }
        const info = document.getElementById('music-info');
        if (info) info.textContent = `⏹️ ${track.name} - Terminado`;
        // Auto-siguiente
        setTimeout(() => musicNext(), 500);
    });

    audio.addEventListener('error', function(e) {
        console.error('❌ Error reproduciendo:', e);
        const info = document.getElementById('music-info');
        if (info) info.textContent = `❌ Error: ${track.name}`;
    });

    updatePlaylistUI();
    updateDurationUI();

    // Auto-reproducir
    audio.play()
        .then(() => {
            musicPlayer.isPlaying = true;
            if (info) info.textContent = `▶️ ${track.name}`;
            updatePlaylistUI();
        })
        .catch(err => {
            console.warn('⚠️ Autoplay bloqueado:', err);
            if (info) info.textContent = `⏸️ ${track.name} (click play para reproducir)`;
        });
}

// ═══ ACTUALIZAR DURACIÓN ═══
function updateDurationUI() {
    const durationDisplay = document.getElementById('music-duration');
    if (durationDisplay && musicPlayer.duration > 0) {
        const mins = Math.floor(musicPlayer.duration / 60);
        const secs = Math.floor(musicPlayer.duration % 60);
        durationDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// ═══ REPRODUCIR ═══
function musicPlay() {
    const info = document.getElementById('music-info');
    if (!musicPlayer.audio) {
        // Si no hay audio cargado, seleccionar primera canción
        if (musicPlayer.playlist.length > 0) {
            selectTrack(0);
        } else {
            if (info) info.textContent = '❌ No hay canciones cargadas';
        }
        return;
    }

    musicPlayer.audio.play()
        .then(() => {
            musicPlayer.isPlaying = true;
            const track = musicPlayer.playlist[musicPlayer.currentTrack];
            if (info) info.textContent = `▶️ ${track.name}`;
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
    if (info && track) info.textContent = `⏸️ ${track.name}`;
    updatePlaylistUI();
}

// ═══ SIGUIENTE ═══
function musicNext() {
    if (musicPlayer.playlist.length === 0) return;
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
        setTimeout(() => {
            if (musicPlayer.isPlaying && musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `▶️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
            } else if (musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `⏸️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
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
        setTimeout(() => {
            if (musicPlayer.isPlaying && musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `▶️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
            } else if (musicPlayer.playlist[musicPlayer.currentTrack]) {
                info.textContent = `⏸️ ${musicPlayer.playlist[musicPlayer.currentTrack].name}`;
            }
        }, 1500);
    }
}

// ═══ INICIALIZAR ═══
document.addEventListener('DOMContentLoaded', function() {
    const win = document.getElementById('win-music');
    if (win) {
        // Cargar canciones al abrir la ventana
        const observer = new MutationObserver(() => {
            if (win.style.display !== 'none') {
                if (!musicPlayer.isLoaded) {
                    loadMusicFiles();
                }
            }
        });
        observer.observe(win, { attributes: true, attributeFilter: ['style'] });

        // Si la ventana ya está visible, cargar
        setTimeout(() => {
            if (win.style.display !== 'none' && !musicPlayer.isLoaded) {
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

console.log('🎵 Reproductor de música real cargado');