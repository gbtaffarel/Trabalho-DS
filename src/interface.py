# Módulo de Interface Gráfica usando customtkinter
# FASE 2: Suporte a polifonia (múltiplas vozes estilo Fuga de Bach)

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox


class Interface:
    """
    Interface gráfica para o Gerador de Trilhas Sonoras MIDI.
    Permite entrada de texto, configuração de múltiplas vozes e geração de MIDI.
    """

    def __init__(self, gerador_callback=None):
        """
        Inicializa a interface gráfica.

        Args:
            gerador_callback: Função callback que recebe os dados da interface
                             e executa a geração do MIDI.
        """
        self.gerador_callback = gerador_callback

        # Configuração do tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Janela principal
        self.janela = ctk.CTk()
        self.janela.title("Gerador de Trilhas Sonoras - Fase 2")
        self.janela.geometry("900x700")
        self.janela.resizable(True, True)

        # Estado das vozes
        self.vozes_configs = []
        self.max_vozes = 4

        self._criar_layout()

    def _criar_layout(self):
        """Cria os elementos da interface gráfica."""

        # === TÍTULO ===
        titulo = ctk.CTkLabel(
            self.janela,
            text="🎵 Gerador de Trilhas Sonoras MIDI 🎵",
            font=("Helvetica", 24, "bold")
        )
        titulo.pack(pady=20)

        subtitulo = ctk.CTkLabel(
            self.janela,
            text="Estilo Fuga de Bach - Múltiplas Vozes",
            font=("Helvetica", 14)
        )
        subtitulo.pack(pady=(0, 20))

        # === FRAME PRINCIPAL ===
        frame_principal = ctk.CTkFrame(self.janela)
        frame_principal.pack(padx=20, pady=10, fill="both", expand=True)

        # === ÁREA DE TEXTO (ENTRADA) ===
        frame_texto = ctk.CTkFrame(frame_principal)
        frame_texto.pack(padx=10, pady=10, fill="both", expand=True)

        label_texto = ctk.CTkLabel(
            frame_texto,
            text="Texto Musical (cada linha = uma voz independente):",
            font=("Helvetica", 12, "bold")
        )
        label_texto.pack(anchor="w", padx=10, pady=(10, 5))

        hint_texto = ctk.CTkLabel(
            frame_texto,
            text="Dica: Use [n] no início da linha para atraso de entrada (ex: [4]CEGA)",
            font=("Helvetica", 10),
            text_color="gray"
        )
        hint_texto.pack(anchor="w", padx=10)

        # Container para texto e scrollbar
        container_texto = ctk.CTkFrame(frame_texto, fg_color="transparent")
        container_texto.pack(padx=10, pady=5, fill="both", expand=True)

        self.caixa_texto = ctk.CTkTextbox(
            container_texto,
            height=150,
            font=("Consolas", 12),
            wrap="word"
        )
        self.caixa_texto.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(container_texto, command=self.caixa_texto.yview)
        scrollbar.pack(side="right", fill="y")
        self.caixa_texto.configure(yscrollcommand=scrollbar.set)

        # === CONFIGURAÇÕES GLOBAIS ===
        frame_global = ctk.CTkFrame(frame_principal)
        frame_global.pack(padx=10, pady=10, fill="x")

        label_global = ctk.CTkLabel(
            frame_global,
            text="Configurações Globais:",
            font=("Helvetica", 12, "bold")
        )
        label_global.pack(anchor="w", padx=10, pady=5)

        # BPM
        frame_bpm = ctk.CTkFrame(frame_global, fg_color="transparent")
        frame_bpm.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_bpm, text="BPM Inicial:").pack(side="left", padx=5)
        self.slider_bpm = ctk.CTkSlider(frame_bpm, from_=40, to=200, number_of_steps=160)
        self.slider_bpm.pack(side="left", padx=5, fill="x", expand=True)
        self.slider_bpm.set(120)
        self.label_bpm = ctk.CTkLabel(frame_bpm, text="120")
        self.label_bpm.pack(side="left", padx=5)
        self.slider_bpm.configure(command=self._atualizar_label_bpm)

        # === CONFIGURAÇÕES POR VOZ ===
        frame_vozes = ctk.CTkFrame(frame_principal)
        frame_vozes.pack(padx=10, pady=10, fill="x")

        label_vozes = ctk.CTkLabel(
            frame_vozes,
            text="Configurações por Voz:",
            font=("Helvetica", 12, "bold")
        )
        label_vozes.pack(anchor="w", padx=10, pady=5)

        # Headers
        frame_headers = ctk.CTkFrame(frame_vozes, fg_color="transparent")
        frame_headers.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(frame_headers, text="Voz", width=60).pack(side="left", padx=2)
        ctk.CTkLabel(frame_headers, text="Instrumento (0-127)", width=120).pack(side="left", padx=2)
        ctk.CTkLabel(frame_headers, text="Volume", width=80).pack(side="left", padx=2)
        ctk.CTkLabel(frame_headers, text="Oitava Base", width=80).pack(side="left", padx=2)
        ctk.CTkLabel(frame_headers, text="Atraso", width=60).pack(side="left", padx=2)

        # Configurações para cada voz
        self.frames_voz = []
        for i in range(self.max_vozes):
            frame_voz = ctk.CTkFrame(frame_vozes, fg_color="transparent")
            frame_voz.pack(fill="x", padx=10, pady=2)
            self.frames_voz.append(frame_voz)

            # Número da voz
            ctk.CTkLabel(frame_voz, text=f"V{i}", width=60).pack(side="left", padx=2)

            # Instrumento
            spin_instrument = ctk.CTkEntry(frame_voz, width=120, placeholder_text="1")
            spin_instrument.insert(0, str(1 if i == 0 else 24 + i * 10))
            spin_instrument.pack(side="left", padx=2)

            # Volume
            slider_vol = ctk.CTkSlider(frame_voz, from_=0, to=127, width=80, number_of_steps=127)
            slider_vol.set(100 - i * 10)  # V0=100, V1=90, etc.
            slider_vol.pack(side="left", padx=2)
            label_vol = ctk.CTkLabel(frame_voz, text=str(100 - i * 10), width=30)
            label_vol.pack(side="left", padx=2)
            slider_vol.configure(command=lambda v, l=label_vol: l.configure(text=str(int(v))))

            # Oitava base
            slider_oitava = ctk.CTkSlider(frame_voz, from_=0, to=8, width=80, number_of_steps=8)
            slider_oitava.set(6 - i)  # V0=6, V1=5, etc.
            slider_oitava.pack(side="left", padx=2)
            label_oit = ctk.CTkLabel(frame_voz, text=str(6 - i), width=30)
            label_oit.pack(side="left", padx=2)
            slider_oitava.configure(command=lambda o, l=label_oit: l.configure(text=str(int(o))))

            # Atraso inicial (beats)
            spin_delay = ctk.CTkEntry(frame_voz, width=60, placeholder_text="0")
            spin_delay.insert(0, str(i * 2))  # Staggered entry
            spin_delay.pack(side="left", padx=2)

            # Salvar referências
            self.vozes_configs.append({
                'instrumento': spin_instrument,
                'volume': slider_vol,
                'volume_label': label_vol,
                'oitava': slider_oitava,
                'oitava_label': label_oit,
                'delay': spin_delay
            })

        # === BOTÕES DE AÇÃO ===
        frame_botoes = ctk.CTkFrame(frame_principal)
        frame_botoes.pack(padx=10, pady=15, fill="x")

        self.btn_carregar = ctk.CTkButton(
            frame_botoes,
            text="📂 Carregar Arquivo",
            command=self._carregar_arquivo,
            width=150
        )
        self.btn_carregar.pack(side="left", padx=5)

        self.btn_salvar = ctk.CTkButton(
            frame_botoes,
            text="💾 Salvar Texto",
            command=self._salvar_texto,
            width=150
        )
        self.btn_salvar.pack(side="left", padx=5)

        self.btn_gerar = ctk.CTkButton(
            frame_botoes,
            text="🎵 Gerar MIDI",
            command=self._gerar_midi,
            width=150,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_gerar.pack(side="right", padx=5)

        self.btn_limpar = ctk.CTkButton(
            frame_botoes,
            text="🗑️ Limpar",
            command=self._limpar_tudo,
            width=150,
            fg_color="red",
            hover_color="darkred"
        )
        self.btn_limpar.pack(side="right", padx=5)

        # === BARRA DE STATUS ===
        self.status_label = ctk.CTkLabel(
            self.janela,
            text="Pronto. Insira o texto musical e configure as vozes.",
            font=("Helvetica", 11),
            text_color="gray"
        )
        self.status_label.pack(pady=10)

    def _atualizar_label_bpm(self, valor):
        """Atualiza o label do BPM quando o slider muda."""
        self.label_bpm.configure(text=str(int(valor)))

    def _carregar_arquivo(self):
        """Abre diálogo para carregar arquivo de texto."""
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo de texto",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if arquivo:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                self.caixa_texto.delete("1.0", "end")
                self.caixa_texto.insert("1.0", conteudo)
                self._atualizar_status(f"Arquivo carregado: {os.path.basename(arquivo)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível carregar o arquivo:\n{str(e)}")

    def _salvar_texto(self):
        """Salva o conteúdo da caixa de texto em um arquivo."""
        arquivo = filedialog.asksaveasfilename(
            title="Salvar texto",
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if arquivo:
            try:
                conteudo = self.caixa_texto.get("1.0", "end").strip()
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                self._atualizar_status(f"Texto salvo em: {os.path.basename(arquivo)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo:\n{str(e)}")

    def _limpar_tudo(self):
        """Limpa todos os campos da interface."""
        self.caixa_texto.delete("1.0", "end")
        self.slider_bpm.set(120)
        self.label_bpm.configure(text="120")

        # Resetar configurações das vozes
        for i, config in enumerate(self.vozes_configs):
            config['instrumento'].delete(0, "end")
            config['instrumento'].insert(0, str(1 if i == 0 else 24 + i * 10))
            config['volume'].set(100 - i * 10)
            config['volume_label'].configure(text=str(100 - i * 10))
            config['oitava'].set(6 - i)
            config['oitava_label'].configure(text=str(6 - i))
            config['delay'].delete(0, "end")
            config['delay'].insert(0, str(i * 2))

        self._atualizar_status("Campos limpos. Pronto para nova entrada.")

    def _gerar_midi(self):
        """Coleta os dados da interface e chama o callback do gerador."""
        texto = self.caixa_texto.get("1.0", "end").strip()

        if not texto:
            messagebox.showwarning("Aviso", "Por favor, insira algum texto musical.")
            return

        # Coletar configurações
        bpm = int(self.slider_bpm.get())

        vozes = []
        for i, config in enumerate(self.vozes_configs):
            try:
                instrumento = int(config['instrumento'].get() or 0)
                instrumento = max(0, min(127, instrumento))  # Clamping 0-127
            except ValueError:
                instrumento = 1

            volume = int(config['volume'].get())
            oitava = int(config['oitava'].get())

            try:
                delay = int(config['delay'].get() or 0)
                delay = max(0, delay)
            except ValueError:
                delay = 0

            vozes.append({
                'voz_id': i,
                'instrumento': instrumento,
                'volume': volume,
                'oitava_base': oitava,
                'delay': delay
            })

        dados = {
            'texto': texto,
            'bpm': bpm,
            'vozes': vozes
        }

        if self.gerador_callback:
            try:
                self._atualizar_status("Gerando MIDI...")
                self.janela.update_idletasks()

                resultado = self.gerador_callback(dados)

                if resultado:
                    self._atualizar_status(f"MIDI gerado com sucesso: {resultado}")
                    messagebox.showinfo("Sucesso", f"Arquivo MIDI gerado:\n{resultado}")
                else:
                    self._atualizar_status("Erro na geração do MIDI.")
            except Exception as e:
                self._atualizar_status(f"Erro: {str(e)}")
                messagebox.showerror("Erro", f"Falha ao gerar MIDI:\n{str(e)}")
        else:
            messagebox.showinfo("Info", "Modo de demonstração. Nenhum callback configurado.")

    def _atualizar_status(self, mensagem):
        """Atualiza a mensagem na barra de status."""
        self.status_label.configure(text=mensagem)

    def iniciar(self):
        """Inicia o loop principal da interface."""
        self.janela.mainloop()

    def obter_dados(self):
        """
        Retorna os dados atuais da interface sem fechar a janela.
        Útil para integração com outros módulos.

        Returns:
            dict: Dicionário com texto, BPM e configurações das vozes.
        """
        texto = self.caixa_texto.get("1.0", "end").strip()
        bpm = int(self.slider_bpm.get())

        vozes = []
        for i, config in enumerate(self.vozes_configs):
            try:
                instrumento = int(config['instrumento'].get() or 0)
            except ValueError:
                instrumento = 1

            vozes.append({
                'voz_id': i,
                'instrumento': max(0, min(127, instrumento)),
                'volume': int(config['volume'].get()),
                'oitava_base': int(config['oitava'].get()),
                'delay': int(config['delay'].get() or 0)
            })

        return {
            'texto': texto,
            'bpm': bpm,
            'vozes': vozes
        }


# Função de conveniência para criar e iniciar a interface
def criar_interface(gerador_callback=None):
    """
    Cria e retorna uma instância da interface.

    Args:
        gerador_callback: Função callback para geração do MIDI.

    Returns:
        Interface: Instância da classe Interface.
    """
    return Interface(gerador_callback)


def gerar_midi(dados):
    """
    Função que conecta a interface ao interpretador e gera o MIDI real.

    Args:
        dados: dict com 'texto', 'bpm' e 'vozes'

    Returns:
        str: Caminho do arquivo MIDI gerado
    """
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from reader import reader
    from translator import translator
    from midigen import midigen
    from interpretador import Interpretador
    from io import StringIO

    texto = dados['texto']
    bpm = dados['bpm']
    vozes = dados['vozes']

    arquivo_midi = "saida_gerada.mid"

    try:
        # Usa primeira voz para parâmetros principais
        voz_principal = vozes[0] if vozes else {}

        midi = midigen(
            volume=voz_principal.get('volume', 100),
            bpm=bpm,
            instrument=voz_principal.get('instrumento', 1),
            oitava=voz_principal.get('oitava_base', 4)
        )

        tradutor = translator()
        interpretador = Interpretador(gerador_midi=midi, tradutor=tradutor)

        # Reader simulado com StringIO para receber texto direto
        class ReaderSimulado:
            def __init__(self, texto):
                self.content = texto
                self.pos = 0

            def length(self):
                return len(self.content)

            def next(self):
                if self.pos < len(self.content):
                    c = self.content[self.pos]
                    self.pos += 1
                    return c
                return None

        reader_simulado = ReaderSimulado(texto)
        interpretador.interpretar(reader_simulado)

        midi.save_mid(arquivo_midi)
        return arquivo_midi

    except Exception as e:
        raise RuntimeError(f"Falha na geração: {e}")


if __name__ == "__main__":
    app = criar_interface(gerar_midi)
    app.iniciar()
