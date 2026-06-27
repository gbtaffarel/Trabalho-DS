import pytest
from unittest.mock import patch
from src.gerar_musica import GerarMusica
from src.interpretador import ConfigVoz


@patch("src.gerar_musica.Reader")
@patch("src.gerar_musica.Translator")
@patch("src.gerar_musica.MidiGen")
@patch("src.gerar_musica.Interpretador")
def test_executar_fluxo_completo(
    MockInterpretador, MockMidiGen, MockTranslator, MockReader
):
    """
    Testa se o orquestrador coordena corretamente as dependências
    e passa a primeira configuração de voz como voz padrão.
    """
    # 1. Configurar os Mocks
    mock_reader_instance = MockReader.return_value
    mock_midi_instance = MockMidiGen.return_value
    mock_interpretador_instance = MockInterpretador.return_value
    mock_translator_instance = MockTranslator.return_value

    gerador = GerarMusica()
    vozes = [ConfigVoz(instrumento=10, volume=80, oitava_base=4, delay=0)]

    # 2. Executar a função
    resultado = gerador.executar(
        texto="A B C", bpm=120, vozes=vozes, arquivo_saida="teste_orquestrador.mid"
    )

    # 3. Asserções
    assert resultado == "teste_orquestrador.mid"

    # Verifica se o texto foi carregado
    mock_reader_instance.load_from_string.assert_called_once_with("A B C")

    # Verifica se o gerador MIDI foi inicializado com a voz[0]
    MockMidiGen.assert_called_once_with(
        volume=80, bpm=120, instrument=10, oitava=4, config_vozes=vozes
    )

    # Verifica se o Interpretador recebeu as injeções corretas (Refatoração do Passo 1)
    MockInterpretador.assert_called_once_with(
        gerador_midi=mock_midi_instance,
        tradutor=mock_translator_instance,
        config_vozes=vozes,
    )

    # Verifica se o ficheiro foi interpretado e salvo
    mock_interpretador_instance.interpretar.assert_called_once_with(
        mock_reader_instance
    )
    mock_midi_instance.save_mid.assert_called_once_with("teste_orquestrador.mid")


@patch("src.gerar_musica.Reader")
@patch("src.gerar_musica.Translator")
@patch("src.gerar_musica.MidiGen")
@patch("src.gerar_musica.Interpretador")
def test_executar_fluxo_sem_vozes_fallback(
    MockInterpretador, MockMidiGen, MockTranslator, MockReader
):
    """
    Testa o comportamento de fallback (voz padrão) quando a
    lista de configurações de vozes está vazia.
    """
    gerador = GerarMusica()

    gerador.executar(texto="A", bpm=100, vozes=[])

    # Verifica se o MidiGen foi chamado com os valores fixos de fallback
    MockMidiGen.assert_called_once_with(
        volume=100, bpm=100, instrument=1, oitava=5, config_vozes=[]
    )
