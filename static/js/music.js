// KALM OS v4.3 - Reproductor de Música Moderno v2.2
// ✅ Eventos registrados UNA VEZ - Sin duplicados
// ✅ Auto-next, pausa, siguiente, anterior funcionan

let musicPlayer = {
    isPlaying: false,
    currentTrack: 0,
    playlist: [],
    volume: 70,
    progress: 0,
    duration: 0,
    audio: null,
    isLoaded: false,
    isLoading: false,
    shuffle: false,
    repeat: false
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

// ═══ CREAR AUDIO UNA SOLA VEZ ═══
// Esto es clave: un solo elemento audio, eventos registrados una vez
musicPlayer.audio = new Audio();
musicPlayer.audio.preload = 'auto';

// ═══ REGISTRAR EVENTOS UNA SOLA VEZ ═══
// Todos leen el estado actual de musicPlayer, no usan closures de canciones

musicPlayer.audio.addEventListener('loadedmetadata', function() {
    musicPlayer.duration = this.duration;
    var track = musicPlayer.playlist[musicPlayer.currentTrack];
    if (track) {
        updateInfo('⏸️ ' + track.name + ' (' + formatTime(this.duration) + ')', '#d8bfd8');
    }
    updateTime(formatTime(0), formatTime(this.duration));
    updateProgress(0);
    console.log('📊 Duración: ' + this.duration + 's');
});

musicPlayer.audio.addEventListener('timeupdate', function() {
    if (this.duration > 0 && !isNaN(this.duration)) {
        var pct = (this.currentTime / this.duration) * 100;
        updateProgress(pct);
        updateTime(formatTime(this.currentTime), formatTime(this.duration));
    }
});

musicPlayer.audio.addEventListener('play', function() {
    musicPlayer.isPlaying = true;
    var track = musicPlayer.playlist[musicPlayer.currentTrack];
    if (track) updateInfo('▶️ ' + track.name, '#da70d6');
    updatePlaylistUI();
    var playBtn = document.querySelector('.btn-play');
    if (playBtn) playBtn.classList.add('playing');
});

musicPlayer.audio.addEventListener('pause', function() {
    musicPlayer.isPlaying = false;
    var track = musicPlayer.playlist[musicPlayer.currentTrack];
    if (track) updateInfo('⏸️ ' + track.name, '#9370db');
    updatePlaylistUI();
    var playBtn = document.querySelector('.btn-play');
    if (playBtn) playBtn.classList.remove('playing');
});

musicPlayer.audio.addEventListener('error', function() {
    var track = musicPlayer.playlist[musicPlayer.currentTrack];
    var errorMsg = this.error ? this.error.message : 'Desconocido';
    console.error('❌ Error de audio:', errorMsg, track ? track.name : '');
    if (track) updateInfo('❌ Error: ' + track.name, '#ff4444');
    musicPlayer.isPlaying = false;
    updatePlaylistUI();
    // Saltar a la siguiente tras un error
    setTimeout(function() {
        if (track && track.isDemo) {
            selectTrack(musicPlayer.currentTrack);
        } else {
            goToNext();
        }
    }, 2000);
});

// ═══ ENDED - SIGUIENTE CANCIÓN ═══
musicPlayer.audio.addEventListener('ended', function() {
    console.log('⏹️ Canción terminada');
    musicPlayer.isPlaying = false;
    updatePlaylistUI();

    if (musicPlayer.repeat) {
        console.log('🔁 Repeat → reiniciando');
        this.currentTime = 0;
        this.play().catch(function() {});
        return;
    }

    goToNext();
});

// ═══ FUNCIÓN: IR A LA SIGUIENTE (reutilizable) ═══
function goToNext() {
    if (musicPlayer.playlist.length === 0) return;

    var nextIndex;
    if (musicPlayer.shuffle) {
        do {
            nextIndex = Math.floor(Math.random() * musicPlayer.playlist.length);
        } while (nextIndex === musicPlayer.currentTrack && musicPlayer.playlist.length > 1);
    } else {
        nextIndex = (musicPlayer.currentTrack + 1) % musicPlayer.playlist.length;
    }

    var nextTrack = musicPlayer.playlist[nextIndex];
    if (!nextTrack) return;

    console.log('⏭️ Siguiente → ' + nextTrack.name);

    musicPlayer.currentTrack = nextIndex;
    updateInfo('⏳ Cargando...', '#ffaa00');
    updateProgress(0);
    updateTime('0:00', '0:00');

    // Cambiar src en el MISMO audio (mantiene el gesto del usuario)
    musicPlayer.audio.src = nextTrack.url;
    musicPlayer.audio.load();

    // Reproducir inmediatamente
    musicPlayer.audio.play().then(function() {
        console.log('✅ Reproduciendo: ' + nextTrack.name);
    }).catch(function(err) {
        console.log('⏸️ Autoplay bloqueado:', err.message);
        updateInfo('▶️ Click ▶ para continuar', '#ffaa00');
    });

    // Seguridad: si en 8s no reproduce, forzar
    setTimeout(function() {
        if (!musicPlayer.isPlaying && musicPlayer.currentTrack === nextIndex) {
            console.log('⚠️ Timeout, forzando selectTrack');
            // No usamos selectTrack aquí para evitar bucle, solo play
            musicPlayer.audio.play().catch(function() {
                updateInfo('▶️ Click ▶ para continuar', '#ffaa00');
            });
        }
    }, 8000);
}

// ═══ FUNCIÓN PRINCIPAL DE CARGA ═══
function loadMusicFiles() {
    var status = document.getElementById('music-status');
    var playlistDiv = document.getElementById('music-playlist');

    if (musicPlayer.isLoading) return;
    musicPlayer.isLoading = true;

    updateStatus('⏳ Cargando canciones...', '#ffaa00');

    if (playlistDiv) {
        playlistDiv.innerHTML = '<div style="color:#9370db;text-align:center;padding:30px;">' +
            '<div style="font-size:32px;margin-bottom:10px;">🎵</div>' +
            '<div style="font-size:13px;">Cargando tu música...</div></div>';
    }

    musicPlayer.playlist = DEMO_PLAYLIST.map(function(t) { return Object.assign({}, t); });

    fetch('/api/music/list')
        .then(function(r) { return r.ok ? r.json() : Promise.reject('Error'); })
        .then(function(data) {
            if (data.ok && data.files && data.files.length > 0) {
                var validFiles = data.files.filter(function(f) { return f.size > 50000; });
                if (validFiles.length > 0) {
                    var localFiles = validFiles.map(function(f) {
                        return {
                            name: f.name.replace(/\.[^.]+$/, ''),
                            artist: 'Local',
                            path: f.path,
                            url: f.url,
                            isDemo: false,
                            size: f.size,
                            cover: '📁'
                        };
                    });
                    musicPlayer.playlist = localFiles.concat(DEMO_PLAYLIST);
                    updateStatus('🎵 ' + localFiles.length + ' locales + ' + DEMO_PLAYLIST.length + ' demo', '#00cc66');
                } else {
                    updateStatus('⚠️ Solo modo demo', '#ffaa00');
                }
            } else {
                updateStatus('🎵 Modo Demo', '#ffaa00');
            }
            musicPlayer.isLoaded = true;
            musicPlayer.isLoading = false;
            updatePlaylistUI();
            if (musicPlayer.playlist.length > 0) selectTrack(0);
        })
        .catch(function(err) {
            console.error('❌ Error cargando música:', err);
            musicPlayer.isLoading = false;
            musicPlayer.playlist = DEMO_PLAYLIST.map(function(t) { return Object.assign({}, t); });
            musicPlayer.isLoaded = true;
            updatePlaylistUI();
            updateStatus('🎵 Modo Demo (sin conexión)', '#ffaa00');
            if (musicPlayer.playlist.length > 0) selectTrack(0);
        });
}

// ═══ FUNCIONES DE ESTADO Y UI ═══
function updateStatus(text, color) {
    var el = document.getElementById('music-status');
    if (el) { el.textContent = text; el.style.color = color || '#9370db'; }
}

function updateInfo(text, color) {
    var el = document.getElementById('music-info');
    if (el) { el.textContent = text; el.style.color = color || '#d8bfd8'; }
}

function updateProgress(percent) {
    var el = document.getElementById('music-progress');
    if (el) el.style.width = Math.min(percent, 100) + '%';
}

function updateTime(current, total) {
    var t = document.getElementById('music-time');
    var d = document.getElementById('music-duration');
    if (t) t.textContent = current || '0:00';
    if (d) d.textContent = total || '0:00';
}

function formatTime(seconds) {
    if (!seconds || isNaN(seconds) || seconds < 0) return '0:00';
    var m = Math.floor(seconds / 60);
    var s = Math.floor(seconds % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
}

// ═══ PLAYLIST UI ═══
function updatePlaylistUI() {
    var div = document.getElementById('music-playlist');
    if (!div) return;

    if (musicPlayer.playlist.length === 0) {
        div.innerHTML = '<div style="color:#9370db;text-align:center;padding:30px;">' +
            '<div style="font-size:32px;margin-bottom:10px;">🎵</div>' +
            '<div style="font-size:13px;">No hay canciones</div></div>';
        return;
    }

    var html = '';
    var cur = musicPlayer.currentTrack;

    for (var i = 0; i < musicPlayer.playlist.length; i++) {
        var track = musicPlayer.playlist[i];
        var active = i === cur;
        var playing = active && musicPlayer.isPlaying;
        var isDemo = track.isDemo || false;
        var bg = active ? 'rgba(106,13,173,0.3)' : 'transparent';
        var border = active ? '#da70d6' : 'transparent';
        var color = playing ? '#da70d6' : (active ? '#e6e6fa' : '#9370db');
        var icon = playing ? '▶️' : (active ? '⏸️' : '🎵');
        var cover = track.cover || (isDemo ? '🎵' : '📁');

        html += '<div class="playlist-item" data-index="' + i + '" ' +
            'style="padding:10px 14px;margin:4px 0;border-radius:8px;cursor:pointer;' +
            'display:flex;align-items:center;gap:12px;background:' + bg + ';' +
            'border-left:3px solid ' + border + ';transition:all 0.2s;" ' +
            'onclick="selectTrack(' + i + ')" ' +
            'onmouseover="this.style.background=\'rgba(75,0,130,0.25)\'" ' +
            'onmouseout="this.style.background=\'' + bg + '\'">' +
            '<span style="font-size:18px;width:30px;text-align:center;">' + cover + '</span>' +
            '<span style="flex:1;color:' + color + ';font-size:13px;overflow:hidden;' +
            'text-overflow:ellipsis;white-space:nowrap;">' + icon + ' ' + track.name + '</span>' +
            '<span style="font-size:11px;color:#6a0dad;">' + (track.artist || 'Local') + '</span></div>';
    }

    div.innerHTML = html;

    setTimeout(function() {
        var activeItem = div.querySelector('.playlist-item[data-index="' + cur + '"]');
        if (activeItem) activeItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }, 100);
}

// ═══ SELECCIONAR CANCIÓN ═══
function selectTrack(index) {
    if (index < 0 || index >= musicPlayer.playlist.length) return;

    // Pausar lo que sea que esté sonando
    musicPlayer.audio.pause();
    musicPlayer.isPlaying = false;
    musicPlayer.progress = 0;
    musicPlayer.duration = 0;

    musicPlayer.currentTrack = index;
    var track = musicPlayer.playlist[index];

    console.log('🎵 Seleccionando: ' + track.name);
    updateInfo('⏳ Cargando: ' + track.name + '...', '#ffaa00');
    updateProgress(0);
    updateTime('0:00', '0:00');

    // Cambiar src y cargar
    musicPlayer.audio.src = track.url;
    musicPlayer.audio.volume = musicPlayer.volume / 100;
    musicPlayer.audio.load();

    // Esperar a que esté listo y reproducir
    var onReady = function() {
        musicPlayer.audio.removeEventListener('canplay', onReady);
        musicPlayer.audio.removeEventListener('canplaythrough', onReady);
        autoPlay();
    };

    musicPlayer.audio.addEventListener('canplay', onReady);
    musicPlayer.audio.addEventListener('canplaythrough', onReady);

    updatePlaylistUI();
}

// ═══ AUTO-REPRODUCIR ═══
function autoPlay() {
    if (!musicPlayer.audio || !musicPlayer.audio.src) return;

    var intentos = 0;
    function intentar() {
        if (intentos >= 3) {
            updateInfo('▶️ Click ▶ para reproducir', '#ffaa00');
            return;
        }
        intentos++;
        musicPlayer.audio.play()
            .then(function() {
                console.log('▶️ Reproduciendo (intento ' + intentos + ')');
            })
            .catch(function(err) {
                console.log('⏸️ Intento ' + intentos + ' falló:', err.message);
                if (intentos < 3) setTimeout(intentar, 400);
                else updateInfo('▶️ Click ▶ para continuar', '#ffaa00');
            });
    }
    intentar();
}

// ═══ CONTROLES ═══
function musicPlay() {
    if (musicPlayer.playlist.length === 0) {
        loadMusicFiles();
        return;
    }
    if (!musicPlayer.audio.src || musicPlayer.audio.src === '' || musicPlayer.audio.src === window.location.href) {
        selectTrack(musicPlayer.currentTrack || 0);
        return;
    }
    if (musicPlayer.isPlaying) {
        musicPlayer.audio.pause();
    } else {
        musicPlayer.audio.play()
            .catch(function(err) {
                console.error('❌ Error:', err);
                updateInfo('❌ Error al reproducir', '#ff4444');
            });
    }
}

function musicPause() {
    if (musicPlayer.audio) {
        musicPlayer.audio.pause();
    }
}

function musicNext() {
    if (musicPlayer.playlist.length === 0) {
        loadMusicFiles();
        return;
    }
    // Si está reproduciendo y lleva menos de 3s, ir a la siguiente
    // Si no, simplemente ir a la siguiente
    goToNext();
}

function musicPrev() {
    if (musicPlayer.playlist.length === 0) return;
    // Si lleva más de 3 segundos, reiniciar la canción actual
    if (musicPlayer.audio && musicPlayer.audio.currentTime > 3) {
        musicPlayer.audio.currentTime = 0;
        return;
    }
    // Si no, ir a la anterior
    var prevIndex = (musicPlayer.currentTrack - 1 + musicPlayer.playlist.length) % musicPlayer.playlist.length;
    selectTrack(prevIndex);
}

function musicShuffle() {
    musicPlayer.shuffle = !musicPlayer.shuffle;
    var btn = document.querySelector('.btn-shuffle');
    if (btn) {
        btn.style.color = musicPlayer.shuffle ? '#da70d6' : '#9370db';
        btn.style.borderColor = musicPlayer.shuffle ? '#da70d6' : 'transparent';
    }
    updateInfo('🔀 Shuffle ' + (musicPlayer.shuffle ? 'ON' : 'OFF'), '#ffaa00');
    setTimeout(function() {
        var t = musicPlayer.playlist[musicPlayer.currentTrack];
        if (t) updateInfo((musicPlayer.isPlaying ? '▶️ ' : '⏸️ ') + t.name, musicPlayer.isPlaying ? '#da70d6' : '#9370db');
    }, 1000);
}

function musicRepeat() {
    musicPlayer.repeat = !musicPlayer.repeat;
    var btn = document.querySelector('.btn-repeat');
    if (btn) {
        btn.style.color = musicPlayer.repeat ? '#da70d6' : '#9370db';
        btn.style.borderColor = musicPlayer.repeat ? '#da70d6' : 'transparent';
    }
    updateInfo('🔁 Repeat ' + (musicPlayer.repeat ? 'ON' : 'OFF'), '#ffaa00');
    setTimeout(function() {
        var t = musicPlayer.playlist[musicPlayer.currentTrack];
        if (t) updateInfo((musicPlayer.isPlaying ? '▶️ ' : '⏸️ ') + t.name, musicPlayer.isPlaying ? '#da70d6' : '#9370db');
    }, 1000);
}

function musicVolumeUp() {
    musicPlayer.volume = Math.min(100, musicPlayer.volume + 10);
    if (musicPlayer.audio) musicPlayer.audio.volume = musicPlayer.volume / 100;
    updateVolumeUI();
}

function musicVolumeDown() {
    musicPlayer.volume = Math.max(0, musicPlayer.volume - 10);
    if (musicPlayer.audio) musicPlayer.audio.volume = musicPlayer.volume / 100;
    updateVolumeUI();
}

function updateVolumeUI() {
    updateInfo('🔊 Volumen: ' + musicPlayer.volume + '%', '#ffaa00');
    var volBar = document.querySelector('.volume-bar');
    if (volBar) volBar.style.width = musicPlayer.volume + '%';
    setTimeout(function() {
        var t = musicPlayer.playlist[musicPlayer.currentTrack];
        if (t) updateInfo((musicPlayer.isPlaying ? '▶️ ' : '⏸️ ') + t.name, musicPlayer.isPlaying ? '#da70d6' : '#9370db');
    }, 1200);
}

// ═══ PROGRESO CLICKEABLE ═══
function seekTo(e) {
    if (!musicPlayer.audio || !musicPlayer.duration) return;
    var rect = e.currentTarget.getBoundingClientRect();
    var clientX = e.clientX || (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
    var x = clientX - rect.left;
    var pct = Math.max(0, Math.min(1, x / rect.width));
    musicPlayer.audio.currentTime = pct * musicPlayer.duration;
    updateProgress(pct * 100);
    updateTime(formatTime(musicPlayer.audio.currentTime), formatTime(musicPlayer.duration));
}

// ═══ INICIALIZAR ═══
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 Inicializando reproductor v2.2...');

    var win = document.getElementById('win-music');
    if (win) {
        var observer = new MutationObserver(function() {
            if (win.style.display !== 'none' && !musicPlayer.isLoaded && !musicPlayer.isLoading) {
                console.log('📂 Ventana abierta, cargando música...');
                loadMusicFiles();
            }
        });
        observer.observe(win, { attributes: true, attributeFilter: ['style'] });

        setTimeout(function() {
            if (win.style.display !== 'none' && !musicPlayer.isLoaded && !musicPlayer.isLoading) {
                loadMusicFiles();
            }
        }, 500);
    }

    var progressContainer = document.querySelector('.progress-container');
    if (progressContainer) {
        progressContainer.addEventListener('click', seekTo);
        progressContainer.addEventListener('touchstart', seekTo);
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
window.seekTo = seekTo;

console.log('🎵 Reproductor v2.2 cargado');
console.log('📌 Auto-next, Shuffle, Repeat, controles corregidos');
