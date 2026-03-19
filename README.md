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

## Requisitos Funcionais:

1. Ler o texto de entrada na interface gráfica do software.
2. Interpretar caracteres, aplicando as regras de mapeamento.
3. Gerar uma saída musical reproduzível.
4. O usuário deve poder configurar parâmetros iniciais (presets), como BPM, 
instrumento inicial, oitava padrão, volume, etc.

## Requisitos Não Funcionais:

- Modularidade
- Baixo acoplameento e alta coesão
- Principios SOLID
- Legibilidade e boas práticas
- Testabilidade
- Versionamento
