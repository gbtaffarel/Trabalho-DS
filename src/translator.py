# Esse modulo contem o conjunto de regras para traduriz os caracteres
# em notas, instrumentos, oitavas e volume.
import re
from dataclasses import dataclass
from typing import Union, Any, List


@dataclass
class Nota:
    valor: int


@dataclass
class Comando:
    acao: str
    parametro: Any


class Translator:
    def __init__(self):
        # Captura atrasos [n], notas com b bemol e caracteres individuais
        self.padrao_tokens = re.compile(r"\[(\d+)\]|Mb|mb|.")

        # Mapeamento Declarativo de Notas Musicais (Fase 1)
        self.notas = {
            "A": 69,
            "B": 71,
            "C": 60,
            "D": 62,
            "E": 64,
            "F": 65,
            "G": 67,
            "H": 70,  # Nota H (Si bemol)
            "Mb": 63,
            "mb": 63,  # Nota Ré sustenido / Mi bemol
        }

        # Mapeamento Declarativo de Comandos (Substitui os Switch Statements)
        self.comandos_diretos = {
            " ": ("volume", 2),
            "?": ("oitava", 1),
            "V": ("oitava", -1),
            ">": ("bpm", 10),
            "<": ("bpm", -10),
            "!": ("instrumento", 24),  # Nylon Guitar
            ";": ("instrumento", 15),  # Pizzicato Strings
            ",": ("instrumento", 114),  # Agogo
        }

    def analisar_linha(self, linha: str) -> List[Union[Nota, Comando]]:
        """
        Lê uma linha inteira de texto, extrai os tokens via regex e retorna uma lista de instruções estruturadas.
        """
        instrucoes = []

        for match in self.padrao_tokens.finditer(linha):
            token_completo = match.group(0)
            grupo_atraso = match.group(1)

            # Regra de Atraso [n] (Fase 2)
            if grupo_atraso is not None:
                valor_atraso = int(grupo_atraso)
                instrucoes.append(Comando(acao="atraso", parametro=valor_atraso))
                continue

            instrucao = self._traduzir_token(token_completo)
            if instrucao:
                instrucoes.append(instrucao)

        # Simula o efeito da quebra de linha '\n' da Fase 1 (muda instrumento para 123)
        instrucoes.append(Comando(acao="instrumento", parametro=123))

        return instrucoes

    def _traduzir_token(self, token: str) -> Union[Nota, Comando, None]:
        # 1. Notas Musicais Puras (Resolve o conflito do 'mb')
        if token in self.notas:
            return Nota(valor=self.notas[token])

        # 2. Comandos Mapeados (Remove a cadeia longa de if-else)
        if token in self.comandos_diretos:
            acao, param = self.comandos_diretos[token]
            return Comando(acao=acao, parametro=param)

        # 3. Pausas (Letras minúsculas de 'a' a 'h')
        if token in "abcdefgh":
            return Comando(acao="pausa", parametro=None)

        # 4. Regra Algorítmica (Dígitos Numéricos)
        if token.isdigit():
            valor = int(token)
            if valor % 2 == 0:
                return Comando(acao="instrumento_add", parametro=valor)
            return Comando(acao="instrumento", parametro=15)

        # 5. Fallback: Consoantes e Vogais O, I, U
        # (Corrige o bug da especificação: 'o', 'i', 'u' agora repetem a nota
        # tal como qualquer outra consoante não mapeada)
        return Comando(acao="consoante", parametro=None)
