import pygame
import os
import time

# Tentar inicializar o mixer, mas lidar com erros
try:
    pygame.mixer.init(frequency=44100)
    MIXER_AVAILABLE = True
    print("Mixer inicializado com sucesso.")
except Exception as e:
    MIXER_AVAILABLE = False
    print(f"Aviso: pygame mixer não disponível. Funções de reprodução desativadas. Erro: {e}")


class Reprodutor:
    def __init__(self):
        self.current_file = None
        self.is_playing = False
        self.is_paused = False

    def tocar(self, arquivo_midi):
        if not os.path.exists(arquivo_midi):
            raise FileNotFoundError(f"Arquivo MIDI não encontrado: {arquivo_midi}")

        if not MIXER_AVAILABLE:
            print("Mixer não disponível. Não é possível reproduzir áudio.")
            # Tentar tocar com timidity ou outro player do sistema
            return

        try:
            pygame.mixer.music.load(arquivo_midi)
            pygame.mixer.music.play()
            self.current_file = arquivo_midi
            self.is_playing = True
            self.is_paused = False
        except Exception as e:
            raise RuntimeError(f"Erro ao reproduzir: {e}")

    def pausar(self):
        if not MIXER_AVAILABLE:
            print("Mixer não disponível. Não é possível pausar.")
            return
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def despausar(self):
        if not MIXER_AVAILABLE:
            print("Mixer não disponível. Não é possível despausar.")
            return
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def parar(self):
        if not MIXER_AVAILABLE:
            print("Mixer não disponível. Não é possível parar.")
            return
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def esta_tocando(self):
        if not MIXER_AVAILABLE:
            return False
        return self.is_playing and not self.is_paused

    def esta_pausado(self):
        if not MIXER_AVAILABLE:
            return False
        return self.is_paused

    def esta_ativo(self):
        if not MIXER_AVAILABLE:
            return False
        return self.is_playing

    def get_posicao(self):
        if not MIXER_AVAILABLE:
            return 0.0
        if self.is_playing:
            return pygame.mixer.music.get_pos() / 1000.0
        return 0.0
        if self.is_playing:
            return pygame.mixer.music.get_pos() / 1000.0
        return 0.0