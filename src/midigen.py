from mido import Message, MidiFile, MidiTrack, MetaMessage

MICROSEGUNDOS_POR_MINUTO = 60000000  # 60 milhoes


class midigen:
    def __init__(self, volume, bpm, instrument, oitava, config_vozes=None):
        self.config_vozes = config_vozes or []
        self.res = MidiFile()
        self.tracks = [MidiTrack() for _ in range(4)]  # Criar 4 faixas
        for track in self.tracks:
            self.res.tracks.append(track)  # type: ignore

        self.volume = volume
        self.bpm = int(MICROSEGUNDOS_POR_MINUTO / bpm)

        # Amarra cada faixa ao seu próprio canal (channel=i) para suportar polifonia
        for i, track in enumerate(self.tracks):
            track.append(MetaMessage("set_tempo", tempo=self.bpm, time=0))  # type: ignore
            track.append(
                Message("program_change", program=instrument, time=0, channel=i)
            )  # type: ignore

        self.instrument = instrument
        self.oitava = oitava
        self.ticks = 480

    def add(self, nota, track_index=0, volume=None):
        if 0 <= track_index < len(self.tracks):
            track = self.tracks[track_index]
            vel = volume if volume is not None else self.volume

            # Força as notas a tocarem no canal exclusivo da voz
            track.append(
                Message("note_on", note=nota, velocity=vel, time=0, channel=track_index)
            )  # type: ignore
            track.append(
                Message(
                    "note_off",
                    note=nota,
                    velocity=vel,
                    time=self.ticks,
                    channel=track_index,
                )
            )  # type: ignore
        else:
            raise IndexError("Índice de faixa inválido")

    def set_instrument(self, instrument, track_index=None):
        self.instrument = instrument
        if track_index is not None and 0 <= track_index < len(self.tracks):
            track = self.tracks[track_index]

            if (
                len(track) == 2
                and self.config_vozes
                and track_index < len(self.config_vozes)
            ):
                atraso_inicial = self.config_vozes[track_index].delay
                for _ in range(atraso_inicial):
                    track.append(
                        Message(
                            "note_off",
                            note=0,
                            velocity=0,
                            time=self.ticks,
                            channel=track_index,
                        )  # type: ignore
                    )

            track.append(
                Message(
                    "program_change", program=instrument, time=0, channel=track_index
                )
            )  # type: ignore
        else:
            for i, track in enumerate(self.tracks):
                track.append(
                    Message("program_change", program=instrument, time=0, channel=i)
                )  # type: ignore

    def set_bpm(self, bpm):
        self.bpm = int(MICROSEGUNDOS_POR_MINUTO / bpm)
        for track in self.tracks:
            track.append(MetaMessage("set_tempo", tempo=self.bpm, time=0))  # type: ignore

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
        # Toda a lógica falha e os loops não utilizados foram removidos.
        # Isso corrige tanto o bug do "assovio" (instrumento 123)
        # quanto os erros "i is not accessed" e "type is unknown" no seu editor.
        self.res.save(name)
