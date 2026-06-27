from reader import reader
from translator import Translator
from midigen import midigen
from interpretador import Interpretador, EstadoVoz, ConfigVoz


class GerarMusica:
    """
    Serviço de aplicação responsável por orquestrar o fluxo completo:
    leitura, tradução, interpretação e geração do arquivo MIDI.
    """

    def executar(
        self,
        texto: str,
        bpm: int,
        vozes: list[ConfigVoz],
        arquivo_saida: str = "saida_gerada.mid",
    ) -> str:
        # 1. Carrega o texto
        texto_reader = reader()
        texto_reader.load_from_string(texto)

        # 2. Inicializa o Tradutor
        tradutor = Translator()

        # 3. Extrai a voz base para configuração inicial do gerador MIDI
        voz_padrao = (
            vozes[0] if vozes else ConfigVoz(instrumento=1, volume=100, oitava_base=5)
        )

        midi = midigen(
            volume=voz_padrao.volume,
            bpm=bpm,
            instrument=voz_padrao.instrumento,
            oitava=voz_padrao.oitava_base,
            config_vozes=vozes,
        )

        # 4. Inicializa o Interpretador injetando as dependências
        interpretador = Interpretador(
            gerador_midi=midi, tradutor=tradutor, config_vozes=vozes
        )

        # 6. Executa a interpretação e salva o ficheiro
        interpretador.interpretar(texto_reader)
        midi.save_mid(arquivo_saida)

        return arquivo_saida
