from dataclasses import dataclass
from mido import Message, MidiFile, MidiTrack, MetaMessage

MICROSEGUNDOS_POR_MINUTO = 60000000


@dataclass
class MidiConfig:
    volume: int = 100
    bpm: int = 120
    instrument: int = 0
    oitava: int = 4
    config_vozes: list = None

    def __post_init__(self):
        if self.config_vozes is None:
            self.config_vozes = []


class MidiGen:
    def __init__(self, volume=100, bpm=120, instrument=0, oitava=4, config_vozes=None):
        """
        Args:
            volume: Volume padrão (0-127)
            bpm: Beats por minuto (deve ser > 0)
            instrument: Instrumento MIDI (0-127)
            oitava: Parâmetro aceito por compatibilidade (não utilizado)
            config_vozes: Lista de configurações de vozes
        """
        if bpm <= 0:
            raise ValueError("BPM deve ser maior que zero")
        if not isinstance(volume, MidiConfig) and not 0 <= volume <= 127:
            raise ValueError("Volume deve estar entre 0 e 127")
        if isinstance(volume, MidiConfig):
            config = volume
            self.volume = config.volume
            self.bpm = int(MICROSEGUNDOS_POR_MINUTO / config.bpm)
            self.instrument = config.instrument
            self.config_vozes = config.config_vozes or []
        else:
            self.volume = volume
            self.bpm = int(MICROSEGUNDOS_POR_MINUTO / bpm)
            self.instrument = instrument
            self.config_vozes = config_vozes or []

        self.res = MidiFile()
        self.tracks = [MidiTrack() for _ in range(4)]
        for track in self.tracks:
            self.res.tracks.append(track)

        for i, track in enumerate(self.tracks):
            track.append(MetaMessage("set_tempo", tempo=self.bpm, time=0))
            track.append(
                Message("program_change", program=self.instrument, time=0, channel=i)
            )

        self.ticks = 480

    def add(self, nota, track_index=0, volume=None):
        if 0 <= track_index < len(self.tracks):
            track = self.tracks[track_index]
            vel = volume if volume is not None else self.volume

            # Força as notas a tocarem no canal exclusivo da voz
            track.append(
                Message("note_on", note=nota, velocity=vel, time=0, channel=track_index)
            )
            track.append(
                Message(
                    "note_off",
                    note=nota,
                    velocity=vel,
                    time=self.ticks,
                    channel=track_index,
                )
            )
        else:
            raise IndexError("Índice de faixa inválido")

    def set_instrument(self, instrument, track_index=None):
        self.instrument = instrument
        target_tracks = []
        is_single_track = track_index is not None and 0 <= track_index < len(self.tracks)
        if is_single_track:
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
                        )
                    )
            target_tracks = [track]
        else:
            target_tracks = self.tracks

        for i, track in enumerate(target_tracks):
            channel = track_index if is_single_track else i
            track.append(
                Message("program_change", program=instrument, time=0, channel=channel)
            )

    def set_bpm(self, bpm):
        if bpm <= 0:
            raise ValueError("BPM deve ser maior que zero")
        self.bpm = int(MICROSEGUNDOS_POR_MINUTO / bpm)
        for track in self.tracks:
            track.append(MetaMessage("set_tempo", tempo=self.bpm, time=0))

    def set_volume(self, volume):
        if not 0 <= volume <= 127:
            raise ValueError("Volume deve estar entre 0 e 127")
        self.volume = volume

    def get_actual_bpm(self):
        """Retorna o BPM real (não microsegundos por batida)."""
        return int(MICROSEGUNDOS_POR_MINUTO / self.bpm) if self.bpm != 0 else 0

    def save_mid(self, name):
        """Salva o arquivo MIDI no disco."""
        self.res.save(name)
