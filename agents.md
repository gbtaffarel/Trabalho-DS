# Instruções de Desenvolvimento: Gerador de Música a partir de Texto (Fase 2)

## 1. Contexto e Objetivo

Você atuará como um desenvolvedor de software criando um Gerador de Música a partir de Texto. [cite_start]O objetivo principal é re-projetar o sistema da Fase 1 para suportar uma estrutura musical de polifonia que simule uma fuga (estilo Johann Sebastian Bach), onde múltiplas vozes interagem simultaneamente[cite: 8, 17, 23].

## 2. Stack Tecnológica

* **Linguagem:** Python
* **Interface Gráfica (GUI):** `customtkinter` (aparência moderna e controles fáceis de usar).
* **Geração MIDI:** `mido` (criação de trilhas, gerenciamento de mensagens MIDI, notas, tempo e instrumentos).
* **Reprodução de Áudio:** `pygame` (especificamente `pygame.mixer.music` para carregar e tocar o arquivo `.mid` gerado em tempo real).

## 3. Requisitos Funcionais e Interface

* [cite_start]**Entrada de Texto:** A entrada deve permitir digitação no teclado e leitura a partir de um arquivo `.txt`[cite: 10].
* [cite_start]**Edição e Salvamento:** O texto importado deve poder ser editado na interface e salvo, substituindo o original[cite: 10, 11].
* [cite_start]**Saída MIDI:** O sistema deve gerar e salvar o resultado em um arquivo `.mid`, permitindo ao usuário escolher o nome e o diretório[cite: 12, 13, 14].
* **Controles da GUI:** Botões para "Importar TXT", "Salvar TXT", "Gerar e Tocar Música", "Pausar/Parar", e "Salvar MIDI".

## 4. Lógica de Negócio: Regras da Fuga e Mapeamento

[cite_start]O mapeamento musical original sofreu alterações significativas para suportar a fuga[cite: 17, 40]. O algoritmo deve processar o texto seguindo estritamente as regras abaixo:

### 4.1. Vozes Independentes

* [cite_start]Cada linha do texto representa uma voz independente[cite: 119].
* [cite_start]As vozes são numeradas sequencialmente ($V0, V1, V2, ...$) e tocadas simultaneamente [polifonia](cite: 120).
* [cite_start]Ignorar quebras de linha para fins de notas; elas servem exclusivamente como separadores de vozes[cite: 93, 151].

### 4.2. Configurações Iniciais por Voz (Ciclo a cada 4 vozes)

[cite_start]Ao iniciar o processamento de uma linha, defina os seguintes estados padrão [o ciclo se repete a partir da voz 4](cite: 127, 134):

* [cite_start]**Voz 0:** Oitava base 6 [cite: 123] | [cite_start]Volume base 100 [cite: 130] | [cite_start]Instrumento Cravo (GM 6) [cite: 136]
* [cite_start]**Voz 1:** Oitava base 5 [cite: 124] | [cite_start]Volume base 80 [cite: 131] | [cite_start]Instrumento Órgão (GM 20) [cite: 137]
* [cite_start]**Voz 2:** Oitava base 4 [cite: 125] | [cite_start]Volume base 60 [cite: 132] | [cite_start]Instrumento Piano (GM 0) [cite: 138]
* [cite_start]**Voz 3:** Oitava base 3 [cite: 126] | [cite_start]Volume base 40 [cite: 133] | [cite_start]Instrumento Fagote (GM 70) [cite: 139]

### 4.3. Atraso de Entrada (Delay)

* [cite_start]O início de cada linha pode conter um número entre colchetes, como `[4]`, que indica um atraso em *beats* antes de a voz começar a tocar[cite: 142, 143].
* [cite_start]Se não houver `[n]`, o atraso é zero e a voz inicia no tempo 0[cite: 143].

### 4.4. Mapeamento de Caracteres

* [cite_start]**Notas (Maiúsculas):** $A=L\dot{a}$, $B=Si$, $C=D\dot{o}$, $D=R\dot{e}$, $E=Mi$, $F=F\dot{a}$, $G=Sol$[cite: 86]. [cite_start]Acréscimos: `Mb` = Mi bemol, `H` = Si bemol[cite: 86].
* [cite_start]**Pausas:** Letras $a-h$ minúsculas geram pausas[cite: 87].
* [cite_start]**Volume:** Espaço dobra o volume [até o limite máximo de 127](cite: 88, 154). [cite_start]Modificações de volume são locais para a voz[cite: 98].
* **Oitava:** `?` sobe uma oitava, `V` desce uma oitava. [cite_start]Estas alterações são locais para a voz da linha e respeitam os limites globais de 0 a 9[cite: 90, 98, 155].
* [cite_start]**BPM (Global):** Padrão inicia em 120[cite: 153]. `>` aumenta o BPM em 10; [cite_start]`<` diminui o BPM em 10[cite: 145, 146]. [cite_start]Pode aparecer em qualquer posição e afeta toda a peça de forma síncrona[cite: 147].
* **Mudança de Instrumento (Local para a voz):**
  * [cite_start]`!` = Harmonica (GM 22) [cite: 89]
  * [cite_start]`;` = Tubular Bells (GM 15) [cite: 91]
  * [cite_start]`,` = Church Organ (GM 20) [cite: 92]
* [cite_start]**Outras Letras (O, I, U e consoantes):** Repete a última nota tocada; se não houver nota anterior, processa como pausa[cite: 148, 149, 150].

## 5. Arquitetura Sugerida

O código deve ser modular. [cite_start]Sugere-se a seguinte divisão de classes[cite: 159]:

1. **`FugueParser`:** Responsável por varrer as linhas do texto, extrair o atraso (`[n]`) e processar os caracteres gerando uma lista de eventos (notas, tempo, instrumentos, volume) para cada voz.
2. **`MidiGenerator`:** Recebe as vozes parseadas. Utiliza o pacote `mido` para criar um arquivo `MidiFile` com um `MidiTrack` para cada voz. Transforma atrasos e BPM em mensagens `mido.MetaMessage('set_tempo')` e notas em `mido.Message('note_on'/'note_off')`.
3. **`AppUI`:** Implementada com `customtkinter`, gerencia o loop da interface, instancição do `FugueParser`, `MidiGenerator` e botões de play usando `pygame`.
