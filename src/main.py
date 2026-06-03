import os
import sys
from reader import reader
from translator import translator
from midigen import midigen
from midi2audio import FluidSynth
from interpretador import Interpretador


def executar_cli():
    """Modo de Linha de Comando original."""
    print("=" * 40)
    print(" Gerador de Trilha Sonora - Modo CLI ")
    print("=" * 40)

    path = input("\nInsira o caminho do arquivo .txt (ex: natal.txt): ").strip()

    if not os.path.exists(path):
        print(
            f"\n[ERRO] Arquivo '{path}' não encontrado. Verifique o caminho e tente novamente."
        )
        return

    print("\nInicializando módulos...")

    try:
        texto = reader(path)
        texto.load()

        tradutor = translator()
        midi = midigen(volume=127, bpm=120, instrument=1, oitava=4)
        interpretador = Interpretador(gerador_midi=midi, tradutor=tradutor)

        print("Lendo e interpretando o arquivo...")

        linha_num = 0
        while not texto.is_empty():
            linha = texto.next_line()
            if linha is not None:
                interpretador.interpretar_linha(linha, linha_num % 4)
            linha_num += 1

    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um problema durante a interpretação: {e}")
        return

    arquivo_midi_saida = "saida_gerada.mid"
    arquivo_audio_saida = "saida_gerada.wav"
    soundfont_path = "FluidR3_GM.sf2"

    print("Gerando arquivo MIDI...")
    midi.save_mid(arquivo_midi_saida)
    print(f"[SUCESSO] Arquivo MIDI salvo como: {arquivo_midi_saida}")

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
            "A geração de áudio (.wav) foi ignorada. Você ainda pode ouvir o .mid gerado."
        )


def processar_midi_gui(dados):
    """
    Função Callback injetada na Interface Gráfica.
    Recebe o dicionário de dados da interface e processa o MIDI.
    """
    texto_reader = reader()
    texto_reader.load_from_string(dados["texto"])

    tradutor = translator()

    # Inicializa com a configuração da primeira voz
    voz_padrao = dados["vozes"][0]
    midi = midigen(
        volume=voz_padrao["volume"],
        bpm=dados["bpm"],
        instrument=voz_padrao["instrumento"],
        oitava=voz_padrao["oitava_base"],
    )

    interpretador = Interpretador(gerador_midi=midi, tradutor=tradutor)

    linha_num = 0
    while not texto_reader.is_empty():
        linha = texto_reader.next_line()
        if linha is not None:
            # Atualiza configurações se houver uma aba para essa voz
            if linha_num < len(dados["vozes"]):
                voz_atual = dados["vozes"][linha_num]
                midi.set_instrument(voz_atual["instrumento"])
                midi.set_volume(voz_atual["volume"])
                midi.set_oitava(voz_atual["oitava_base"])

            interpretador.interpretar_linha(linha, linha_num % 4)
        linha_num += 1

    arquivo_saida = "saida_gerada.mid"
    midi.save_mid(arquivo_saida)
    return arquivo_saida


def executar_gui():
    """Inicia o modo de Interface Gráfica."""
    print("Iniciando Interface Gráfica...")
    try:
        from interface import Interface

        app = Interface(gerador_callback=processar_midi_gui)
        app.iniciar()
    except ImportError as e:
        print(f"\n[ERRO] Não foi possível carregar a interface gráfica: {e}")
        print(
            "Certifique-se de que a biblioteca customtkinter está instalada ('pip install customtkinter')."
        )
        print("Voltando para o modo de Linha de Comando (CLI)...\n")
        executar_cli()


def main():
    """Função principal que roteia a escolha do usuário."""
    print("=" * 40)
    print(" Gerador de Trilha Sonora MIDI ")
    print("=" * 40)

    escolha = (
        input(
            "Deseja executar com Interface Gráfica (G) ou Linha de Comando (C)? [G/C]: "
        )
        .strip()
        .upper()
    )

    if escolha == "C":
        executar_cli()
    else:
        # Padrão é carregar a GUI se escolher 'G' ou apertar Enter vazio
        executar_gui()


if __name__ == "__main__":
    main()
