import os
from reader import reader
from translator import translator
from midigen import midigen
from midi2audio import FluidSynth
from interpretador import Interpretador


def main():
    print("=" * 40)
    print(" Gerador de Trilha Sonora - Fase 1/2 ")
    print("=" * 40)

    # 1. Entrada de Dados (Pode ser substituído pela UI do customtkinter no futuro)
    path = input("\nInsira o caminho do arquivo .txt (ex: natal.txt): ").strip()

    if not os.path.exists(path):
        print(
            f"\n[ERRO] Arquivo '{path}' não encontrado. Verifique o caminho e tente novamente."
        )
        return

    print("\nInicializando módulos...")

    # 2. Instanciação e Injeção de Dependências
    try:
        texto = reader(path)
        texto.load()

        tradutor = translator()
        # Inicializando o gerador MIDI com os presets padrão (volume max, 120 BPM, Piano, 4ª Oitava)
        midi = midigen(volume=127, bpm=120, instrument=1, oitava=4)

        # Injetamos o gerador e o tradutor dentro do interpretador (Dependency Inversion Principle)
        interpretador = Interpretador(gerador_midi=midi, tradutor=tradutor)

        print("Lendo e interpretando o arquivo...")

        # 3. Execução da Regra de Negócio
        interpretador.interpretar(texto)

    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um problema durante a interpretação: {e}")
        return

    # 4. Saída e Salvamento de Dados
    arquivo_midi_saida = "saida_gerada.mid"
    arquivo_audio_saida = "saida_gerada.wav"
    soundfont_path = "FluidR3_GM.sf2"

    print("Gerando arquivo MIDI...")
    midi.save_mid(arquivo_midi_saida)
    print(f"[SUCESSO] Arquivo MIDI salvo como: {arquivo_midi_saida}")

    # Conversão opcional para WAV, apenas se o SoundFont estiver presente
    if os.path.exists(soundfont_path):
        print("Convertendo MIDI para áudio (WAV)...")
        try:
            fs = FluidSynth(soundfont_path)
            fs.midi_to_audio(arquivo_midi_saida, arquivo_audio_saida)
            print(f"[SUCESSO] Áudio WAV salvo como: {arquivo_audio_saida}")
        except Exception as e:
            print(f"\n[AVISO] Falha ao converter para WAV: {e}")
    else:
        print(f"\n[AVISO] Soundfont '{soundfont_path}' não encontrado no diretório.")
        print(
            "A geração de áudio (.wav) foi ignorada. Você ainda pode ouvir o .mid gerado em qualquer player."
        )


if __name__ == "__main__":
    # Esse bloco __main__ garante que o código só rode se o arquivo for executado diretamente,
    # prevenindo execuções acidentais caso main.py seja importado em scripts de teste.
    main()
