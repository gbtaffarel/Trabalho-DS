# Trabalho final - Desenvolvimento de software

Esse sistema recebe um arquivo de texto e mapeia os caracteres para uma sequência
e notas musicais ou ações, que poderá ser reproduzida.

## Tabela de mapeamento

Essa tabela é uma versão inicial e poderá ser alterada.

|Texto|Nota - Ação|
|:---:|:---:|
|A|Lá|
|B|Sí|
|C|Dó|
|D|Ré|
|E|Mi|
|F|Fá|
|G|Sol|
|H|Sí Bb|
|a,b,c,d,e,f,g,h|Silêncio|
|Espaço|Dobra volume, se não puder, deixa no máximo|
|!|Troca para instrumento MIDI #24|
|O,o,I,i,U,u|Troca para instrumento MIDI #110|
|Outra Consoante|Se o anterior era nota, repete, caso contrário, silencio|
|Dígito par|MIDI #(atual + Dígito)|
|? ou .|Aumenta uma oitava|
|NL|Troca para instrumento MIDI #123|
|;|Troca para instrumento MIDI #15|
|,|Troca para instrumento MIDI #114|
|Caso contrário|Se o anterior era nota, repete, caso contrário, silencio|

## Requisitos Funcionais

1. Ler o texto de entrada na interface gráfica do software.
2. Interpretar caracteres, aplicando as regras de mapeamento.
3. Gerar uma saída musical reproduzível.
4. O usuário deve poder configurar parâmetros iniciais (presets), como BPM,
instrumento inicial, oitava padrão, volume, etc.

## Requisitos Não Funcionais

- Modularidade
- Baixo acoplameento e alta coesão
- Principios SOLID
- Legibilidade e boas práticas
- Testabilidade
- Versionamento

## Módulos e Classes

### Módulo de interface gráfica

Esse módulo é responsável por criar e gerenciar a interface gráfica, perminitndo
ao usuário interagir com o o software (entrar o texto, configurar parãmetros
iniciais e iniciar a reprodução musical).

- Classe interface()
  - Métodos
    - desenharInterface()
    - obterTextoEntrada()         > Podemos tentar carregar arquivo
    - obterParametrosIniciais()   > Com base no que foi setado na GUI
    - cancelarReprodução()

### Módulo de interpretação

Esse módulo é responsável por processar a entrada e gerar a lista de eventos musicais.

- Classe interpretador()
  - Métodos
    - carregarRegras()
    - interpretar(texto, contexto)  > Função que vai iterar o texto
    - aplicarRegras(caractere)      > Função que vai aplicar regra caracter por caracter

- Classe estadoMusical()            > Guarda o estado atual da interpretação.
  - volumeAtual
  - oitavaAtual
  - instrumentoAtual
  - ultimoCaractere

### Módulo de geração e eventos

Esse módulo é rsponsável por converter a lista de eventos musicais em uma saída
reproduzível, seja um arquivo MIDI ou uma reprodução direta.

- Classe gerador()
  - Métodos
    - tocarNota(nota, oitava, volume, instrumento)
    - pausar()
    - alterarInstrumento(IdInstrumento)
    - setBPM(bpm)

### Módulo de Regras

Esse módulo visa aumentar a extensibilidade do software e atender ao critério de
open/closed, sendo responsável por definir as regras de mapeamento entre caracteres
e eventos musicais, ao invés de ter essas regras hardcoded no módulo de interpretação.
