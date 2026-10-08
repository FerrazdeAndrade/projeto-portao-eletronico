let audioContext;
let intervaloBipe;
let intervaloLED;

// Executa automaticamente assim que a página é carregada
document.addEventListener('DOMContentLoaded', () => {
    console.log("Sistema do Portão Automático inicializado no Frontend!");
    atualizarStatusBD();
});

// Procura a contagem de acionamentos no banco de dados via API
function atualizarStatusBD() {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            const contador = document.getElementById('contador');
            if (contador && data.total_acionamentos !== undefined) {
                contador.textContent = data.total_acionamentos;
            }
        })
        .catch(err => console.error('Erro ao conectar à API Flask:', err));
}

// Emissão de som via Web Audio API do navegador
function tocarBipe(frequencia = 1000, duracaoMs = 150) {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }

    const osc = audioContext.createOscillator();
    const gain = audioContext.createGain();

    osc.type = 'sine';
    osc.frequency.value = frequencia;
    gain.gain.setValueAtTime(0.1, audioContext.currentTime);

    osc.connect(gain);
    gain.connect(audioContext.destination);

    osc.start();
    setTimeout(() => osc.stop(), duracaoMs);
}

function iniciarSinalSonoro(tempoTotalMs = 3000) {
    clearInterval(intervaloBipe);
    tocarBipe(1000, 150);

    intervaloBipe = setInterval(() => {
        tocarBipe(1000, 150);
    }, 400);

    setTimeout(() => {
        clearInterval(intervaloBipe);
    }, tempoTotalMs);
}

// Sinalização visual no LED do topo da garagem
function piscarLED(corHex, tempoTotalMs = 3000) {
    const luzStatus = document.getElementById('luzStatus');
    if (!luzStatus) return;

    clearInterval(intervaloLED);
    luzStatus.style.backgroundColor = corHex;
    luzStatus.style.boxShadow = `0 0 12px ${corHex}`;

    let visivel = true;
    intervaloLED = setInterval(() => {
        visivel = !visivel;
        luzStatus.style.opacity = visivel ? '1' : '0.2';
    }, 250);

    setTimeout(() => {
        clearInterval(intervaloLED);
        luzStatus.style.opacity = '1';
        luzStatus.style.backgroundColor = corHex;
    }, tempoTotalMs);
}

// FUNÇÃO ACIONADA PELOS BOTÕES DO HTML
function enviarComando(acao) {
    console.log("Comando enviado:", acao);

    const portao = document.getElementById('portao');
    const estadoTexto = document.getElementById('estado');
    const btnAbrir = document.getElementById('btnAbrir');
    const btnFechar = document.getElementById('btnFechar');
    const contadorBD = document.getElementById('contador');
    const ledControle = document.getElementById('ledControle');

    // Desativa os botões para evitar cliques duplos durante a animação
    btnAbrir.disabled = true;
    btnFechar.disabled = true;

    // Pisca indicador visual do controle remoto
    if (ledControle) {
        ledControle.style.backgroundColor = '#2ecc71';
        setTimeout(() => { ledControle.style.backgroundColor = '#7f8c8d'; }, 300);
    }

    // Comunicação POST com a API Flask do Backend
    fetch(`/api/portao/${acao}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            console.log("Resposta do servidor:", data);
            if (data.status === 'sucesso' && contadorBD) {
                // Atualiza o contador na tela com o valor real do BD
                contadorBD.textContent = data.total_acionamentos;
            }
        })
        .catch(err => console.error('Erro de comunicação com o backend:', err));

    if (acao === 'abrir') {
        iniciarSinalSonoro(3000);
        piscarLED('#2ecc71', 3000); // Pisca LED Verde

        portao.classList.remove('fechado');
        portao.classList.add('aberto');
        estadoTexto.textContent = 'ABRINDO...';
        estadoTexto.style.color = '#2ecc71';

        setTimeout(() => {
            estadoTexto.textContent = 'ABERTO';
            btnFechar.disabled = false; // Liberta o botão FECHAR
        }, 3000);

    } else if (acao === 'fechar') {
        iniciarSinalSonoro(3000);
        piscarLED('#e74c3c', 3000); // Pisca LED Vermelho

        portao.classList.remove('aberto');
        portao.classList.add('fechado');
        estadoTexto.textContent = 'FECHANDO...';
        estadoTexto.style.color = '#e74c3c';

        setTimeout(() => {
            estadoTexto.textContent = 'FECHADO';
            btnAbrir.disabled = false; // Liberta o botão ABRIR
        }, 3000);
    }
}