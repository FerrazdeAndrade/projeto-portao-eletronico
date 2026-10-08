#include <Servo.h>
#include <IRremote.h>

// --- PINAGEM DO HARDWARE ---
const int RECV_PIN     = 2;   // Pino do Receptor IR (Sensor Infravermelho)
const int LED_VERMELHO = 4;   // LED Indicador de Portão Fechado/Fechando
const int LED_VERDE    = 5;   // LED Indicador de Portão Aberto/Abrindo
const int SERVO_PIN    = 9;   // Pino de sinal PWM do Servomotor SG90
const int PIEZO_BUZZER = 10;  // Pino do Buzzer Passivo/Ativo

// --- OBJETOS E VARIÁVEIS DE ESTADO ---
Servo meuServo;

// Código HEX do botão do seu controle remoto IR (exemplo padrão: 0x44)
const uint16_t COMANDO_BOTAO = 0x44; 

// Estado atual do portão: 0 = Fechado | 1 = Aberto
int estadoPortao = 0; 

void setup() {
  // Inicializa a porta serial a 9600 bps para comunicação com o Flask (app.py)
  Serial.begin(9600);

  // Configuração dos pinos de saída
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(PIEZO_BUZZER, OUTPUT);

  // Configuração do Servo Motor
  meuServo.attach(SERVO_PIN);
  meuServo.write(0); // Garante posição inicial em 0° (Fechado)

  // Estado inicial dos componentes físicos (Fechado -> LED Vermelho Aceso)
  digitalWrite(LED_VERMELHO, HIGH);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(PIEZO_BUZZER, LOW);

  // Inicializa a recepção do sinal infravermelho
  IrReceiver.begin(RECV_PIN, ENABLE_LED_FEEDBACK);
  
  Serial.println("Sistema de Portão Automático Iniciado!");
}

void loop() {
  // 1. LEITURA DO CONTROLE REMOTO IR
  if (IrReceiver.decode()) {
    uint16_t comando = IrReceiver.decodedIRData.command;

    if (comando == COMANDO_BOTAO) {
      alternarPortao();
    } else if (comando != 0 && comando != 0xFFFF) {
      Serial.print("Botao ignorado: 0x");
      Serial.println(comando, HEX);
    }
    IrReceiver.resume(); // Prepara o receptor para a próxima leitura
  }

  // 2. LEITURA DOS COMANDOS DA INTERFACE WEB (FLASK VIA SERIAL)
  if (Serial.available() > 0) {
    char comandoSerial = Serial.read();

    // Se receber 'A' e o portão estiver fechado, abre
    if (comandoSerial == 'A' && estadoPortao == 0) {
      alternarPortao();
    } 
    // Se receber 'F' e o portão estiver aberto, fecha
    else if (comandoSerial == 'F' && estadoPortao == 1) {
      alternarPortao();
    }
  }
}

// --- FUNÇÃO PARA MOVER O SERVOMOTOR E SINALIZAR ---
void alternarPortao() {
  if (estadoPortao == 0) {
    // === PROCESSO DE ABERTURA (0° -> 120°) ===
    for (int angulo = 0; angulo <= 120; angulo += 10) {
      meuServo.write(angulo);
      
      // Pisca LED Verde e apaga Vermelho
      digitalWrite(LED_VERDE, HIGH);
      digitalWrite(LED_VERMELHO, LOW);
      
      tocarBuzzer(100);
      delay(80);
      
      digitalWrite(LED_VERDE, LOW);
    }
    
    // Posição final: LED Verde Fixo
    digitalWrite(LED_VERDE, HIGH);
    digitalWrite(LED_VERMELHO, LOW);
    estadoPortao = 1;
    Serial.println("Estado: ABERTO");

  } else {
    // === PROCESSO DE FECHAMENTO (120° -> 0°) ===
    for (int angulo = 120; angulo >= 0; angulo -= 10) {
      meuServo.write(angulo);
      
      // Pisca LED Vermelho e apaga Verde
      digitalWrite(LED_VERMELHO, HIGH);
      digitalWrite(LED_VERDE, LOW);
      
      tocarBuzzer(100);
      delay(80);
      
      digitalWrite(LED_VERMELHO, LOW);
    }
    
    // Posição final: LED Vermelho Fixo
    digitalWrite(LED_VERMELHO, HIGH);
    digitalWrite(LED_VERDE, LOW);
    estadoPortao = 0;
    Serial.println("Estado: FECHADO");
  }
}

// --- FUNÇÃO AUXILIAR DO BUZZER ---
void tocarBuzzer(int duracao) {
  digitalWrite(PIEZO_BUZZER, HIGH);
  delay(duracao);
  digitalWrite(PIEZO_BUZZER, LOW);
}