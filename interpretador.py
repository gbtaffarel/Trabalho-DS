# interpretador.py


class Interpretador:
    def __init__(self, gerador_midi, tradutor):
        """
        Aplica o princípio de Inversão de Dependência (SOLID).
        A classe recebe os objetos prontos em vez de instanciá-los internamente.
        """
        self.gerador_midi = gerador_midi
        self.tradutor = tradutor

        # Estado Musical (Poderia ser um TAD "EstadoMusical" separado,
        # conforme você idealizou no README)
        self.standard_note = 60
        self.last_note = False
        self.last_note_value = 0

    def interpretar(self, texto_reader):
        """
        Itera sobre a entrada de texto e delega a aplicação das regras.
        """
        for _ in range(texto_reader.length()):
            caractere = texto_reader.next()
            if caractere is None:
                break

            instrucao = self.tradutor.translate(caractere)
            self._aplicar_regras(instrucao)

    def _aplicar_regras(self, instrucao):
        """
        Método privado que traduz a instrução em ações reais no MIDI.
        """
        # Se a instrução for um inteiro (Nota Musical)
        if isinstance(instrucao, int):
            nota_real = instrucao + (self.gerador_midi.get_oitava() + 1) * 12
            self.gerador_midi.add(nota_real)

            # Atualiza o estado
            self.last_note_value = nota_real
            self.last_note = True
            return

        # Se a instrução for um comando/ação (Lista)
        comando = instrucao[0]

        if comando == "volume":
            valor = instrucao[1]
            if valor == 0:
                self._tocar_silencio()
            elif valor == 2:
                self._dobrar_volume()

        elif comando == "instrument":
            self.gerador_midi.set_instrument(instrucao[1])

        elif comando == "instrument+":
            # BUG CORRIGIDO: get_instrument() com parênteses
            novo_inst = instrucao[1] + self.gerador_midi.get_instrument()
            if novo_inst > 127:
                novo_inst = 127  # Ajustado para o limite máximo
            self.gerador_midi.set_instrument(novo_inst)

        elif comando == "consonant":
            if self.last_note:
                self.gerador_midi.add(self.last_note_value)
            else:
                self._tocar_silencio()

        elif comando == "oitava":
            oitava_atual = self.gerador_midi.get_oitava()
            if oitava_atual + 1 <= 9:
                self.gerador_midi.set_oitava(oitava_atual + 1)

        # Reseta o estado da última nota se o comando não repetiu a nota
        if comando != "consonant":
            self.last_note = False

    # --- Métodos auxiliares privados (Clean Code) ---

    def _tocar_silencio(self):
        """Simula um silêncio zerando o volume temporariamente."""
        vol_atual = self.gerador_midi.get_volume()
        self.gerador_midi.set_volume(0)
        self.gerador_midi.add(self.standard_note)
        self.gerador_midi.set_volume(vol_atual)

    def _dobrar_volume(self):
        """Dobra o volume respeitando o limite do MIDI (127)."""
        vol_atual = self.gerador_midi.get_volume()
        novo_vol = vol_atual * 2
        # Correção com base no Enunciado Fase 1 (se exceder, recebe o máximo)
        if novo_vol > 127:
            novo_vol = 127
        self.gerador_midi.set_volume(novo_vol)
