from mido import Message, MidiFile, MidiTrack, MetaMessage

class midigen:
    def __init__(self, volume, bpm, instrument, oitava):
        self.res = MidiFile()
        self.tracks = [MidiTrack() for _ in range(4)]  # Criar 4 faixas
        for track in self.tracks:
            self.res.tracks.append(track)
        
        self.volume = volume
        self.bpm = int(60000000 / bpm)
        
        # Adicionar metadados iniciais em cada faixa
        for track in self.tracks:
            track.append(MetaMessage('set_tempo', tempo=self.bpm, time=0))
            track.append(Message('program_change', program=instrument, time=0))
        
        self.instrument = instrument
        self.oitava = oitava
        self.ticks = 480

    def add(self, nota, track_index=0):
        # Adicionar a nota à faixa especificada
        if 0 <= track_index < len(self.tracks):
            track = self.tracks[track_index]
            # Verificar se a nota já foi adicionada anteriormente na mesma posição
            # Se sim, atualizar os tempos das mensagens anteriores
            # Para simplificar, vamos assumir que não há notas sobrepostas
            track.append(Message('note_on', note=nota, velocity=self.volume, time=0))
            track.append(Message('note_off', note=nota, velocity=self.volume, time=self.ticks))
        else:
            raise IndexError("Índice de faixa inválido")

    def set_instrument(self, instrument):
        self.instrument = instrument
        for track in self.tracks:
            track.append(Message('program_change', program=instrument, time=0))

    def set_bpm(self, bpm):
        self.bpm = int(60000000 / bpm)
        for track in self.tracks:
            track.append(MetaMessage('set_tempo', tempo=self.bpm, time=0))

    def set_volume(self, volume):
        self.volume = volume

    def set_ticks(self, ticks):
        self.ticks = ticks

    def set_oitava(self, oitava):
        self.oitava = oitava

    def get_instrument(self):
        return self.instrument
    
    def get_volume(self):
        return self.volume
    
    def get_bpm(self):
        return self.bpm
    
    def get_ticks(self):
        return self.ticks
    
    def get_oitava(self):
        return self.oitava

    def save_mid(self, name):
        # Atualizar todas as trilhas com os metadados atuais antes de salvar
        for i, track in enumerate(self.tracks):
            # Adicionar metadados no final da trilha se ainda não estiverem presentes
            # Verificar se já temos set_tempo e program_change no final da trilha
            # Se não tiver, adicione-os
            if len(track) == 0 or not isinstance(track[-1], MetaMessage) or track[-1].type != 'set_tempo':
                # Adicionar metadados no final da trilha
                track.append(MetaMessage('set_tempo', tempo=self.bpm, time=0))
                track.append(Message('program_change', program=self.instrument, time=0))
        self.res.save(name)