#include <IRremote.h>
#include <Servo.h>

// Definição dos Pinos
const int PIN_IR = 2;
const int PIN_SERVO = 9;
const int PIN_LED_VERDE = 3;
const int PIN_LED_VERMELHO = 4;
const int PIN_BUZZER = 5;

// Mapeamento dos Botões
const unsigned long BOTAO_PORTAO = 0xFFA25D; // Botão maior (POWER) -> Abre/Fecha o portão
const unsigned long BOTAO_BIPE   = 0xFF22DD; // Botão menor (TEST) -> Ativa o buzzer

// Posições do Servo (Ângulos)
const int ANGULO_FECHADO = 0;
const int ANGULO_ABERTO  = 90;

Servo meuServo;
bool portaoAberto = false;

void setup() {
  Serial.begin(9600);
  
  IrReceiver.begin(PIN_IR, ENABLE_LED_FEEDBACK);
  meuServo.attach(PIN_SERVO);
  
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_VERMELHO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  // Estado Inicial: Portão Fechado
  meuServo.write(ANGULO_FECHADO);
  digitalWrite(PIN_LED_VERMELHO, HIGH);
  digitalWrite(PIN_LED_VERDE, LOW);
}

void loop() {
  if (IrReceiver.decode()) {
    unsigned long codigo = IrReceiver.decodedIRData.decodedRawData;

    // Se o código for do botão maior (POWER) -> Alterna o portão
    if (codigo == BOTAO_PORTAO) {
      if (portaoAberto) {
        // Fechar Portão
        meuServo.write(ANGULO_FECHADO);
        digitalWrite(PIN_LED_VERDE, LOW);
        digitalWrite(PIN_LED_VERMELHO, HIGH);
        
        // Sinal sonoro de fechamento (2 bipes curtos)
        tocarBuzzer(100);
        delay(100);
        tocarBuzzer(100);
        
        portaoAberto = false;
        Serial.println("Portao Fechado");
      } else {
        // Abrir Portão
        meuServo.write(ANGULO_ABERTO);
        digitalWrite(PIN_LED_VERMELHO, LOW);
        digitalWrite(PIN_LED_VERDE, HIGH);
        
        // Sinal sonoro de abertura (1 bipe longo)
        tocarBuzzer(300);
        
        portaoAberto = true;
        Serial.println("Portao Aberto");
      }
    } 
    // Se o código for do botão menor (TEST) -> Ativa apenas o bipe
    else if (codigo == BOTAO_BIPE) {
      tocarBuzzer(150);
      Serial.println("Bipe acionado pelo controle");
    }

    IrReceiver.resume(); // Prepara o receptor para a próxima leitura
  }
}

// Função auxiliar para emissão de som
void tocarBuzzer(int duracaoMs) {
  tone(PIN_BUZZER, 1000); // Frequência de 1kHz
  delay(duracaoMs);
  noTone(PIN_BUZZER);
}