import pytest
from unittest.mock import patch, MagicMock
import pygame
from src.reprodutor import Reprodutor


@pytest.fixture
def mock_pygame():
    """
    Fixture que faz mock dos módulos do pygame.
    Impede que o teste tente usar o hardware de áudio real do sistema.
    """
    with patch("src.reprodutor.pygame.mixer") as mock_mixer:
        # Finge que o mixer ainda não foi inicializado
        mock_mixer.get_init.return_value = False
        yield mock_mixer


def test_inicializacao_sucesso(mock_pygame):
    """Testa se o reprodutor arranca corretamente com o mixer disponível."""
    player = Reprodutor()

    assert player.mixer_available is True
    mock_pygame.init.assert_called_once()


def test_inicializacao_falha_hardware(mock_pygame):
    """Garante que o programa não crasha se não houver placa de som."""
    # Simulamos o pygame a atirar um erro ao tentar inicializar
    mock_pygame.init.side_effect = pygame.error("No audio device found")

    player = Reprodutor()
    assert player.mixer_available is False


def test_tocar_arquivo_inexistente(mock_pygame):
    """Garante que tentar reproduzir um ficheiro que não existe lança exceção."""
    player = Reprodutor()
    with pytest.raises(FileNotFoundError):
        player.tocar("musica_fantasma.mid")


@patch("src.reprodutor.os.path.exists", return_value=True)
def test_tocar_arquivo_sucesso(mock_exists, mock_pygame):
    """Testa o fluxo de reprodução de uma música."""
    player = Reprodutor()
    player.tocar("musica_valida.mid")

    assert player.current_file == "musica_valida.mid"
    assert player.is_playing is True
    assert player.is_paused is False

    # Verifica se os comandos corretos foram enviados ao pygame
    mock_pygame.music.load.assert_called_once_with("musica_valida.mid")
    mock_pygame.music.play.assert_called_once()


@patch("src.reprodutor.os.path.exists", return_value=True)
def test_pausar_e_despausar(mock_exists, mock_pygame):
    """Testa a alternância entre estado a tocar e pausado."""
    player = Reprodutor()
    player.tocar("musica.mid")

    # Aciona pausa
    player.pausar()
    assert player.is_paused is True
    mock_pygame.music.pause.assert_called_once()

    # Aciona despausar
    player.despausar()
    assert player.is_paused is False
    mock_pygame.music.unpause.assert_called_once()


@patch("src.reprodutor.os.path.exists", return_value=True)
def test_parar_musica(mock_exists, mock_pygame):
    """Testa parar a música e limpar os estados."""
    mock_pygame.music.get_busy.return_value = True
    player = Reprodutor()

    player.tocar("musica.mid")
    player.parar()

    assert player.is_playing is False
    assert player.is_paused is False
    mock_pygame.music.stop.assert_called_once()
