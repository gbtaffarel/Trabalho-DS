import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dataclasses import dataclass
from translator import Nota, Comando

OITAVA_PADRAO = [6, 5, 4, 3]
VOLUME_PADRAO = [100, 80, 60, 40]
INSTRUMENTO_PADRAO = [6, 20, 0, 70]


@dataclass
class ConfigVoz:
    instrumento: int
    volume: int
    oitava_base: int
    delay: int = 0

    def __post_init__(self):
        if not 0 <= self.instrumento <= 127:
            raise ValueError("Instrumento deve estar entre 0 e 127")
        if not 0 <= self.volume <= 127:
            raise ValueError("Volume deve estar entre 0 e 127")
        if self.delay < 0:
            raise ValueError("Atraso nao pode ser negativo")


@dataclass
class EstadoVoz:
    id_voz: int
    oitava_atual: int
    volume_atual: int
    instrumento_atual: int
    ultima_nota: int = 60
    tocou_nota: bool = False

    @classmethod
    def criar(cls, id_voz: int, config_vozes: list = None):
        if config_vozes and id_voz < len(config_vozes):
            cfg = config_vozes[id_voz]
            return cls(
                id_voz=id_voz,
                oitava_atual=cfg.oitava_base,
                volume_atual=cfg.volume,
                instrumento_atual=cfg.instrumento,
            )

        # Fallback padrão
        idx = id_voz % 4
        return cls(
            id_voz=id_voz,
            oitava_atual=OITAVA_PADRAO[idx],
            volume_atual=VOLUME_PADRAO[idx],
            instrumento_atual=INSTRUMENTO_PADRAO[idx],
        )

    def dobrar_volume(self):
        self.volume_atual = min(127, self.volume_atual * 2)

    def alterar_oitava(self, deslocamento):
        nova_oitava = self.oitava_atual + deslocamento
        if 0 <= nova_oitava <= 9:
            self.oitava_atual = nova_oitava

    def registrar_nota(self, nota):
        self.ultima_nota = nota
        self.tocou_nota = True

    def registrar_pausa(self):
        self.tocou_nota = False


class Interpretador:
    def __init__(self, gerador_midi, tradutor, config_vozes=None):
        """
        Aplica o princípio de Inversão de Dependência (SOLID).
        A classe recebe os objetos prontos em vez de instanciá-los internamente.
        """
        self.gerador_midi = gerador_midi
        self.tradutor = tradutor
        self.config_vozes = config_vozes or []

        self._regras = {
            "volume": self._dobrar_volume,
            "instrumento": self._mudar_instrumento,
            "instrumento_add": self._somar_instrumento,
            "oitava": self._mudar_oitava,
            "atraso": self._aplicar_atraso,
            "bpm": self._mudar_bpm,
            "pausa": self._tocar_pausa,
            "consoante": self._tocar_consoante,
        }

    def interpretar(self, texto_reader):
        """
        Itera sobre a entrada de texto e delega a aplicação das regras.
        Cada linha do texto corresponde a uma voz diferente.
        """
        track_index = 0
        while not texto_reader.is_empty():
            linha = texto_reader.next_line()  # Obter a próxima linha
            if linha is None:
                break

            estado = EstadoVoz.criar(track_index, config_vozes=self.config_vozes)

            self.gerador_midi.set_instrument(estado.instrumento_atual, track_index)

            instrucoes = self.tradutor.analisar_linha(linha)

            for instrucao in instrucoes:
                if isinstance(instrucao, Nota):
                    self._tocar_nota(instrucao.valor, estado, track_index)
                elif isinstance(instrucao, Comando):
                    funcao = self._regras.get(instrucao.acao)
                    if funcao:
                        funcao(instrucao.parametro, estado, track_index)
            track_index += 1

    # --- Métodos auxiliares privados (Clean Code) ---

    def _tocar_nota(self, valor_base, estado: EstadoVoz, track_index):
        # Subtraímos 4 para que o cálculo desloque a nota corretamente.
        deslocamento_oitava = (estado.oitava_atual - 4) * 12
        nota_real = valor_base + deslocamento_oitava

        # Se passar de 127, vira 127. Se for menor que 0, vira 0.
        nota_real = max(0, min(127, nota_real))

        self.gerador_midi.set_volume(estado.volume_atual)
        self.gerador_midi.add(nota_real, track_index)
        estado.registrar_nota(nota_real)

    def _dobrar_volume(self, parametro, estado: EstadoVoz, track_index):
        estado.dobrar_volume()

    def _mudar_oitava(self, parametro, estado: EstadoVoz, track_index):
        estado.alterar_oitava(parametro)

    def _tocar_pausa(self, parametro, estado: EstadoVoz, track_index):
        self.gerador_midi.add(0, track_index, volume=0)
        estado.registrar_pausa()

    def _mudar_instrumento(self, parametro, estado: EstadoVoz, track_index):
        estado.instrumento_atual = parametro
        self.gerador_midi.set_instrument(parametro, track_index)

    def _somar_instrumento(self, parametro, estado: EstadoVoz, track_index):
        novo_inst = (estado.instrumento_atual + parametro) % 128
        estado.instrumento_atual = novo_inst
        self.gerador_midi.set_instrument(novo_inst, track_index)

    def _aplicar_atraso(self, parametro, estado: EstadoVoz, track_index):
        for _ in range(parametro):
            self._tocar_pausa(None, estado, track_index)

    def _mudar_bpm(self, parametro, estado: EstadoVoz, track_index):
        bpm_atual = self.gerador_midi.get_actual_bpm()
        novo_bpm = max(40, bpm_atual + parametro)
        self.gerador_midi.set_bpm(novo_bpm)

    def _tocar_consoante(self, parametro, estado: EstadoVoz, track_index):
        if estado.tocou_nota:
            self.gerador_midi.set_volume(estado.volume_atual)
            self.gerador_midi.add(estado.ultima_nota, track_index)
        else:
            self._tocar_pausa(None, estado, track_index)
