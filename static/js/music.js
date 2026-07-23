// KALM OS v4.3 - Reproductor de Música v3.0
// ✅ Estado manejado por botones, no por eventos
// ✅ Eventos solo para cambios automáticos (auto-play, ended, error)
// ✅ Sin condición de carrera pause/play

var musicPlayer = {
    isPlaying: false,
    currentTrack: 0,
    playlist: [],
    volume: 70,
    duration: 0,
    audio: null,
    isLoaded: false,
    isLoading: false,
    shuffle: false,
    repeat: false,
    transitioning: false
};

var DEMO_PLAYLIST = [
    {
        name: 'Beethoven - Sonata No. 8 (Pathétique)',
        artist: 'Beethoven',
        url: 'https://upload.wikimedia.org/wikipedia/commons/5/5d/Beethoven_-_Sonata_No._8_%28Path%C3%A9tique%29_in_C_minor_Op._13%2C_2nd_movement.ogg',
        isDemo: true, cover: '🎵'
    },
    {
        name: 'Grieg - Peer Gynt Suite No. 1 (Morning)',
        artist: 'Grieg',
        url: 'https://upload.wikimedia.org/wikipedia/commons/6/6c/Grieg_-_Peer_Gynt_Suite_No._1_%28movement_1%29.ogg',
        isDemo: true, cover: '🎶'
    },
    {
        name: 'Bach - Brandenburg Concerto No. 1',
        artist: 'Bach',
        url: 'https://upload.wikimedia.org/wikipedia/commons/9/98/Bach_-_Brandenburg_Concerto_No._1_in_F_Major_BWV_1046_%281st_movement%29.ogg',
        isDemo: true, cover: '🎻'
    }
];

// ═══ CREAR AUDIO UNA SOLA VEZ ═══
musicPlayer.audio = new Audio();
musicPlayer.audio.preload = 'auto';

function getTrack() {
    return musicPlayer.playlist[musicPlayer.currentTrack] || null;
}

function formatTime(s) {
    if (!s || isNaN(s) || s < 0) return '0:00';
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
}

// ═══════════════════════════════════════════════════════════
// EVENTOS DEL AUDIO — SOLO para cambios AUTOMÁTICOS
// El estado de play/pause lo manejan los botones directamente.
// Estos eventos solo reaccionan a: auto-play, ended, error.
// ═══════════════════════════════════════════════════════════

musicPlayer.audio.addEventListener('loadedmetadata', function() {
    musicPlayer.duration = this.duration;
    var t = getTrack();
    if (t && !musicPlayer.transitioning) {
        updateInfo('⏸️ ' + t.name + ' (' + formatTime(this.duration) + ')', '#d8bfd8');
    }
    updateTime(formatTime(0), formatTime(this.duration));
    updateProgress(0);
});

musicPlayer.audio.addEventListener('timeupdate', function() {
    if (this.duration > 0 && !isNaN(this.duration)) {
        var pct = (this.currentTime / this.duration) * 100;
        updateProgress(pct);
        updateTime(formatTime(this.currentTime), formatTime(this.duration));
    }
});

// Este SOLO se ejecuta durante transiciones (auto-play de siguiente canción)
musicPlayer.audio.addEventListener('play', function() {
    if (musicPlayer.transitioning) {
        console.log('🎵 Evento play (auto)');
        musicPlayer.isPlaying = true;
        musicPlayer.transitioning = false;
        var t = getTrack();
        if (t) updateInfo('▶️ ' + t.name, '#da70d6');
        updatePlaylistUI();
    }
    // Si NO es transición, el botón ya actualizó el estado. No hacemos nada.
});

// Este se ignora SIEMPRE durante transiciones
musicPlayer.audio.addEventListener('pause', function() {
    if (musicPlayer.transitioning) {
        console.log('🎵 Evento pause IGNORADO (transición)');
        return;
    }
    // Si no es transición, el botón ya actualizó el estado. No hacemos nada.
    console.log('🎵 Evento pause (externo)');
});

musicPlayer.audio.addEventListener('ended', function() {
    console.log('🎵 Evento ended');
    if (musicPlayer.repeat) {
        console.log('🔁 Repeat → reiniciando');
        this.currentTime = 0;
        this.play().catch(function() {});
        return;
    }
    goToNext();
});

musicPlayer.audio.addEventListener('error', function() {
    var t = getTrack();
    console.error('❌ Error de audio:', t ? t.name : '');
    musicPlayer.transitioning = false;
    musicPlayer.isPlaying = false;
    if (t) updateInfo('❌ Error: ' + t.name, '#ff4444');
    updatePlaylistUI();
    setTimeout(function() {
        if (t && t.isDemo) selectTrack(musicPlayer.currentTrack);
        else goToNext();
    }, 2000);
});

// Auto-play cuando canplay se dispara durante una transición
musicPlayer.audio.addEventListener('canplay', function() {
    if (musicPlayer.transitioning) {
        console.log('🎵 canplay → auto-play');
        this.play().then(function() {
            console.log('✅ Auto-play OK');
        }).catch(function(err) {
            console.log('⏸️ Auto-play bloqueado:', err.message);
            musicPlayer.transitioning = false;
            musicPlayer.isPlaying = false;
            updateInfo('▶️ Click ▶ para continuar', '#ffaa00');
            updatePlaylistUI();
        });
    }
});

// ═══════════════════════════════════════════════════════════
// IR A SIGUIENTE — usado por ended y por botón
// ═══════════════════════════════════════════════════════════

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

    // Activar transición ANTES de cambiar src
    musicPlayer.transitioning = true;
    musicPlayer.isPlaying = false;
    musicPlayer.currentTrack = nextIndex;

    updateInfo('⏳ Cargando...', '#ffaa00');
    updateProgress(0);
    updateTime('0:00', '0:00');

    // Cambiar src SIN llamar pause() — evita evento pause extra
    musicPlayer.audio.src = nextTrack.url;
    musicPlayer.audio.load();
    updatePlaylistUI();

    // Seguridad: si en 10s no reproduce, desactivar transición
    setTimeout(function() {
        if (musicPlayer.transitioning && musicPlayer.currentTrack === nextIndex) {
            console.log('⚠️ Timeout goToNext');
            musicPlayer.transitioning = false;
            musicPlayer.isPlaying = false;
            updateInfo('▶️ Click ▶ para continuar', '#ffaa00');
            updatePlaylistUI();
        }
    }, 10000);
}

// ═══════════════════════════════════════════════════════════
// SELECCIONAR CANCIÓN — usado por click en playlist
// ═══════════════════════════════════════════════════════════

function selectTrack(index) {
    if (index < 0 || index >= musicPlayer.playlist.length) return;

    var track = musicPlayer.playlist[index];
    console.log('🎵 Seleccionando: ' + track.name);

    // Activar transición
    musicPlayer.transitioning = true;
    musicPlayer.isPlaying = false;
    musicPlayer.currentTrack = index;

    updateInfo('⏳ Cargando: ' + track.name + '...', '#ffaa00');
    updateProgress(0);
    updateTime('0:00', '0:00');

    // Cambiar src SIN llamar pause()
    musicPlayer.audio.src = track.url;
    musicPlayer.audio.volume = musicPlayer.volume / 100;
    musicPlayer.audio.load();
    updatePlaylistUI();

    // Seguridad
    setTimeout(function() {
        if (musicPlayer.transitioning && musicPlayer.currentTrack === index) {
            console.log('⚠️ Timeout selectTrack');
            musicPlayer.transitioning = false;
            musicPlayer.isPlaying = false;
            updateInfo('▶️ Click ▶ para continuar', '#ffaa00');
            updatePlaylistUI();
        }
    }, 10000);
}

// ═══════════════════════════════════════════════════════════
// CONTROLES DE USUARIO — gestionan estado DIRECTAMENTE
// No dependen de eventos play/pause
// ═══════════════════════════════════════════════════════════

function musicPlay() {
    console.log('🎵 musicPlay() — isPlaying=' + musicPlayer.isPlaying + ' transitioning=' + musicPlayer.transitioning);

    // Si está en transición, ignorar
    if (musicPlayer.transitioning) return;

    // Si no hay canción cargada, cargar la primera
    if (!musicPlayer.audio.src || musicPlayer.audio.src === '' || musicPlayer.audio.src === location.href) {
        if (musicPlayer.playlist.length > 0) {
            selectTrack(musicPlayer.currentTrack || 0);
        } else {
            loadMusicFiles();
        }
        return;
    }

    var t = getTrack();

    if (musicPlayer.isPlaying) {
        // ═══ ESTÁ REPRODUCIENDO → PAUSAR ═══
        musicPlayer.isPlaying = false;
        musicPlayer.audio.pause();
        if (t) updateInfo('⏸️ ' + t.name, '#9370db');
        updatePlaylistUI();
        console.log('⏸️ Pausado por botón Play');
    } else {
        // ═══ ESTÁ PAUSADO → REPRODUCIR ═══
        musicPlayer.isPlaying = true;
        musicPlayer.audio.play().catch(function(err) {
            console.error('❌ Error al reproducir:', err);
            musicPlayer.isPlaying = false;
            if (t) updateInfo('❌ Error al reproducir', '#ff4444');
            updatePlaylistUI();
        });
        if (t) updateInfo('▶️ ' + t.name, '#da70d6');
        updatePlaylistUI();
        console.log('▶️ Reproduciendo por botón Play');
    }
}

function musicPause() {
    console.log('🎵 musicPause() — isPlaying=' + musicPlayer.isPlaying + ' transitioning=' + musicPlayer.transitioning);

    // Si está en transición, ignorar
    if (musicPlayer.transitioning) return;

    // Si ya está pausado, no hacer nada
    if (!musicPlayer.isPlaying) return;

    // ═══ PAUSAR ═══
    musicPlayer.isPlaying = false;
    musicPlayer.audio.pause();
    var t = getTrack();
    if (t) updateInfo('⏸️ ' + t.name, '#9370db');
    updatePlaylistUI();
    console.log('⏸️ Pausado por botón Pausa');
}

function musicNext() {
    console.log('🎵 musicNext()');
    if (musicPlayer.playlist.length === 0) {
        loadMusicFiles();
        return;
    }
    goToNext();
}

function musicPrev() {
    console.log('🎵 musicPrev()');
    if (musicPlayer.playlist.length === 0) return;

    // Si lleva más de 3 segundos, reiniciar la canción actual
    if (musicPlayer.audio && musicPlayer.audio.currentTime > 3) {
        musicPlayer.audio.currentTime = 0;
        return;
    }

    // Ir a la anterior
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
    flashInfo('🔀 Shuffle ' + (musicPlayer.shuffle ? 'ON' : 'OFF'));
}

function musicRepeat() {
    musicPlayer.repeat = !musicPlayer.repeat;
    var btn = document.querySelector('.btn-repeat');
    if (btn) {
        btn.style.color = musicPlayer.repeat ? '#da70d6' : '#9370db';
        btn.style.borderColor = musicPlayer.repeat ? '#da70d6' : 'transparent';
    }
    flashInfo('🔁 Repeat ' + (musicPlayer.repeat ? 'ON' : 'OFF'));
}

function musicVolumeUp() {
    musicPlayer.volume = Math.min(100, musicPlayer.volume + 10);
    if (musicPlayer.audio) musicPlayer.audio.volume = musicPlayer.volume / 100;
    flashInfo('🔊 Volumen: ' + musicPlayer.volume + '%');
    var volBar = document.querySelector('.volume-bar');
    if (volBar) volBar.style.width = musicPlayer.volume + '%';
}

function musicVolumeDown() {
    musicPlayer.volume = Math.max(0, musicPlayer.volume - 10);
    if (musicPlayer.audio) musicPlayer.audio.volume = musicPlayer.volume / 100;
    flashInfo('🔊 Volumen: ' + musicPlayer.volume + '%');
    var volBar = document.querySelector('.volume-bar');
    if (volBar) volBar.style.width = musicPlayer.volume + '%';
}

function flashInfo(text) {
    updateInfo(text, '#ffaa00');
    setTimeout(function() {
        var t = getTrack();
        if (t) {
            updateInfo((musicPlayer.isPlaying ? '▶️ ' : '⏸️ ') + t.name, musicPlayer.isPlaying ? '#da70d6' : '#9370db');
        }
    }, 1200);
}

// ═══════════════════════════════════════════════════════════
// CARGA DE ARCHIVOS
// ═══════════════════════════════════════════════════════════

function loadMusicFiles() {
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
                var valid = data.files.filter(function(f) { return f.size > 50000; });
                if (valid.length > 0) {
                    var local = valid.map(function(f) {
                        return {
                            name: f.name.replace(/\.[^.]+$/, ''),
                            artist: 'Local', path: f.path, url: f.url,
                            isDemo: false, size: f.size, cover: '📁'
                        };
                    });
                    musicPlayer.playlist = local.concat(DEMO_PLAYLIST);
                    updateStatus('🎵 ' + local.length + ' locales + ' + DEMO_PLAYLIST.length + ' demo', '#00cc66');
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

// ═══════════════════════════════════════════════════════════
// FUNCIONES DE UI
// ═══════════════════════════════════════════════════════════

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
        var bg = active ? 'rgba(106,13,173,0.3)' : 'transparent';
        var border = active ? '#da70d6' : 'transparent';
        var color = playing ? '#da70d6' : (active ? '#e6e6fa' : '#9370db');
        var icon = playing ? '▶️' : (active ? '⏸️' : '🎵');
        var cover = track.cover || '📁';

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
        var item = div.querySelector('.playlist-item[data-index="' + cur + '"]');
        if (item) item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }, 100);
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
    console.log('🎵 Inicializando reproductor v3.0...');

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

    var pc = document.querySelector('.progress-container');
    if (pc) {
        pc.addEventListener('click', seekTo);
        pc.addEventListener('touchstart', seekTo);
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

console.log('🎵 Reproductor v3.0 cargado — Estado gestionado por botones');
