import pytest
from unittest.mock import MagicMock
from src.interpretador import EstadoVoz, ConfigVoz, Interpretador


def test_estado_voz_sem_estado_global():
    """
    Garante que EstadoVoz cria instâncias corretamente recebendo as configurações
    via parâmetro, sem depender de ClassVar.
    """
    configs = [
        ConfigVoz(instrumento=10, volume=85, oitava_base=5, delay=0),
        ConfigVoz(instrumento=20, volume=70, oitava_base=4, delay=2),
    ]

    estado_v0 = EstadoVoz.criar(id_voz=0, config_vozes=configs)
    assert estado_v0.instrumento_atual == 10
    assert estado_v0.volume_atual == 85
    assert estado_v0.oitava_atual == 5

    estado_v1 = EstadoVoz.criar(id_voz=1, config_vozes=configs)
    assert estado_v1.instrumento_atual == 20
    assert estado_v1.volume_atual == 70

    estado_v2 = EstadoVoz.criar(id_voz=2, config_vozes=None)
    assert estado_v2.instrumento_atual == 0


def test_config_voz_validacao_instrumento():
    """Testa que instrumento deve estar entre 0 e 127."""
    with pytest.raises(ValueError, match="Instrumento deve estar entre 0 e 127"):
        ConfigVoz(instrumento=128, volume=100, oitava_base=4)

    with pytest.raises(ValueError, match="Instrumento deve estar entre 0 e 127"):
        ConfigVoz(instrumento=-1, volume=100, oitava_base=4)


def test_config_voz_validacao_volume():
    """Testa que volume deve estar entre 0 e 127."""
    with pytest.raises(ValueError, match="Volume deve estar entre 0 e 127"):
        ConfigVoz(instrumento=0, volume=128, oitava_base=4)

    with pytest.raises(ValueError, match="Volume deve estar entre 0 e 127"):
        ConfigVoz(instrumento=0, volume=-1, oitava_base=4)


def test_config_voz_validacao_delay():
    """Testa que delay não pode ser negativo."""
    with pytest.raises(ValueError, match="Atraso nao pode ser negativo"):
        ConfigVoz(instrumento=0, volume=100, oitava_base=4, delay=-1)


def test_estado_voz_dobrar_volume():
    """Testa dobrar_volume não ultrapassa 127."""
    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)
    estado.volume_atual = 80
    estado.dobrar_volume()
    assert estado.volume_atual == 127

    estado.volume_atual = 100
    estado.dobrar_volume()
    assert estado.volume_atual == 127


def test_estado_voz_alterar_oitava():
    """Testa alteração de oitava com limites."""
    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)

    estado.oitava_atual = 5
    estado.alterar_oitava(2)
    assert estado.oitava_atual == 7

    estado.alterar_oitava(3)
    assert estado.oitava_atual == 7


def test_estado_voz_registrar_nota():
    """Testa registrar nota."""
    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)
    estado.registrar_nota(60)
    assert estado.ultima_nota == 60
    assert estado.tocou_nota is True


def test_estado_voz_registrar_pausa():
    """Testa registrar pausa."""
    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)
    estado.tocou_nota = True
    estado.registrar_pausa()
    assert estado.tocou_nota is False


def test_interpretador_inicializacao():
    """Testa que Interpretador recebe dependências via injeção."""
    mock_gerador = MagicMock()
    mock_tradutor = MagicMock()
    config_vozes = [ConfigVoz(instrumento=1, volume=100, oitava_base=4, delay=0)]

    interpretador = Interpretador(
        gerador_midi=mock_gerador, tradutor=mock_tradutor, config_vozes=config_vozes
    )

    assert interpretador.gerador_midi is mock_gerador
    assert interpretador.tradutor is mock_tradutor
    assert interpretador.config_vozes == config_vozes


def test_interpretador_inicializacao_sem_vozes():
    """Testa Interpretador com config_vozes=None."""
    mock_gerador = MagicMock()
    mock_tradutor = MagicMock()

    interpretador = Interpretador(
        gerador_midi=mock_gerador, tradutor=mock_tradutor, config_vozes=None
    )

    assert interpretador.config_vozes == []


def test_mudar_bpm():
    """Testa o método _mudar_bpm."""
    mock_gerador = MagicMock()
    mock_gerador.get_actual_bpm.return_value = 120
    mock_tradutor = MagicMock()

    interpretador = Interpretador(
        gerador_midi=mock_gerador, tradutor=mock_tradutor, config_vozes=None
    )

    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)
    interpretador._mudar_bpm(10, estado, 0)

    mock_gerador.set_bpm.assert_called_once_with(130)


def test_tocar_consoante_com_nota():
    """Testa _tocar_consoante quando há nota anterior."""
    mock_gerador = MagicMock()
    mock_tradutor = MagicMock()

    interpretador = Interpretador(
        gerador_midi=mock_gerador, tradutor=mock_tradutor, config_vozes=None
    )

    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)
    estado.tocou_nota = True
    estado.ultima_nota = 60

    interpretador._tocar_consoante(None, estado, 0)

    mock_gerador.set_volume.assert_called_once()
    mock_gerador.add.assert_called_once_with(60, 0)


def test_tocar_consoante_sem_nota():
    """Testa _tocar_consoante quando não há nota anterior."""
    mock_gerador = MagicMock()
    mock_tradutor = MagicMock()

    interpretador = Interpretador(
        gerador_midi=mock_gerador, tradutor=mock_tradutor, config_vozes=None
    )

    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)
    estado.tocou_nota = False

    interpretador._tocar_consoante(None, estado, 0)

    mock_gerador.set_volume.assert_not_called()


def test_somar_instrumento():
    """Testa _somar_instrumento com overflow."""
    mock_gerador = MagicMock()
    mock_tradutor = MagicMock()

    interpretador = Interpretador(
        gerador_midi=mock_gerador, tradutor=mock_tradutor, config_vozes=None
    )

    estado = EstadoVoz.criar(id_voz=0, config_vozes=None)
    estado.instrumento_atual = 125

    interpretador._somar_instrumento(10, estado, 0)

    assert estado.instrumento_atual == 7
    mock_gerador.set_instrument.assert_called_once_with(7, 0)