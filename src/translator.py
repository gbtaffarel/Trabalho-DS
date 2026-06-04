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

        # Mapeamento de Notas Musicais (Fase 1)
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
        # Notas Musicais Puras
        if token in self.notas:
            return Nota(valor=self.notas[token])

        c = token.lower()

        # Pausas (Letras minúsculas de 'a' a 'h' e 'mb')
        if c in "abcdefgh" or token in ["mb"]:
            return Comando(acao="pausa", parametro=None)

        # Alteradores de Volume (Espaço duplica o volume)
        if token == " ":
            return Comando(acao="volume", parametro=2)

        # Alteradores de Oitava (+1 ou -1)
        if token == "?":
            return Comando(acao="oitava", parametro=1)
        if token == "V":
            return Comando(acao="oitava", parametro=-1)

        # Alteradores de BPM (Fase 2: +10 ou -10)
        if token == ">":
            return Comando(acao="bpm", parametro=10)
        if token == "<":
            return Comando(acao="bpm", parametro=-10)

        # Instrumentos Mapeados por Caractere
        if token == "!":
            return Comando(acao="instrumento", parametro=24)  # Nylon Guitar
        if token == ";":
            return Comando(acao="instrumento", parametro=15)  # Pizzicato Strings
        if token == ",":
            return Comando(acao="instrumento", parametro=114)  # Agogo
        if c in "oiu":
            return Comando(acao="instrumento", parametro=110)  # Fiddle

        # Regra de Dígitos Numéricos
        if token.isdigit():
            valor = int(token)
            if valor % 2 == 0:
                # Dígito par: Soma o valor ao instrumento atual
                return Comando(acao="instrumento_add", parametro=valor)
            else:
                # Dígito ímpar: Altera para o instrumento 15
                return Comando(acao="instrumento", parametro=15)

        # Consoantes e Fallback (Repetição de nota / Silêncio)
        return Comando(acao="consoante", parametro=None)
