from dataclasses import dataclass
from translator import Nota, Comando


@dataclass
class EstadoVoz:
    id_voz: int
    oitava_atual: int
    volume_atual: int
    instrumento_atual: int
    ultima_nota: int = 60
    tocou_nota: bool = False

    @classmethod
    def criar(cls, id_voz: int):
        ciclo_oitavas = [6, 5, 4, 3]
        ciclo_volumes = [100, 80, 60, 40]
        ciclo_instrumentos = [6, 20, 0, 70]

        idx = id_voz % 4
        return cls(
            id_voz=id_voz,
            oitava_atual=ciclo_oitavas[idx],
            volume_atual=ciclo_volumes[idx],
            instrumento_atual=ciclo_instrumentos[idx],
        )


class Interpretador:
    def __init__(self, gerador_midi, tradutor):
        """
        Aplica o princípio de Inversão de Dependência (SOLID).
        A classe recebe os objetos prontos em vez de instanciá-los internamente.
        """
        self.gerador_midi = gerador_midi
        self.tradutor = tradutor

        self._regras = {
            "volume": self._dobrar_volume,
            "instrumento": self._mudar_instrumento,
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

            estado = EstadoVoz.criar(track_index)

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
        """Toca uma nota considerando a oitava atual."""
        nota_real = valor_base + (estado.oitava_atual + 1) * 12
        self.gerador_midi.add(nota_real, track_index, volume=estado.volume_atual)
        estado.ultima_nota = nota_real
        estado.tocou_nota = True

    def _dobrar_volume(self, parametro, estado: EstadoVoz, track_index):
        """Dobra o volume local da voz, respeitando o limite máximo de 127."""
        novo_vol = estado.volume_atual * 2
        if novo_vol > 127:
            novo_vol = 127
        estado.volume_atual = novo_vol

    def _mudar_instrumento(self, parametro, estado: EstadoVoz, track_index):
        return

    def _mudar_oitava(self, parametro, estado: EstadoVoz, track_index):
        """Aumenta ou diminui a oitava atual da voz. O parâmetro é um inteiro positivo ou negativo."""
        nova_oitava = estado.oitava_atual + parametro
        if 0 <= nova_oitava <= 9:
            estado.oitava_atual = nova_oitava

    def _aplicar_atraso(self, parametro, estado: EstadoVoz, track_index):
        return

    def _mudar_bpm(self, parametro, estado: EstadoVoz, track_index):
        return

    def _tocar_pausa(self, parametro, estado: EstadoVoz, track_index):
        """Simula silencio"""
        self.gerador_midi.add(0, track_index, volume=0)
        estado.tocou_nota = False
        return

    def _tocar_consoante(self, parametro, estado: EstadoVoz, track_index):
        return
