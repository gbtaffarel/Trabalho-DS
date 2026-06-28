import pytest
from src.midigen import MidiGen, MidiConfig, MICROSEGUNDOS_POR_MINUTO
from src.interpretador import ConfigVoz


def test_calculo_bpm_constante():
    """
    Garante que a conversão de BPM para microssegundos usa a constante
    corretamente (ex: 120 bpm -> get_actual_bpm() retorna 120).
    """
    bpm_inicial = 120
    midi = MidiGen(volume=100, bpm=bpm_inicial, instrument=1, oitava=4)

    assert midi.get_actual_bpm() == bpm_inicial

    novo_bpm = 60
    midi.set_bpm(novo_bpm)
    assert midi.get_actual_bpm() == novo_bpm


def test_midigen_injecao_dependencias():
    """
    Garante que a dependência config_vozes seja injetada no construtor
    corretamente, garantindo que o objeto nasce num estado válido.
    """
    vozes = [ConfigVoz(instrumento=1, volume=100, oitava_base=4, delay=2)]

    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4, config_vozes=vozes)

    assert midi.config_vozes == vozes
    assert len(midi.config_vozes) == 1
    assert midi.config_vozes[0].delay == 2


def test_add_nota():
    """Testa o método add que insere notas na track."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    midi.add(60, track_index=0)
    assert len(midi.tracks[0]) == 4

    midi.add(64, track_index=1)
    assert len(midi.tracks[1]) == 4


def test_add_nota_com_volume_customizado():
    """Testa add com volume diferente do padrão."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    midi.add(60, track_index=0, volume=50)
    assert len(midi.tracks[0]) == 4


def test_add_track_invalida():
    """Testa que add com track_index inválido levanta IndexError."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    with pytest.raises(IndexError):
        midi.add(60, track_index=10)


def test_set_instrument_track_especifica():
    """Testa set_instrument para uma track específica."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4, config_vozes=[])

    midi.set_instrument(24, track_index=2)
    assert midi.instrument == 24


def test_set_instrument_todas_tracks():
    """Testa set_instrument sem track_index (aplica a todas)."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    midi.set_instrument(24)
    assert midi.instrument == 24


def test_set_instrument_com_delay():
    """Testa set_instrument com atraso inicial."""
    vozes = [ConfigVoz(instrumento=1, volume=100, oitava_base=4, delay=3)]
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4, config_vozes=vozes)

    midi.set_instrument(24, track_index=0)
    assert midi.instrument == 24
    assert len(midi.tracks[0]) > 2


def test_set_bpm_valido():
    """Testa set_bpm com valor válido."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    midi.set_bpm(100)
    assert midi.get_actual_bpm() == 100


def test_set_bpm_zero_levanta_erro():
    """Testa que set_bpm com zero levanta ValueError."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    with pytest.raises(ValueError, match="BPM deve ser maior que zero"):
        midi.set_bpm(0)


def test_set_bpm_negativo_levanta_erro():
    """Testa que set_bpm com valor negativo levanta ValueError."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    with pytest.raises(ValueError, match="BPM deve ser maior que zero"):
        midi.set_bpm(-10)


def test_set_volume_valido():
    """Testa set_volume com valor válido."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    midi.set_volume(80)
    assert midi.volume == 80


def test_set_volume_zero():
    """Testa set_volume com zero (válido)."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    midi.set_volume(0)
    assert midi.volume == 0


def test_set_volume_127():
    """Testa set_volume com 127 (válido)."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    midi.set_volume(127)
    assert midi.volume == 127


def test_set_volume_fora_range_levanta_erro():
    """Testa que set_volume com valor fora de 0-127 levanta ValueError."""
    midi = MidiGen(volume=100, bpm=120, instrument=1, oitava=4)

    with pytest.raises(ValueError, match="Volume deve estar entre 0 e 127"):
        midi.set_volume(128)

    with pytest.raises(ValueError, match="Volume deve estar entre 0 e 127"):
        midi.set_volume(-1)


def test_midigen_com_midiconfig():
    """Testa criação de MidiGen com MidiConfig."""
    config = MidiConfig(volume=80, bpm=100, instrument=5, oitava=3)
    midi = MidiGen(config)

    assert midi.volume == 80
    assert midi.get_actual_bpm() == 100
    assert midi.instrument == 5


def test_constructor_bpm_zero_levanta_erro():
    """Testa que construtor com bpm=0 levanta ValueError."""
    with pytest.raises(ValueError, match="BPM deve ser maior que zero"):
        MidiGen(bpm=0)


def test_constructor_volume_invalido_levanta_erro():
    """Testa que construtor com volume inválido levanta ValueError."""
    with pytest.raises(ValueError, match="Volume deve estar entre 0 e 127"):
        MidiGen(volume=200)