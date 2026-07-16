// KALM OS v4.3 - Bloc de notas

let notepadFile = null;
let notepadModified = false;

function notepadSave() {
    const content = document.getElementById('notepad-content');
    const status = document.getElementById('notepad-status');
    if (!content || !status) return;
    
    if (notepadFile) {
        // Guardar en archivo real (simulado)
        localStorage.setItem('kalm_notepad_' + notepadFile, content.value);
        localStorage.setItem('kalm_notepad_current', notepadFile);
        status.textContent = '✅ Guardado en: ' + notepadFile;
        notepadModified = false;
    } else {
        // Guardar con nombre
        const name = prompt('Nombre del archivo:', 'nota.txt');
        if (name) {
            notepadFile = name;
            localStorage.setItem('kalm_notepad_' + name, content.value);
            localStorage.setItem('kalm_notepad_current', name);
            status.textContent = '✅ Guardado como: ' + name;
            notepadModified = false;
            document.querySelector('#win-notepad .title-bar span').textContent = '📝 ' + name;
        }
    }
    setTimeout(() => {
        if (status.textContent.includes('✅')) {
            status.textContent = '📝 Listo';
        }
    }, 3000);
}

function notepadLoad() {
    const content = document.getElementById('notepad-content');
    const status = document.getElementById('notepad-status');
    if (!content || !status) return;
    
    // Buscar archivos guardados
    const files = [];
    for (let key in localStorage) {
        if (key.startsWith('kalm_notepad_') && key !== 'kalm_notepad_current') {
            files.push(key.replace('kalm_notepad_', ''));
        }
    }
    
    if (files.length === 0) {
        status.textContent = '❌ No hay archivos guardados';
        setTimeout(() => status.textContent = '📝 Listo', 2000);
        return;
    }
    
    // Mostrar lista para elegir
    let options = files.map((f, i) => `${i+1}. ${f}`).join('\n');
    const choice = prompt('Archivos guardados:\n' + options + '\n\nElige número (o cancelar):');
    if (choice === null) return;
    
    const idx = parseInt(choice) - 1;
    if (idx >= 0 && idx < files.length) {
        const name = files[idx];
        const saved = localStorage.getItem('kalm_notepad_' + name);
        if (saved) {
            content.value = saved;
            notepadFile = name;
            notepadModified = false;
            status.textContent = '📂 Cargado: ' + name;
            document.querySelector('#win-notepad .title-bar span').textContent = '📝 ' + name;
        } else {
            status.textContent = '❌ Error cargando archivo';
        }
    }
    setTimeout(() => {
        if (status.textContent.includes('📂') || status.textContent.includes('❌')) {
            status.textContent = '📝 Listo';
        }
    }, 2000);
}

function notepadClear() {
    const content = document.getElementById('notepad-content');
    const status = document.getElementById('notepad-status');
    if (!content || !status) return;
    
    if (notepadModified && !confirm('¿Hay cambios sin guardar. ¿Borrar de todos modos?')) return;
    
    content.value = '';
    notepadFile = null;
    notepadModified = false;
    status.textContent = '🗑️ Limpiado';
    document.querySelector('#win-notepad .title-bar span').textContent = '📝 Bloc de notas';
    setTimeout(() => status.textContent = '📝 Listo', 2000);
}

function notepadNew() {
    const content = document.getElementById('notepad-content');
    const status = document.getElementById('notepad-status');
    if (!content || !status) return;
    
    if (notepadModified && !confirm('¿Hay cambios sin guardar. ¿Crear nuevo de todos modos?')) return;
    
    content.value = '';
    notepadFile = null;
    notepadModified = false;
    status.textContent = '📄 Nuevo documento';
    document.querySelector('#win-notepad .title-bar span').textContent = '📝 Bloc de notas';
    setTimeout(() => status.textContent = '📝 Listo', 2000);
}

function notepadFind() {
    const content = document.getElementById('notepad-content');
    if (!content) return;
    
    const search = prompt('Buscar:');
    if (!search) return;
    
    const text = content.value;
    const idx = text.indexOf(search);
    if (idx >= 0) {
        content.focus();
        content.setSelectionRange(idx, idx + search.length);
        alert('✅ Encontrado en la posición ' + (idx + 1));
    } else {
        alert('❌ No se encontró: "' + search + '"');
    }
}

// Detectar cambios en el contenido
document.addEventListener('DOMContentLoaded', function() {
    const content = document.getElementById('notepad-content');
    if (content) {
        content.addEventListener('input', function() {
            notepadModified = true;
            const status = document.getElementById('notepad-status');
            if (status) status.textContent = '✏️ Editando...';
        });
    }
    
    // Cargar último archivo editado
    const lastFile = localStorage.getItem('kalm_notepad_current');
    if (lastFile) {
        const saved = localStorage.getItem('kalm_notepad_' + lastFile);
        if (saved && document.getElementById('notepad-content')) {
            document.getElementById('notepad-content').value = saved;
            notepadFile = lastFile;
            document.querySelector('#win-notepad .title-bar span').textContent = '📝 ' + lastFile;
        }
    }
});

// Atajos de teclado
document.addEventListener('keydown', function(e) {
    const content = document.getElementById('notepad-content');
    if (!content || document.activeElement !== content) return;
    
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        notepadSave();
    }
    if (e.ctrlKey && e.key === 'o') {
        e.preventDefault();
        notepadLoad();
    }
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        notepadNew();
    }
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        notepadFind();
    }
});