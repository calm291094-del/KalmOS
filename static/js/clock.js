// KALM OS v4.3 - Reloj Mundial

let clockInterval = null;
let clockFormat = '24h';

function updateWorldClocks() {
    const now = new Date();
    
    // Hora local
    const localDisplay = document.getElementById('clock-display');
    if (localDisplay) {
        localDisplay.textContent = now.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    // Ciudades del mundo
    const cities = {
        'clock-london': { offset: 0, name: 'Londres' },
        'clock-ny': { offset: -4, name: 'Nueva York' },
        'clock-tokyo': { offset: 9, name: 'Tokio' },
        'clock-sydney': { offset: 10, name: 'Sídney' },
        'clock-paris': { offset: 2, name: 'París' },
        'clock-dubai': { offset: 4, name: 'Dubái' },
        'clock-moscow': { offset: 3, name: 'Moscú' },
        'clock-la': { offset: -7, name: 'Los Ángeles' }
    };
    
    for (const [id, city] of Object.entries(cities)) {
        const el = document.getElementById(id);
        if (el) {
            const cityTime = new Date(now.getTime() + (now.getTimezoneOffset() + city.offset * 60) * 60000);
            el.textContent = cityTime.toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
}

function toggleClockFormat() {
    clockFormat = clockFormat === '24h' ? '12h' : '24h';
    const btn = document.getElementById('clock-format-btn');
    if (btn) btn.textContent = clockFormat === '24h' ? '24h' : '12h';
    updateWorldClocks();
}

function addCity() {
    const name = prompt('Nombre de la ciudad:');
    if (!name) return;
    const offset = prompt('Diferencia horaria (ej: -3, +2, 0):');
    if (offset === null) return;
    
    const numOffset = parseFloat(offset);
    if (isNaN(numOffset)) {
        alert('❌ Diferencia horaria inválida');
        return;
    }
    
    const container = document.getElementById('world-clocks');
    if (!container) return;
    
    const div = document.createElement('div');
    div.style.cssText = 'background:#1a0033;padding:8px;border-radius:5px;text-align:center;border:1px solid #4b0082';
    const id = 'clock-city-' + Date.now();
    div.innerHTML = `
        <div style="font-size:10px;color:#9370db">🌍 ${name}</div>
        <div style="font-size:16px;color:#fff" id="${id}">--:--</div>
    `;
    container.appendChild(div);
    
    // Guardar en localStorage
    const cities = JSON.parse(localStorage.getItem('kalm_cities') || '[]');
    cities.push({ name, offset: numOffset, id });
    localStorage.setItem('kalm_cities', JSON.stringify(cities));
}

// Cargar ciudades guardadas
function loadSavedCities() {
    const container = document.getElementById('world-clocks');
    if (!container) return;
    
    const cities = JSON.parse(localStorage.getItem('kalm_cities') || '[]');
    cities.forEach(city => {
        const div = document.createElement('div');
        div.style.cssText = 'background:#1a0033;padding:8px;border-radius:5px;text-align:center;border:1px solid #4b0082';
        div.innerHTML = `
            <div style="font-size:10px;color:#9370db">🌍 ${city.name}</div>
            <div style="font-size:16px;color:#fff" id="${city.id}">--:--</div>
        `;
        container.appendChild(div);
    });
}

// Iniciar reloj
document.addEventListener('DOMContentLoaded', function() {
    // Cargar ciudades guardadas antes de iniciar
    loadSavedCities();
    
    // Iniciar actualización
    updateWorldClocks();
    if (clockInterval) clearInterval(clockInterval);
    clockInterval = setInterval(updateWorldClocks, 1000);
});

// Limpiar intervalo al cerrar la ventana
window.addEventListener('beforeunload', function() {
    if (clockInterval) {
        clearInterval(clockInterval);
        clockInterval = null;
    }
});