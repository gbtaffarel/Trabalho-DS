import pytest
from src.interpretador import EstadoVoz, ConfigVoz


def test_estado_voz_sem_estado_global():
    """
    Garante que EstadoVoz cria instâncias corretamente recebendo as configurações
    via parâmetro, sem depender de ClassVar.
    """
    configs = [
        ConfigVoz(instrumento=10, volume=85, oitava_base=5, delay=0),
        ConfigVoz(instrumento=20, volume=70, oitava_base=4, delay=2),
    ]

    # Teste de criação usando injeção explícita
    estado_v0 = EstadoVoz.criar(id_voz=0, config_vozes=configs)
    assert estado_v0.instrumento_atual == 10
    assert estado_v0.volume_atual == 85
    assert estado_v0.oitava_atual == 5

    # Teste para voz secundária
    estado_v1 = EstadoVoz.criar(id_voz=1, config_vozes=configs)
    assert estado_v1.instrumento_atual == 20
    assert estado_v1.volume_atual == 70

    # Teste do Fallback (quando não há configs para a voz ou lista é vazia)
    estado_v2 = EstadoVoz.criar(id_voz=2, config_vozes=None)
    assert (
        estado_v2.instrumento_atual == 0
    )  # 3º item do array de fallback [6, 20, 0, 70]
