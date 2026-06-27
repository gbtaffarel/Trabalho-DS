# Módulo de Interface Gráfica usando customtkinter
# FASE 2: Suporte a polifonia (múltiplas vozes estilo Fuga de Bach)

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import time
from interpretador import ConfigVoz
from reprodutor import Reprodutor


class VoiceConfigView(ctk.CTkFrame):
    """
    Componente visual responsável exclusivamente por construir a tabela de vozes
    e extrair as configurações (ConfigVoz) inseridas pelo utilizador.
    (Resolve o SRP e reduz o tamanho da Interface principal)
    """

    def __init__(self, master, max_vozes=4, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.max_vozes = max_vozes
        self.vozes_configs = []
        self._criar_tabela()

    def _criar_tabela(self):
        # Cabeçalhos da Tabela
        ctk.CTkLabel(self, text="Voz", width=60).grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkLabel(self, text="Instrumento (0-127)", width=120).grid(
            row=0, column=1, padx=2, pady=2
        )
        ctk.CTkLabel(self, text="Volume").grid(
            row=0, column=2, columnspan=2, padx=2, pady=2
        )
        ctk.CTkLabel(self, text="Oitava Base").grid(
            row=0, column=4, columnspan=2, padx=2, pady=2
        )
        ctk.CTkLabel(self, text="Atraso", width=60).grid(
            row=0, column=6, padx=2, pady=2
        )

        for i in range(self.max_vozes):
            ctk.CTkLabel(self, text=f"V{i}", width=60).grid(
                row=i + 1, column=0, padx=2, pady=5
            )

            spin_instrument = ctk.CTkEntry(self, width=120, placeholder_text="1")
            spin_instrument.insert(0, str(1 if i == 0 else 24 + i * 10))
            spin_instrument.grid(row=i + 1, column=1, padx=2, pady=5)

            slider_vol = ctk.CTkSlider(
                self, from_=0, to=127, width=80, number_of_steps=127
            )
            slider_vol.set(100 - i * 10)
            slider_vol.grid(row=i + 1, column=2, padx=(10, 2), pady=5)

            label_vol = ctk.CTkLabel(self, text=str(100 - i * 10), width=30)
            label_vol.grid(row=i + 1, column=3, padx=(2, 10), pady=5)
            slider_vol.configure(
                command=lambda v, lam=label_vol: lam.configure(text=str(int(v)))
            )

            slider_oitava = ctk.CTkSlider(
                self, from_=0, to=8, width=80, number_of_steps=8
            )
            slider_oitava.set(6 - i)
            slider_oitava.grid(row=i + 1, column=4, padx=(10, 2), pady=5)

            label_oit = ctk.CTkLabel(self, text=str(6 - i), width=30)
            label_oit.grid(row=i + 1, column=5, padx=(2, 10), pady=5)
            slider_oitava.configure(
                command=lambda o, lam=label_oit: lam.configure(text=str(int(o)))
            )

            spin_delay = ctk.CTkEntry(self, width=60, placeholder_text="0")
            spin_delay.insert(0, str(i * 2))
            spin_delay.grid(row=i + 1, column=6, padx=2, pady=5)

            self.vozes_configs.append(
                {
                    "instrumento": spin_instrument,
                    "volume": slider_vol,
                    "volume_label": label_vol,
                    "oitava": slider_oitava,
                    "oitava_label": label_oit,
                    "delay": spin_delay,
                }
            )

    def obter_configs(self) -> list[ConfigVoz]:
        vozes = []
        for _, config in enumerate(self.vozes_configs):
            try:
                instrumento = int(config["instrumento"].get() or 0)
                instrumento = max(0, min(127, instrumento))
            except ValueError:
                instrumento = 1

            try:
                delay = int(config["delay"].get() or 0)
                delay = max(0, delay)
            except ValueError:
                delay = 0

            vozes.append(
                ConfigVoz(
                    instrumento=instrumento,
                    volume=int(config["volume"].get()),
                    oitava_base=int(config["oitava"].get()),
                    delay=delay,
                )
            )
        return vozes

    def limpar_campos(self):
        for i, config in enumerate(self.vozes_configs):
            config["instrumento"].delete(0, "end")
            config["instrumento"].insert(0, str(1 if i == 0 else 24 + i * 10))
            config["volume"].set(100 - i * 10)
            config["volume_label"].configure(text=str(100 - i * 10))
            config["oitava"].set(6 - i)
            config["oitava_label"].configure(text=str(6 - i))
            config["delay"].delete(0, "end")
            config["delay"].insert(0, str(i * 2))


class Interface:
    """
    Coordenação principal da Interface Gráfica.
    Focada em orquestrar os componentes visuais, tratar eventos e repassar
    comandos para o serviço de domínio.
    """

    def __init__(self, gerador_callback=None):
        self.gerador_callback = gerador_callback

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.janela = ctk.CTk()
        self.janela.title("Gerador de Trilhas Sonoras - Fase 2")
        self.janela.geometry("900x1000")
        self.janela.resizable(True, True)

        self.player = Reprodutor()
        self.playing = False

        self._criar_layout()

    def _criar_layout(self):
        """Método principal dividido em sub-métodos focados e legíveis."""
        self._criar_cabecalho_e_container()
        self._criar_editor_texto(self.frame_principal)
        self._criar_configuracao_global(self.frame_principal)
        self._criar_tabela_vozes(self.frame_principal)
        self._criar_botoes_acao(self.frame_principal)
        self._criar_controles_reproducao(self.frame_principal)
        self._criar_status()

    def _criar_cabecalho_e_container(self):
        titulo = ctk.CTkLabel(
            self.janela,
            text="Gerador de Trilhas Sonoras MIDI",
            font=("Helvetica", 24, "bold"),
        )
        titulo.pack(pady=20)
        self.frame_principal = ctk.CTkFrame(self.janela)
        self.frame_principal.pack(padx=20, pady=10, fill="both", expand=True)

    def _criar_editor_texto(self, parent):
        frame_texto = ctk.CTkFrame(parent)
        frame_texto.pack(padx=10, pady=10, fill="both", expand=True)
        ctk.CTkLabel(
            frame_texto,
            text="Texto Musical (cada linha = uma voz independente):",
            font=("Helvetica", 12, "bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(
            frame_texto,
            text="Dica: Use [n] no início da linha para atraso de entrada (ex: [4]CCEAGA)",
            font=("Helvetica", 10),
            text_color="gray",
        ).pack(anchor="w", padx=10)

        container_texto = ctk.CTkFrame(frame_texto, fg_color="transparent")
        container_texto.pack(padx=10, pady=5, fill="both", expand=True)

        self.caixa_texto = ctk.CTkTextbox(
            container_texto, height=150, font=("Consolas", 12), wrap="word"
        )
        self.caixa_texto.pack(side="left", fill="both", expand=True)
        scrollbar = ctk.CTkScrollbar(container_texto, command=self.caixa_texto.yview)
        scrollbar.pack(side="right", fill="y")
        self.caixa_texto.configure(yscrollcommand=scrollbar.set)

    def _criar_configuracao_global(self, parent):
        frame_global = ctk.CTkFrame(parent)
        frame_global.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(
            frame_global, text="Configurações Globais:", font=("Helvetica", 12, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        frame_bpm = ctk.CTkFrame(frame_global, fg_color="transparent")
        frame_bpm.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame_bpm, text="BPM Inicial:").pack(side="left", padx=5)

        self.slider_bpm = ctk.CTkSlider(
            frame_bpm, from_=40, to=200, number_of_steps=160
        )
        self.slider_bpm.pack(side="left", padx=5, fill="x", expand=True)
        self.slider_bpm.set(120)
        self.label_bpm = ctk.CTkLabel(frame_bpm, text="120")
        self.label_bpm.pack(side="left", padx=5)
        self.slider_bpm.configure(
            command=lambda v: self.label_bpm.configure(text=str(int(v)))
        )

    def _criar_tabela_vozes(self, parent):
        frame_vozes = ctk.CTkFrame(parent)
        frame_vozes.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(
            frame_vozes, text="Configurações por Voz:", font=("Helvetica", 12, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        # Componentização visual: injetamos a nossa nova classe aqui
        self.tabela_vozes = VoiceConfigView(frame_vozes)
        self.tabela_vozes.pack(fill="x", padx=10, pady=2)

    def _criar_botoes_acao(self, parent):
        frame_botoes = ctk.CTkFrame(parent)
        frame_botoes.pack(padx=10, pady=15, fill="x")
        ctk.CTkButton(
            frame_botoes,
            text="📂 Carregar Ficheiro",
            command=self._carregar_arquivo,
            width=150,
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            frame_botoes, text="💾 Salvar Texto", command=self._salvar_texto, width=150
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            frame_botoes,
            text="Gerar MIDI",
            command=self._gerar_midi,
            width=150,
            fg_color="green",
            hover_color="darkgreen",
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            frame_botoes,
            text="Reset",
            command=self._limpar_tudo,
            width=150,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=5)

    def _criar_controles_reproducao(self, parent):
        frame_player = ctk.CTkFrame(parent)
        frame_player.pack(padx=10, pady=10, fill="x")
        ctk.CTkButton(
            frame_player,
            text="▶ Play",
            command=self._tocar_musica,
            width=100,
            fg_color="green",
            hover_color="darkgreen",
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            frame_player, text="⏸ Pausar", command=self._pausar_musica, width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            frame_player,
            text="⏹ Parar",
            command=self._parar_musica,
            width=100,
            fg_color="red",
            hover_color="darkred",
        ).pack(side="left", padx=5)

        self.progresso_frame = ctk.CTkFrame(frame_player)
        self.progresso_frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(
            self.progresso_frame, text="Progresso:", font=("Helvetica", 12)
        ).pack(side="left", padx=10)
        self.progresso_bar = ctk.CTkProgressBar(
            self.progresso_frame, width=400, height=20
        )
        self.progresso_bar.pack(side="left", padx=10, fill="x", expand=True)
        self.progresso_bar.set(0)

    def _criar_status(self):
        self.status_label = ctk.CTkLabel(
            self.janela,
            text="Pronto. Insira o texto musical e configure as vozes.",
            font=("Helvetica", 11),
            text_color="gray",
        )
        self.status_label.pack(pady=10)

    # --- Tratamento de Ficheiros e Ações ---

    def _carregar_arquivo(self):
        arquivo = filedialog.askopenfilename(
            title="Selecionar ficheiro de texto",
            filetypes=[("Ficheiros de texto", "*.txt"), ("Todos os ficheiros", "*.*")],
        )
        if arquivo:
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                self.caixa_texto.delete("1.0", "end")
                self.caixa_texto.insert("1.0", conteudo)
                self._atualizar_status(
                    f"Ficheiro carregado: {os.path.basename(arquivo)}"
                )
            except OSError as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível carregar o ficheiro:\n{str(e)}"
                )

    def _salvar_texto(self):
        arquivo = filedialog.asksaveasfilename(
            title="Salvar texto",
            defaultextension=".txt",
            filetypes=[("Ficheiros de texto", "*.txt"), ("Todos os ficheiros", "*.*")],
        )
        if arquivo:
            try:
                conteudo = self.caixa_texto.get("1.0", "end").strip()
                with open(arquivo, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                self._atualizar_status(f"Texto salvo em: {os.path.basename(arquivo)}")
            except OSError as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível salvar o ficheiro:\n{str(e)}"
                )

    def _limpar_tudo(self):
        self.caixa_texto.delete("1.0", "end")
        self.slider_bpm.set(120)
        self.label_bpm.configure(text="120")
        self.tabela_vozes.limpar_campos()
        self._atualizar_status("Campos limpos. Pronto para nova entrada.")

    def _gerar_midi(self):
        texto = self.caixa_texto.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Aviso", "Por favor, insira algum texto musical.")
            return False
        if not self.gerador_callback:
            messagebox.showinfo(
                "Info", "Modo de demonstração. Nenhum callback configurado."
            )
            return False

        # Aqui o código ficou extremamente limpo. A UI apenas pede à Tabela as configurações formatadas.
        dados = {
            "texto": texto,
            "bpm": int(self.slider_bpm.get()),
            "vozes": self.tabela_vozes.obter_configs(),
        }

        try:
            self._atualizar_status("A gerar MIDI...")
            self.janela.update_idletasks()
            resultado = self.gerador_callback(dados)
            if resultado:
                self._atualizar_status(f"MIDI gerado com sucesso: {resultado}")
                self.player.current_file = resultado
                return True
            else:
                self._atualizar_status("Erro na geração do MIDI.")
        except Exception as e:
            self._atualizar_status(f"Erro: {str(e)}")
            messagebox.showerror("Erro", f"Falha ao gerar MIDI:\n{str(e)}")
            return False

    def _atualizar_status(self, mensagem):
        self.status_label.configure(text=mensagem)

    # --- Controlo de Reprodução ---

    def _tocar_musica(self):
        if not self._gerar_midi():
            return
        try:
            self.player.tocar("saida_gerada.mid")
            self.playing = True
            self._atualizar_status("A reproduzir...")
            self._atualizar_progresso()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao reproduzir: {e}")

    def _pausar_musica(self):
        if self.player.esta_tocando():
            self.player.pausar()
            self.playing = False
            self._atualizar_status("Pausado")
        elif self.player.esta_pausado():
            self.player.despausar()
            self.playing = True
            self._atualizar_status("A reproduzir...")
            self._atualizar_progresso()
        else:
            self._tocar_musica()

    def _parar_musica(self):
        self.player.parar()
        self.playing = False
        self.progresso_bar.set(0)
        self._atualizar_status("Reprodução parada")

    def _atualizar_progresso(self):
        if self.playing:

            def update_progress():
                while self.playing and self.player.esta_ativo():
                    self.progresso_bar.set(min(self.progresso_bar.get() + 0.01, 1.0))
                    time.sleep(0.1)
                if not self.playing:
                    self.progresso_bar.set(0)

            threading.Thread(target=update_progress, daemon=True).start()

    def iniciar(self):
        self.janela.mainloop()


if __name__ == "__main__":
    from gerar_musica import GerarMusica

    def processar_midi(dados):
        gerador = GerarMusica()
        return gerador.executar(
            texto=dados["texto"], bpm=dados["bpm"], vozes=dados["vozes"]
        )

    app = Interface(gerador_callback=processar_midi)
    app.iniciar()
