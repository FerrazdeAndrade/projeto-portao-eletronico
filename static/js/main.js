// URL base apontando para o servidor Flask
const API_URL = "http://127.0.0.1:5000";

let audioCtx;
let intervaloBipe;
let intervaloPisca;

document.addEventListener('DOMContentLoaded', () => {
    fetch(`${API_URL}/api/status`)
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const contador = document.getElementById('contador');
            if (contador && data.total_acionamentos !== undefined) {
                contador.textContent = data.total_acionamentos;
            }
        })
        .catch(err => console.error('Erro ao buscar status do BD:', err));
});

function emitirBipe(frequencia = 1000, duracaoMs = 150) {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'sine';
    oscillator.frequency.value = frequencia;
    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    setTimeout(() => {
        oscillator.stop();
    }, duracaoMs);
}

function iniciarBipesContinuos(tempoTotalMs = 3000) {
    clearInterval(intervaloBipe);
    emitirBipe(1000, 150);

    intervaloBipe = setInterval(() => {
        emitirBipe(1000, 150);
    }, 400);

    setTimeout(() => {
        clearInterval(intervaloBipe);
    }, tempoTotalMs);
}

function piscarLuzStatus(cor, tempoTotalMs = 3000) {
    const luzStatus = document.getElementById('luzStatus');
    if (!luzStatus) return;

    clearInterval(intervaloPisca);
    luzStatus.style.backgroundColor = cor;

    let visivel = true;
    intervaloPisca = setInterval(() => {
        visivel = !visivel;
        luzStatus.style.opacity = visivel ? '1' : '0.2';
    }, 250);

    setTimeout(() => {
        clearInterval(intervaloPisca);
        luzStatus.style.opacity = '1';
        luzStatus.style.backgroundColor = cor;
    }, tempoTotalMs);
}

function enviarComando(acao) {
    const portao = document.getElementById('portao');
    const estado = document.getElementById('estado');
    const btnAbrir = document.getElementById('btnAbrir');
    const btnFechar = document.getElementById('btnFechar');
    const contador = document.getElementById('contador');

    btnAbrir.disabled = true;
    btnFechar.disabled = true;

    // Requisição HTTP enviando diretamente para o servidor Python
    fetch(`${API_URL}/api/portao/${acao}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.status === 'sucesso' && contador) {
                contador.textContent = data.total_acionamentos;
            }
        })
        .catch(err => {
            console.error('Erro na comunicação com o servidor:', err);
        });

    if (acao === 'abrir') {
        iniciarBipesContinuos(3000);
        piscarLuzStatus('#2ecc71', 3000);

        portao.classList.remove('fechado');
        portao.classList.add('aberto');
        estado.textContent = 'ABRINDO...';
        estado.style.color = '#2ecc71';

        setTimeout(() => {
            estado.textContent = 'ABERTO';
            estado.style.color = '#2ecc71';
            btnFechar.disabled = false;
        }, 3000);

    } else if (acao === 'fechar') {
        iniciarBipesContinuos(3000);
        piscarLuzStatus('#e74c3c', 3000);

        portao.classList.remove('aberto');
        portao.classList.add('fechado');
        estado.textContent = 'FECHANDO...';
        estado.style.color = '#e74c3c';

        setTimeout(() => {
            estado.textContent = 'FECHADO';
            estado.style.color = '#e74c3c';
            btnAbrir.disabled = false;
        }, 3000);
    }
}