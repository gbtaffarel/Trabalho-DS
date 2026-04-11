from mido import Message, MidiFile, MidiTrack, MetaMessage
class midigen:

    def __init__(self, volume, bpm, instrument, oitava):
        self.res = MidiFile();
        self.track = MidiTrack();
        self.res.tracks.append(self.track);

        self.volume = volume
        self.bpm = int(60000000 / bpm)
        self.track.append(MetaMessage('set_tempo', tempo=self.bpm))
        self.instrument = instrument
        self.track.append(Message('program_change', program=self.instrument, time=0))
        self.oitava = oitava
        self.ticks = 480

    def add(self, nota):
        self.track.append(Message('note_on', note=nota, velocity=self.volume, time=0))
        self.track.append(Message('note_off', note=nota, velocity=self.volume, time=self.ticks))
    
    def set_instrument(self, instrument):
        self.instrument = instrument
        self.track.append(Message('program_change', program=instrument, time=0))

    def set_bpm(self, bpm):
        self.bpm = int(60000000 / bpm)
        self.track.append(MetaMessage('set_tempo', tempo=self.bpm))

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
        self.res.save(name)