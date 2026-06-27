import pytest
from src.midigen import Midigen, MICROSEGUNDOS_POR_MINUTO
from src.interpretador import ConfigVoz


def test_calculo_bpm_constante():
    """
    Garante que a conversão de BPM para microssegundos usa a constante
    corretamente (ex: 120 bpm -> 500.000 microssegundos).
    """
    bpm_inicial = 120
    midi = Midigen(volume=100, bpm=bpm_inicial, instrument=1, oitava=4)

    esperado = int(MICROSEGUNDOS_POR_MINUTO / bpm_inicial)
    assert midi.get_bpm() == esperado

    novo_bpm = 60
    midi.set_bpm(novo_bpm)
    esperado_novo = int(MICROSEGUNDOS_POR_MINUTO / novo_bpm)
    assert midi.get_bpm() == esperado_novo


def test_midigen_injecao_dependencias():
    """
    Garante que a dependência config_vozes seja injetada no construtor
    corretamente, garantindo que o objeto nasce num estado válido.
    """
    vozes = [ConfigVoz(instrumento=1, volume=100, oitava_base=4, delay=2)]

    # Instanciação completa numa única etapa
    midi = Midigen(volume=100, bpm=120, instrument=1, oitava=4, config_vozes=vozes)

    assert midi.config_vozes == vozes
    assert len(midi.config_vozes) == 1
    assert midi.config_vozes[0].delay == 2
