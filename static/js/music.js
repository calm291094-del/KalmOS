// KALM OS v4.3 - Reproductor de Música

let musicPlayer = {
    isPlaying: false,
    currentTrack: 0,
    playlist: [],
    volume: 70,
    progress: 0,
    duration: 0
};

function musicPlay() {
    const info = document.getElementById('music-info');
    const progress = document.getElementById('music-progress');
    const time = document.getElementById('music-time');
    const duration = document.getElementById('music-duration');
    
    if (!info) return;
    
    if (musicPlayer.playlist.length === 0) {
        // Simular playlist
        musicPlayer.playlist = [
            '🎵 Canción 1 - Artista A',
            '🎵 Canción 2 - Artista B',
            '🎵 Canción 3 - Artista C',
            '🎵 Canción 4 - Artista D'
        ];
        document.getElementById('music-playlist').innerHTML = 
            musicPlayer.playlist.map((t, i) => 
                `<div style="padding:2px 5px;${i === musicPlayer.currentTrack ? 'color:#da70d6;font-weight:bold' : 'color:#9370db'}">
                    ${i === musicPlayer.currentTrack ? '▶️ ' : ''}${t}
                </div>`
            ).join('');
    }
    
    musicPlayer.isPlaying = true;
    const track = musicPlayer.playlist[musicPlayer.currentTrack] || '🎵 Sin título';
    info.textContent = `▶️ Reproduciendo: ${track}`;
    
    // Simular progreso
    musicPlayer.duration = 180 + Math.random() * 120;
    let currentTime = 0;
    
    if (musicPlayer.progressInterval) {
        clearInterval(musicPlayer.progressInterval);
    }
    
    musicPlayer.progressInterval = setInterval(() => {
        if (musicPlayer.isPlaying) {
            currentTime += 1;
            const pct = Math.min((currentTime / musicPlayer.duration) * 100, 100);
            if (progress) progress.style.width = pct + '%';
            if (time) {
                const mins = Math.floor(currentTime / 60);
                const secs = Math.floor(currentTime % 60);
                time.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
            }
            if (duration) {
                const mins = Math.floor(musicPlayer.duration / 60);
                const secs = Math.floor(musicPlayer.duration % 60);
                duration.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
            }
            
            if (currentTime >= musicPlayer.duration) {
                musicNext();
            }
        }
    }, 1000);
}

function musicPause() {
    const info = document.getElementById('music-info');
    if (!info) return;
    
    musicPlayer.isPlaying = !musicPlayer.isPlaying;
    info.textContent = musicPlayer.isPlaying ? 
        `▶️ Reproduciendo: ${musicPlayer.playlist[musicPlayer.currentTrack] || '🎵'}` : 
        '⏸️ Pausado';
}

function musicNext() {
    const info = document.getElementById('music-info');
    const progress = document.getElementById('music-progress');
    const time = document.getElementById('music-time');
    
    if (!info) return;
    
    if (musicPlayer.playlist.length === 0) {
        musicPlay();
        return;
    }
    
    musicPlayer.currentTrack = (musicPlayer.currentTrack + 1) % musicPlayer.playlist.length;
    if (progress) progress.style.width = '0%';
    if (time) time.textContent = '0:00';
    musicPlayer.isPlaying = true;
    info.textContent = `⏭️ Siguiente: ${musicPlayer.playlist[musicPlayer.currentTrack]}`;
    
    // Actualizar playlist visual
    const playlistDiv = document.getElementById('music-playlist');
    if (playlistDiv) {
        playlistDiv.innerHTML = musicPlayer.playlist.map((t, i) => 
            `<div style="padding:2px 5px;${i === musicPlayer.currentTrack ? 'color:#da70d6;font-weight:bold' : 'color:#9370db'};cursor:pointer" onclick="musicJumpTo(${i})">
                ${i === musicPlayer.currentTrack ? '▶️ ' : '📄 '}${t}
            </div>`
        ).join('');
    }
    
    // Reiniciar progreso
    if (musicPlayer.progressInterval) {
        clearInterval(musicPlayer.progressInterval);
        musicPlayer.progressInterval = null;
    }
    setTimeout(musicPlay, 500);
}

function musicPrev() {
    const info = document.getElementById('music-info');
    const progress = document.getElementById('music-progress');
    const time = document.getElementById('music-time');
    
    if (!info) return;
    
    if (musicPlayer.playlist.length === 0) {
        musicPlay();
        return;
    }
    
    musicPlayer.currentTrack = (musicPlayer.currentTrack - 1 + musicPlayer.playlist.length) % musicPlayer.playlist.length;
    if (progress) progress.style.width = '0%';
    if (time) time.textContent = '0:00';
    musicPlayer.isPlaying = true;
    info.textContent = `⏮️ Anterior: ${musicPlayer.playlist[musicPlayer.currentTrack]}`;
    
    // Actualizar playlist visual
    const playlistDiv = document.getElementById('music-playlist');
    if (playlistDiv) {
        playlistDiv.innerHTML = musicPlayer.playlist.map((t, i) => 
            `<div style="padding:2px 5px;${i === musicPlayer.currentTrack ? 'color:#da70d6;font-weight:bold' : 'color:#9370db'};cursor:pointer" onclick="musicJumpTo(${i})">
                ${i === musicPlayer.currentTrack ? '▶️ ' : '📄 '}${t}
            </div>`
        ).join('');
    }
    
    if (musicPlayer.progressInterval) {
        clearInterval(musicPlayer.progressInterval);
        musicPlayer.progressInterval = null;
    }
    setTimeout(musicPlay, 500);
}

function musicJumpTo(index) {
    if (index >= 0 && index < musicPlayer.playlist.length) {
        musicPlayer.currentTrack = index;
        const info = document.getElementById('music-info');
        if (info) info.textContent = `▶️ Reproduciendo: ${musicPlayer.playlist[index]}`;
        if (musicPlayer.progressInterval) {
            clearInterval(musicPlayer.progressInterval);
            musicPlayer.progressInterval = null;
        }
        setTimeout(musicPlay, 300);
    }
}

function musicVolumeUp() {
    musicPlayer.volume = Math.min(100, musicPlayer.volume + 10);
    document.getElementById('music-info').textContent = `🔊 Volumen: ${musicPlayer.volume}%`;
    setTimeout(() => {
        if (musicPlayer.isPlaying) {
            document.getElementById('music-info').textContent = `▶️ Reproduciendo: ${musicPlayer.playlist[musicPlayer.currentTrack] || '🎵'}`;
        }
    }, 1500);
}

function musicVolumeDown() {
    musicPlayer.volume = Math.max(0, musicPlayer.volume - 10);
    document.getElementById('music-info').textContent = `🔉 Volumen: ${musicPlayer.volume}%`;
    setTimeout(() => {
        if (musicPlayer.isPlaying) {
            document.getElementById('music-info').textContent = `▶️ Reproduciendo: ${musicPlayer.playlist[musicPlayer.currentTrack] || '🎵'}`;
        }
    }, 1500);
}

function musicAddTrack() {
    const track = prompt('Nombre de la canción (Ej: "Artista - Canción"):');
    if (track && track.trim()) {
        musicPlayer.playlist.push(track.trim());
        const playlistDiv = document.getElementById('music-playlist');
        if (playlistDiv) {
            playlistDiv.innerHTML = musicPlayer.playlist.map((t, i) => 
                `<div style="padding:2px 5px;${i === musicPlayer.currentTrack ? 'color:#da70d6;font-weight:bold' : 'color:#9370db'};cursor:pointer" onclick="musicJumpTo(${i})">
                    ${i === musicPlayer.currentTrack ? '▶️ ' : '📄 '}${t}
                </div>`
            ).join('');
        }
        document.getElementById('music-info').textContent = `✅ Añadido: ${track.trim()}`;
        setTimeout(() => {
            if (musicPlayer.isPlaying) {
                document.getElementById('music-info').textContent = `▶️ Reproduciendo: ${musicPlayer.playlist[musicPlayer.currentTrack] || '🎵'}`;
            } else {
                document.getElementById('music-info').textContent = '🎵 Listo';
            }
        }, 1500);
    }
}

function musicClearPlaylist() {
    if (!confirm('¿Borrar toda la playlist?')) return;
    musicPlayer.playlist = [];
    musicPlayer.currentTrack = 0;
    musicPlayer.isPlaying = false;
    if (musicPlayer.progressInterval) {
        clearInterval(musicPlayer.progressInterval);
        musicPlayer.progressInterval = null;
    }
    document.getElementById('music-playlist').innerHTML = '📋 Playlist vacía';
    document.getElementById('music-info').textContent = '🗑️ Playlist borrada';
    document.getElementById('music-progress').style.width = '0%';
    document.getElementById('music-time').textContent = '0:00';
    document.getElementById('music-duration').textContent = '0:00';
}