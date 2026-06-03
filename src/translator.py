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

        # Tokeniza para facilitar a identificação
        self.padrao_tokens = re.compile(r"\[(\d+)\]|Mb|mb|.")
        self.notas = {
            "A": 69,
            "B": 71,
            "H": 70,
            "C": 60,
            "D": 62,
            "E": 64,
            "Mb": 63,
            "F": 65,
            "G": 67,
        }

    def analisar_linha(self, linha: str) -> List[Union[Nota, Comando]]:
        """
        Lê uma linha inteira de texto, extrai os tokens via regex e retorna uma lista de instruções estruturadas.
        """

        instrucoes = []

        for match in self.padrao_tokens.finditer(linha):
            token_completo = match.group(0)
            grupo_atraso = match.group(1)

            # Trata o caso especifico do atraso [n]
            if grupo_atraso is not None:
                valor_atraso = int(grupo_atraso)
                instrucoes.append(Comando(acao="atraso", parametro=valor_atraso))
                continue

            instrucao = self._traduzir_token(token_completo)
            if instrucao:
                instrucoes.append(instrucao)

        return instrucoes

    def _traduzir_token(self, token: str) -> Union[Nota, Comando, None]:
        """
        Recebe um token isolado (ex: "Mb", "C", ">", " ") e retorna o objeto correspondente.
        """

        # Analisa notas
        if token in self.notas:
            return Nota(valor=self.notas[token])

        # Analisa alterador de bpm
        elif token == ">":
            return Comando(acao="bpm", parametro=10)
        elif token == "<":
            return Comando(acao="bpm", parametro=-10)

        # Analisa alterador de oitava
        elif token == "?":
            return Comando(acao="oitava", parametro=1)
        elif token == "V":
            return Comando(acao="oitava", parametro=-1)

        elif token == " ":
            return Comando(acao="volume", parametro=2)
        elif token == "!":
            return Comando(acao="instrumento", parametro=22)

        elif token == ";":
            return Comando(acao="instrumento", parametro=15)
        elif token == ",":
            return Comando(acao="instrumento", parametro=20)

        # Pausas (a-h minúsculas)
        elif token in ["a", "b", "h", "c", "d", "e", "mb", "f", "g"]:
            return Comando(acao="pausa", parametro=None)

        # Vogais soltas e consoantes (Repetição/Consonante)
        elif token.isalpha():  # Se for letra e não caiu nas regras acima
            return Comando(acao="consoante", parametro=None)

        # Caracteres não mapeados
        return None

    #   CODIGO DA PRIMEIRA FASE
    #   def translate(self, char):
    #     if char in self.notas:
    #         teste = self.notas.get(char)
    #         return teste
    #
    #     # Transforma o caractere para minusculo para facilitar comparacoes
    #     c = char.lower()
    #
    #     if c in "abcdefgh":
    #         return ["volume", 0]
    #
    #     if c == " ":
    #         return ["volume", 2]
    #
    #     if c == "!":
    #         return ["instrument", 24]
    #
    #     if c in "oiu":
    #         return ["instrument", 110]
    #
    #     if c in "jklmnpqrstvwxyz":
    #         return ["consonant"]
    #
    #     if char.isdigit() and int(char) % 2 == 0:
    #         return ["instrument+", int(char)]
    #
    #     if c == "?":
    #         return ["oitava"]
    #
    #     if c == "\n":
    #         return ["instrument", 123]
    #
    #     if c == ";" or (char.isdigit() and int(char) % 2 != 0):
    #         return ["instrument", 15]
    #
    #     if c == ",":
    #         return ["instrument", 114]
    #
    #     return ["consonant"]
