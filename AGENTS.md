# AGENTS.md - Guia do Repositório (Atualizado FASE 2)

## Visão Geral

Gerador de trilhas sonoras MIDI em Python a partir de arquivos de texto. Mapeia caracteres para notas musicais, instrumentos, volume e mudanças de oitava. O sistema foi atualizado para suportar **Interface Gráfica (GUI)** e **polifonia em estilo Fuga de Bach**, onde cada linha de texto representa uma voz musical independente.

## Stack Tecnológica

- **Linguagem:** Python 3
- **Bibliotecas:** `mido` (I/O de MIDI), `customtkinter` (GUI), `midi2audio` (conversão WAV via FluidSynth opcional)
- **Arquitetura:** Pipeline modular estruturado nos módulos: `gui` → `entrada` → `interpretador` / `translator` → `midigen`.

## Comandos Críticos

- **Executar:** `python main.py` (Inicia a interface gráfica)
- **Bypass da Interface (Testes):** `python main.py --cli --file natal.txt`
- **Instalar dependências:** `pip install mido customtkinter midi2audio` (sem `requirements.txt`)

## Contexto de Desenvolvimento

- **SoundFont requerido para WAV:** `FluidR3_GM.sf2` deve existir na raiz (não rastreado, ignorado no git). Sem ele, apenas `.mid` é gerado.
- **Saída:** Arquivo `.mid` salvo no diretório escolhido pelo usuário na interface.
- **Idioma:** Código, comentários e interface em **Português**.
- **Regras Fuga de Bach:** Linhas = Vozes (V0, V1...). Suporte a delays de entrada `[n]`, controle de BPM (`>`, `<`) e oitavas/volumes base específicos por voz.

## Bugs Conhecidos e Débitos Técnicos

- **Bug de Tipagem Numérica (`translator.py`):** A verificação `isinstance(c, int)` é um código morto (dead code), pois a entrada do caractere `c` é sempre uma string. Isso impede que regras de dígitos pares/ímpares (ex: somar valor ao instrumento atual) sejam executadas. **Solução necessária:** Usar `c.isdigit()`.
- **Quebras de Linha (`NL`):** Na Fase 1 o `NL` trocava instrumento; na Fase 2, o `NL` deve ser ignorado/usado apenas como separador de vozes, necessitando refatoração no loop de leitura.

## Entrypoints & Fluxo de Execução

1. `main.py / modulo_interface` - Ponto de entrada. Renderiza o layout `customtkinter` e captura texto, BPM e setups da UI.
2. `modulo_entrada` - Lê o texto da caixa de entrada ou carrega arquivo `.txt`. Divide o texto cru em um array de linhas (vozes).
3. `interpretador.py` - Engine de regras musicais. Itera sobre cada voz de forma independente. Processa os tokens de atraso `[n]` no início da linha.
4. `translator.py` - Mapeia os caracteres para instruções no formato dicionário ou tupla (ex: `["nota", "C"]`, `["bpm", +10]`).
5. `midigen.py` - Geração do arquivo MIDI. Agora precisa criar múltiplos `MidiTrack()` (um para cada linha interpretada) para permitir a polifonia.

## Notas de Arquitetura

- **Inversão de Dependência:** A classe `Interpretador` recebe as instâncias de `gerador_midi` e `tradutor` via injeção de dependência no construtor.
- **Rastreamento de Estado por Voz:** O controle de estado mudou de global para local. O TAD `estadoMusical` agora precisa manter instâncias separadas para cada linha/voz, rastreando `last_note`, `volume_base` (V0=100, V1=80...) e `oitava_base` (V0=6, V1=5...).
- **Cálculo de Oitava:** A fórmula de conversão de nota MIDI continua sendo `nota_real = instrucao + (oitava + 1) * 12`, porém o multiplicador de oitava agora é relativo ao estado de voz atual.
