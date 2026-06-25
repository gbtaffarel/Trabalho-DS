import os
from interface import Interface
from interpretador import ConfigVoz
from gerar_musica import GerarMusica


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
        # No modo CLI original, o texto vinha de um ficheiro
        with open(path, "r", encoding="utf-8") as f:
            texto_bruto = f.read()

        # O CLI usava valores fixos por padrão
        vozes_cli = [ConfigVoz(instrumento=1, volume=127, oitava_base=4, delay=0)]

        gerador = GerarMusica()
        arquivo_midi_saida = "saida_gerada.mid"

        print("Lendo e interpretando o arquivo...")
        gerador.executar(
            texto=texto_bruto,
            bpm=120,
            vozes=vozes_cli,
            arquivo_saida=arquivo_midi_saida,
        )

    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um problema durante a interpretação: {e}")
        return


def processar_midi_gui(dados):
    """
    Função Callback injetada na Interface Gráfica.
    Recebe o dicionário de dados da interface e processa o MIDI.
    """
    gerador = GerarMusica()
    return gerador.executar(
        texto=dados["texto"],
        bpm=dados["bpm"],
        vozes=dados["vozes"],
        arquivo_saida="saida_gerada.mid",
    )


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


if __name__ == "__main__":

    def processar_midi(dados):
        """
        Função que recebe os dados da GUI e usa o serviço central para gerar o MIDI.
        """
        gerador = GerarMusica()
        return gerador.executar(
            texto=dados["texto"], bpm=dados["bpm"], vozes=dados["vozes"]
        )

    app = Interface(gerador_callback=processar_midi)
    app.iniciar()
