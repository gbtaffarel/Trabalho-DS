import pygame
import time
import os
import sys

if sys.platform.startswith("linux"):
    os.environ["SDL_SOUNDFONTS"] = "/usr/share/soundfonts/FluidR3_GM.sf2"


class Reprodutor:
    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.mixer_available = False

        self._inicializar_mixer()

    def _inicializar_mixer(self):
        """Tenta inicializar o mixer isoladamente."""
        try:
            # Evita reinicializar se já estiver rodando
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100)
            self.mixer_available = True
            print("Mixer inicializado com sucesso.")
        except pygame.error as e:  # <-- Usamos o erro específico do pygame
            self.mixer_available = False
            print(
                f"Aviso: pygame mixer não disponível. Funções de áudio desativadas. Detalhes: {e}"
            )
        except (
            OSError
        ) as e:  # <-- Tratamos falhas do sistema operativo (ex: drivers de áudio)
            self.mixer_available = False
            print(
                f"Aviso: Falha no sistema operativo ao aceder ao áudio. Detalhes: {e}"
            )

    def tocar(self, arquivo_midi):
        if not os.path.exists(arquivo_midi):
            raise FileNotFoundError(f"Arquivo MIDI não encontrado: {arquivo_midi}")

        if not self.mixer_available:
            print("Mixer não disponível. Não é possível reproduzir áudio.")
            return

        try:
            pygame.mixer.music.load(arquivo_midi)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
        except pygame.error as e:
            # O 'from e' encadeia a exceção, preservando a causa original para depuração
            raise RuntimeError(
                f"Falha interna do pygame ao tentar reproduzir '{arquivo_midi}'"
            ) from e

    def pausar(self):
        if not self.mixer_available:
            return
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def despausar(self):
        if not self.mixer_available:
            return
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def parar(self):
        if not self.mixer_available:
            return
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def esta_tocando(self):
        if not self.mixer_available:
            return False
        return self.is_playing and not self.is_paused

    def esta_pausado(self):
        if not self.mixer_available:
            return False
        return self.is_paused

    def esta_ativo(self):
        if not self.mixer_available:
            return False
        return self.is_playing

    def get_posicao(self):
        if not self.mixer_available:
            return 0.0
        if self.is_playing:
            return pygame.mixer.music.get_pos() / 1000.0
        return 0.0


# Teste unitario
if __name__ == "__main__":
    print("\n--- Iniciando Teste Isolado do Reprodutor (Pygame Nativo) ---")

    player = Reprodutor()
    caminho_arquivo = os.path.join("..", "saida_gerada.mid")

    if os.path.exists(caminho_arquivo):
        print(f"Tocando o ficheiro: {caminho_arquivo}")
        player.tocar(caminho_arquivo)

        try:
            # O get_busy() avisa quando a música acaba naturalmente
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)  # Verifica a cada 0.1s para responder mais rápido
        except KeyboardInterrupt:
            print("\nReprodução interrompida pelo utilizador.")
        finally:
            # Garante que o estado interno do reprodutor é limpo
            player.parar()

            # DESLIGA as threads de áudio do Pygame para liberar o sistema
            if pygame.mixer.get_init():
                pygame.mixer.quit()

            print("Teste finalizado com sucesso.")
            sys.exit(0)  # Força o Python a fechar o programa corretamente
    else:
        print(f"ERRO: Ficheiro não encontrado em '{caminho_arquivo}'")
        sys.exit(1)
