# Módulo de Interface Gráfica usando customtkinter
# FASE 2: Suporte a polifonia (múltiplas vozes estilo Fuga de Bach)

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import time
from reprodutor import Reprodutor


class Interface:
    """
    Interface gráfica para o Gerador de Trilhas Sonoras MIDI.
    Permite entrada de texto, configuração de múltiplas vozes e geração de MIDI.
    """

    def __init__(self, gerador_callback=None):
        self.gerador_callback = gerador_callback

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.janela = ctk.CTk()
        self.janela.title("Gerador de Trilhas Sonoras - Fase 2")
        self.janela.geometry("900x1000")
        self.janela.resizable(True, True)

        self.vozes_configs = []
        self.max_vozes = 4

        self.player = Reprodutor()
        self.player_thread = None
        self.playing = False

        self._criar_layout()

    def _criar_layout(self):
        titulo = ctk.CTkLabel(
            self.janela,
            text="Gerador de Trilhas Sonoras MIDI",
            font=("Helvetica", 24, "bold"),
        )
        titulo.pack(pady=20)

        frame_principal = ctk.CTkFrame(self.janela)
        frame_principal.pack(padx=20, pady=10, fill="both", expand=True)

        # Área de texto
        frame_texto = ctk.CTkFrame(frame_principal)
        frame_texto.pack(padx=10, pady=10, fill="both", expand=True)

        label_texto = ctk.CTkLabel(
            frame_texto,
            text="Texto Musical (cada linha = uma voz independente):",
            font=("Helvetica", 12, "bold"),
        )
        label_texto.pack(anchor="w", padx=10, pady=(10, 5))

        hint_texto = ctk.CTkLabel(
            frame_texto,
            text="Dica: Use [n] no início da linha para atraso de entrada (ex: [4]CCEAGA)",
            font=("Helvetica", 10),
            text_color="gray",
        )
        hint_texto.pack(anchor="w", padx=10)

        container_texto = ctk.CTkFrame(frame_texto, fg_color="transparent")
        container_texto.pack(padx=10, pady=5, fill="both", expand=True)

        self.caixa_texto = ctk.CTkTextbox(
            container_texto, height=150, font=("Consolas", 12), wrap="word"
        )
        self.caixa_texto.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(container_texto, command=self.caixa_texto.yview)
        scrollbar.pack(side="right", fill="y")
        self.caixa_texto.configure(yscrollcommand=scrollbar.set)

        # Configurações globais
        frame_global = ctk.CTkFrame(frame_principal)
        frame_global.pack(padx=10, pady=10, fill="x")

        label_global = ctk.CTkLabel(
            frame_global, text="Configurações Globais:", font=("Helvetica", 12, "bold")
        )
        label_global.pack(anchor="w", padx=10, pady=5)

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
        self.slider_bpm.configure(command=self._atualizar_label_bpm)

        # Configurações por voz
        frame_vozes = ctk.CTkFrame(frame_principal)
        frame_vozes.pack(padx=10, pady=10, fill="x")

        label_vozes = ctk.CTkLabel(
            frame_vozes, text="Configurações por Voz:", font=("Helvetica", 12, "bold")
        )
        label_vozes.pack(anchor="w", padx=10, pady=5)

        # Usamos um sub-frame transparente que utilizará o sistema GRID (Grade/Tabela)
        frame_tabela = ctk.CTkFrame(frame_vozes, fg_color="transparent")
        frame_tabela.pack(fill="x", padx=10, pady=2)

        # Cabeçalhos da Tabela (Linha 0)
        # Note o columnspan=2 em Volume e Oitava Base para mesclar células (Slider + Valor)
        ctk.CTkLabel(frame_tabela, text="Voz", width=60).grid(
            row=0, column=0, padx=2, pady=2
        )
        ctk.CTkLabel(frame_tabela, text="Instrumento (0-127)", width=120).grid(
            row=0, column=1, padx=2, pady=2
        )
        ctk.CTkLabel(frame_tabela, text="Volume").grid(
            row=0, column=2, columnspan=2, padx=2, pady=2
        )
        ctk.CTkLabel(frame_tabela, text="Oitava Base").grid(
            row=0, column=4, columnspan=2, padx=2, pady=2
        )
        ctk.CTkLabel(frame_tabela, text="Atraso", width=60).grid(
            row=0, column=6, padx=2, pady=2
        )

        self.vozes_configs = []
        for i in range(self.max_vozes):
            # Coluna 0: Nome da Voz
            ctk.CTkLabel(frame_tabela, text=f"V{i}", width=60).grid(
                row=i + 1, column=0, padx=2, pady=5
            )

            # Coluna 1: Instrumento
            spin_instrument = ctk.CTkEntry(
                frame_tabela, width=120, placeholder_text="1"
            )
            spin_instrument.insert(0, str(1 if i == 0 else 24 + i * 10))
            spin_instrument.grid(row=i + 1, column=1, padx=2, pady=5)

            # Coluna 2: Slider de Volume
            slider_vol = ctk.CTkSlider(
                frame_tabela, from_=0, to=127, width=80, number_of_steps=127
            )
            slider_vol.set(100 - i * 10)
            slider_vol.grid(row=i + 1, column=2, padx=(10, 2), pady=5)

            # Coluna 3: Label Numérico de Volume
            label_vol = ctk.CTkLabel(frame_tabela, text=str(100 - i * 10), width=30)
            label_vol.grid(row=i + 1, column=3, padx=(2, 10), pady=5)
            slider_vol.configure(
                command=lambda v, lam=label_vol: lam.configure(text=str(int(v)))
            )

            # Coluna 4: Slider de Oitava Base
            slider_oitava = ctk.CTkSlider(
                frame_tabela, from_=0, to=8, width=80, number_of_steps=8
            )
            slider_oitava.set(6 - i)
            slider_oitava.grid(row=i + 1, column=4, padx=(10, 2), pady=5)

            # Coluna 5: Label Numérico de Oitava
            label_oit = ctk.CTkLabel(frame_tabela, text=str(6 - i), width=30)
            label_oit.grid(row=i + 1, column=5, padx=(2, 10), pady=5)
            slider_oitava.configure(
                command=lambda o, lam=label_oit: lam.configure(text=str(int(o)))
            )

            # Coluna 6: Atraso
            spin_delay = ctk.CTkEntry(frame_tabela, width=60, placeholder_text="0")
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

        # Botões de ação
        frame_botoes = ctk.CTkFrame(frame_principal)
        frame_botoes.pack(padx=10, pady=15, fill="x")

        self.btn_carregar = ctk.CTkButton(
            frame_botoes,
            text="📂 Carregar Arquivo",
            command=self._carregar_arquivo,
            width=150,
        )
        self.btn_carregar.pack(side="right", padx=5)

        self.btn_salvar = ctk.CTkButton(
            frame_botoes, text="💾 Salvar Texto", command=self._salvar_texto, width=150
        )
        self.btn_salvar.pack(side="right", padx=5)

        self.btn_gerar = ctk.CTkButton(
            frame_botoes,
            text="Gerar MIDI",
            command=self._gerar_midi,
            width=150,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.btn_gerar.pack(side="left", padx=5)

        self.btn_limpar = ctk.CTkButton(
            frame_botoes,
            text="Reset",
            command=self._limpar_tudo,
            width=150,
            fg_color="red",
            hover_color="darkred",
        )
        self.btn_limpar.pack(side="left", padx=5)

        # Player controls
        frame_player = ctk.CTkFrame(frame_principal)
        frame_player.pack(padx=10, pady=10, fill="x")

        self.btn_play = ctk.CTkButton(
            frame_player,
            text="▶ Play",
            command=self._tocar_musica,
            width=100,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.btn_play.pack(side="left", padx=5)

        self.btn_pause = ctk.CTkButton(
            frame_player, text="⏸ Pausar", command=self._pausar_musica, width=100
        )
        self.btn_pause.pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(
            frame_player,
            text="⏹ Parar",
            command=self._parar_musica,
            width=100,
            fg_color="red",
            hover_color="darkred",
        )
        self.btn_stop.pack(side="left", padx=5)

        self.progresso_frame = ctk.CTkFrame(frame_player)
        self.progresso_frame.pack(padx=10, pady=10, fill="x")

        self.progresso_label = ctk.CTkLabel(
            self.progresso_frame, text="Progresso:", font=("Helvetica", 12)
        )
        self.progresso_label.pack(side="left", padx=10)

        self.progresso_bar = ctk.CTkProgressBar(
            self.progresso_frame, width=400, height=20
        )
        self.progresso_bar.pack(side="left", padx=10, fill="x", expand=True)
        self.progresso_bar.set(0)

        # Barra de status (única)
        self.status_label = ctk.CTkLabel(
            self.janela,
            text="Pronto. Insira o texto musical e configure as vozes.",
            font=("Helvetica", 11),
            text_color="gray",
        )
        self.status_label.pack(pady=10)

    def _atualizar_label_bpm(self, valor):
        self.label_bpm.configure(text=str(int(valor)))

    def _carregar_arquivo(self):
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo de texto",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if arquivo:
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                self.caixa_texto.delete("1.0", "end")
                self.caixa_texto.insert("1.0", conteudo)
                self._atualizar_status(
                    f"Arquivo carregado: {os.path.basename(arquivo)}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível carregar o arquivo:\n{str(e)}"
                )

    def _salvar_texto(self):
        arquivo = filedialog.asksaveasfilename(
            title="Salvar texto",
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if arquivo:
            try:
                conteudo = self.caixa_texto.get("1.0", "end").strip()
                with open(arquivo, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                self._atualizar_status(f"Texto salvo em: {os.path.basename(arquivo)}")
            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível salvar o arquivo:\n{str(e)}"
                )

    def _limpar_tudo(self):
        self.caixa_texto.delete("1.0", "end")
        self.slider_bpm.set(120)
        self.label_bpm.configure(text="120")

        for i, config in enumerate(self.vozes_configs):
            config["instrumento"].delete(0, "end")
            config["instrumento"].insert(0, str(1 if i == 0 else 24 + i * 10))
            config["volume"].set(100 - i * 10)
            config["volume_label"].configure(text=str(100 - i * 10))
            config["oitava"].set(6 - i)
            config["oitava_label"].configure(text=str(6 - i))
            config["delay"].delete(0, "end")
            config["delay"].insert(0, str(i * 2))

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

        bpm = int(self.slider_bpm.get())

        vozes = []
        for i, config in enumerate(self.vozes_configs):
            try:
                instrumento = int(config["instrumento"].get() or 0)
                instrumento = max(0, min(127, instrumento))
            except ValueError:
                instrumento = 1

            volume = int(config["volume"].get())
            oitava = int(config["oitava"].get())

            try:
                delay = int(config["delay"].get() or 0)
                delay = max(0, delay)
            except ValueError:
                delay = 0

            vozes.append(
                {
                    "voz_id": i,
                    "instrumento": instrumento,
                    "volume": volume,
                    "oitava_base": oitava,
                    "delay": delay,
                }
            )

        dados = {"texto": texto, "bpm": bpm, "vozes": vozes}

        try:
            self._atualizar_status("Gerando MIDI...")
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

    def _tocar_musica(self):

        # Gera o MIDI primeiro. Se falhar, interrompe o fluxo aqui.
        if not self._gerar_midi():
            return

        try:
            self.player.tocar("saida_gerada.mid")
            self.playing = True
            self._atualizar_status("Reproduzindo...")
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
            self._atualizar_status("Reproduzindo...")
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

    def obter_dados(self):
        texto = self.caixa_texto.get("1.0", "end").strip()
        bpm = int(self.slider_bpm.get())

        vozes = []
        for i, config in enumerate(self.vozes_configs):
            try:
                instrumento = int(config["instrumento"].get() or 0)
            except ValueError:
                instrumento = 1

            vozes.append(
                {
                    "voz_id": i,
                    "instrumento": max(0, min(127, instrumento)),
                    "volume": int(config["volume"].get()),
                    "oitava_base": int(config["oitava"].get()),
                    "delay": int(config["delay"].get() or 0),
                }
            )

        return {"texto": texto, "bpm": bpm, "vozes": vozes}


if __name__ == "__main__":
    from reader import reader
    from translator import translator
    from midigen import midigen
    from interpretador import Interpretador

    def processar_midi(dados):
        """
        Função que recebe os dados da GUI e usa as classes do backend para gerar o MIDI.
        """
        # 1. Carrega o texto usando o seu reader
        texto_reader = reader()
        texto_reader.load_from_string(dados["texto"])

        # 2. Inicializa o tradutor
        tradutor = translator()

        # 3. Pega as configurações da Voz 0 para a inicialização padrão
        voz_padrao = dados["vozes"][0]
        midi = midigen(
            volume=voz_padrao["volume"],
            bpm=dados["bpm"],
            instrument=voz_padrao["instrumento"],
            oitava=voz_padrao["oitava_base"],
        )

        # 4. Inicializa o interpretador
        interpretador = Interpretador(gerador_midi=midi, tradutor=tradutor)

        # 5. Processa linha por linha (uma para cada faixa/voz)
        linha_num = 0
        while not texto_reader.is_empty():
            linha = texto_reader.next_line()
            if linha is not None:
                # Se houver configuração específica para essa voz na interface, atualiza o MIDI
                if linha_num < len(dados["vozes"]):
                    voz_atual = dados["vozes"][linha_num]
                    midi.set_instrument(voz_atual["instrumento"])
                    midi.set_volume(voz_atual["volume"])
                    midi.set_oitava(voz_atual["oitava_base"])

                # Interpreta a linha atual na respectiva track
                interpretador.interpretar_linha(linha, linha_num % 4)
            linha_num += 1

        # 6. Salva o arquivo e retorna o nome para a interface saber que deu certo
        arquivo_saida = "saida_gerada.mid"
        midi.save_mid(arquivo_saida)
        return arquivo_saida

    app = Interface(gerador_callback=processar_midi)
    app.iniciar()
