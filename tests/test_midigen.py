import pytest
from src.midigen import midigen, MICROSEGUNDOS_POR_MINUTO


def test_calculo_bpm_constante():
    """
    Garante que a conversão de BPM para microssegundos usa a constante
    corretamente (ex: 120 bpm -> 500.000 microssegundos).
    """
    bpm_inicial = 120
    midi = midigen(volume=100, bpm=bpm_inicial, instrument=1, oitava=4)

    esperado = int(MICROSEGUNDOS_POR_MINUTO / bpm_inicial)
    assert midi.get_bpm() == esperado

    novo_bpm = 60
    midi.set_bpm(novo_bpm)
    esperado_novo = int(MICROSEGUNDOS_POR_MINUTO / novo_bpm)
    assert midi.get_bpm() == esperado_novo
