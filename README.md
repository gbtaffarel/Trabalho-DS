# Gerador de Música a Partir de Texto - Fase 2

Este repositório contém a implementação da Fase 2 do Trabalho Prático da disciplina de desenvolvimento de software. O objetivo fundamental é definir, implementar, testar e depurar um software capaz de gerar música a partir da leitura de textos.

---

## Instruções para Execução

### Requisitos de Software

- Interpretador python instalado
- make
- SoundFont (.sf2)
  - Para linux, verifique se a soundfont está ESPECIFICAMENTE no caminho /usr/share/soundfonts/FluidR3_GM.sf2

### Primeira execução no linux

rode o comando para gerar e ativar o amebiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências necessárias:

```bash
make install
```

Verifique se todos os requisitos estão instalados corretamente:

```bash
make check
```

Se tudo estiver correto, pode executar o programa:

```bash
make run
```

---

## Novidades e Funcionalidades da Fase 2

Nesta segunda fase de desenvolvimento, o sistema recebeu atualizações importantes:

- A entrada de texto pelo usuário pode ser feita através de digitação em campo editável, leitura de um arquivo TXT, ou ambos.

- Arquivos de texto modificados na interface podem ser salvos, substituindo o arquivo original.

- O sistema agora exporta e salva o arquivo de áudio resultante no formato MIDI.

- O grupo de desenvolvimento define as regras de nomenclatura e o diretório padrão para o salvamento dos arquivos MIDI, ou delega essa escolha ao usuário.

- Todos os instrumentos musicais do sistema agora seguem o padrão General MIDI (GM), que conta com 128 opções.

---

## Mapeamento em Fuga (Polifonia)

A alteração mais significativa desta etapa é a mudança estrutural do mapeamento para suportar melodias em "fuga", simulando as composições polifônicas do período Barroco de Johann Sebastian Bach.

### Dinâmica das Vozes

- O arquivo de texto é lido e dividido em linhas.

- Cada linha processada representa uma voz musical independente (V0, V1, V2, etc.) que tocará de forma simultânea com as demais.

- As quebras de linha funcionam exclusivamente como separadores de vozes e são ignoradas durante a interpretação das notas.

- Para simular as entradas defasadas características de uma fuga, é possível definir um atraso inicial em batidas (beats) para cada voz, inserindo um número entre colchetes no começo da linha (exemplo: `[4]` indica quatro beats de pausa).

### Configuração Inicial por Voz

As vozes recebem valores padrão distintos para permitir o contraste de registros acústicos. A partir da Voz 4, os valores cíclicos de oitava e volume recomeçam.

| Identificador | Oitava Base | Volume Base | Sugestão de Instrumento |
| --- | --- | --- | --- |
| **Voz 0** | 6 | 100 | Cravo (GM 6) |
| **Voz 1** | 5 | 80 | Órgão (GM 20) |
| **Voz 2** | 4 | 60 | Piano (GM 0) |
| **Voz 3** | 3 | 40 | Fagote (GM 70) |

### Mapeamento de Caracteres

A leitura individual dos caracteres dentro de uma voz determina as ações musicais do sistema:

- Letras de **A** até **H** representam notas musicais, onde "Mb" corresponde a Mi bemol e "H" corresponde a Si bemol.

- Letras de **a** até **h** (minúsculas) representam pausas.

- O caractere de **espaço** dobra o volume atual da voz, respeitando o limite máximo de 127.

- O caractere **?** sobe em uma oitava a nota da voz atual.

- O caractere **V** desce em uma oitava a nota da voz atual.

- O caractere **!** troca o instrumento da voz atual para Harmônica (GM 22).

- O caractere **;** troca o instrumento da voz atual para Tubular Bells (GM 15).

- O caractere **,** troca o instrumento da voz atual para Church Organ (GM 20).

- O caractere **>** aumenta o andamento geral (BPM) da música em 10 unidades.

- O caractere **<** diminui o andamento geral (BPM) da música em 10 unidades.

- As vogais **O, I, U** e quaisquer outras **consoantes** não especificadas irão repetir a última nota executada.

- Caso nenhuma nota anterior tenha sido registrada, as vogais e consoantes não mapeadas inserem uma pausa.

---

## Fases de Entrega

O desenvolvimento deste trabalho prático é fragmentado nas seguintes entregas:

1. **Requisitos:** Adição de novos requisitos funcionais e não-funcionais à lista concebida na Fase 1 do projeto.

1. **Projeto de Classes:** Reprojeto do modelo funcional, expandindo as classes originais para comportar as novas exigências.

1. **Interface (UI):** Criação de croquis para a nova interface de usuário, seguidos da devida justificativa para os layouts e comportamentos propostos.

1. **Implementação:** Programação de um protótipo, incluindo rotinas de teste e depuração, usando tecnologia e plataforma escolhidas pelo próprio grupo.

1. **Apresentação:** Entrega de documentação final, avaliação de código no GitHub, possível apresentação para a turma e sessão especial de demonstração direta para o professor.
