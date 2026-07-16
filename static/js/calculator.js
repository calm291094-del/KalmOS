// KALM OS v4.3 - Calculadora

let calcDisplay = '';
let calcMemory = 0;
let calcOperator = '';
let calcNewNumber = true;

function calcInput(value) {
    const display = document.getElementById('calc-display');
    if (!display) return;
    
    if (value === 'C') {
        calcDisplay = '';
        calcOperator = '';
        calcNewNumber = true;
        display.value = '0';
        return;
    }
    
    if (value === '±') {
        if (calcDisplay.startsWith('-')) {
            calcDisplay = calcDisplay.substring(1);
        } else if (calcDisplay !== '0' && calcDisplay !== '') {
            calcDisplay = '-' + calcDisplay;
        }
        display.value = calcDisplay || '0';
        return;
    }
    
    if (value === 'sqrt') {
        try {
            const num = parseFloat(calcDisplay) || 0;
            if (num < 0) {
                display.value = 'Error';
                calcDisplay = '';
                return;
            }
            const result = Math.sqrt(num);
            calcDisplay = result.toString();
            display.value = calcDisplay;
            calcNewNumber = true;
        } catch(e) {
            display.value = 'Error';
            calcDisplay = '';
        }
        return;
    }
    
    if (value === '**') {
        calcDisplay += '**';
        display.value = calcDisplay;
        return;
    }
    
    if (['+', '-', '*', '/'].includes(value)) {
        if (!calcNewNumber && calcDisplay) {
            calcResult();
        }
        calcOperator = value;
        calcMemory = parseFloat(calcDisplay) || 0;
        calcNewNumber = true;
        display.value = calcDisplay + ' ' + value;
        return;
    }
    
    if (value === '=') {
        calcResult();
        return;
    }
    
    // Números y punto decimal
    if (calcNewNumber) {
        calcDisplay = (value === '.' ? '0.' : value);
        calcNewNumber = false;
    } else {
        if (value === '.' && calcDisplay.includes('.')) return;
        calcDisplay += value;
    }
    display.value = calcDisplay;
}

function calcResult() {
    const display = document.getElementById('calc-display');
    if (!display) return;
    
    if (!calcOperator) {
        display.value = calcDisplay || '0';
        return;
    }
    
    const current = parseFloat(calcDisplay) || 0;
    let result = 0;
    
    switch(calcOperator) {
        case '+': result = calcMemory + current; break;
        case '-': result = calcMemory - current; break;
        case '*': result = calcMemory * current; break;
        case '/': 
            if (current === 0) {
                display.value = 'Error';
                calcDisplay = '';
                calcOperator = '';
                return;
            }
            result = calcMemory / current; 
            break;
        default: result = current;
    }
    
    calcDisplay = result.toString();
    display.value = calcDisplay;
    calcOperator = '';
    calcNewNumber = true;
}

// Soporte para teclado
document.addEventListener('keydown', function(e) {
    const key = e.key;
    if (key >= '0' && key <= '9') {
        calcInput(key);
    } else if (key === '.') {
        calcInput('.');
    } else if (key === '+') {
        calcInput('+');
    } else if (key === '-') {
        calcInput('-');
    } else if (key === '*') {
        calcInput('*');
    } else if (key === '/') {
        calcInput('/');
    } else if (key === 'Enter' || key === '=') {
        calcResult();
    } else if (key === 'Escape' || key === 'c') {
        calcInput('C');
    } else if (key === 'Backspace') {
        const display = document.getElementById('calc-display');
        if (display && calcDisplay.length > 1) {
            calcDisplay = calcDisplay.slice(0, -1);
            display.value = calcDisplay;
        } else {
            calcInput('C');
        }
    }
});