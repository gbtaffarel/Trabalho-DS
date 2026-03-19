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
|H|Sí bb|
|a,b,c,d,e,f,g,h|Silêncio|
|Espaço|Dobra volume, se não puder, deixa no max|
|!|MIDI #24|
|O,o,I,i,U,u|MIDI #110|
|Outra Consoante|Se o anterior era nota, repete, caso contrário, silencio|
|Dígito par|MIDI #(atual + Dígito)|
|? ou .|Aumenta uma oitava|
|NL|MIDI #123|
|;|MIDI #15|
|,|MIDI #114|
|Caso contrário|Se o anterior era nota, repete, caso contrário, silencio|
