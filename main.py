from reader import reader
from translator import translator
from midigen import midigen
from midi2audio import FluidSynth

def addNota(nota):
    note = nota + (midi.get_oitava() + 1) * 12
    midi.add(note)
    return note

def zeraVolume():
    volume = midi.get_volume()
    midi.set_volume(0)
    midi.add(standard_note)
    midi.set_volume(volume)

def dobrarVolume():
    volume = midi.get_volume()
    volume = volume * 2
    if volume > 127:
        volume = volume - 127
    midi.set_volume(volume)

def trocarInstrumento(id_instrumento):
    midi.set_instrument(id_instrumento)

print("Gerador de Trilha Sonora (TESTE)")
print("Insira a localização de um arquivo .txt")
path = input()


text = reader(path)
text.load()

translate = translator()

midi = midigen(127, 120, 1, 4)

standard_note = 60
last_note = False
last_note_value = 0

for i in range (text.length()):
    next_char = text.next()
    instruction = translate.translate(next_char)
    if isinstance(instruction, int):
        last_note_value = addNota(instruction)
        last_note = True
    else:
        if instruction[0] == "volume":
            if instruction[1] == 0:
                zeraVolume()
            elif instruction[1] == 2:
                dobrarVolume()
        elif instruction[0] == "instrument":
            instrument_replace = instruction[1]
        elif instruction[0] == "instrument+":
            instrument_replace = instruction[1] + midi.get_instrument
            if (instrument_replace > 127):
                instrument_replace = instrument_replace - 127
            midi.set_instrument(instrument_replace)
        elif instruction[0] == "consonant":
            if last_note:
                midi.add(last_note_value)
            else:
                volume = midi.get_volume()
                midi.set_volume(0)
                midi.add(standard_note)
                midi.set_volume(volume)
        elif instruction[0] == "oitava":
            if midi.get_oitava() + 1 <= 9:
                midi.set_oitava(midi.get_oitava() + 1)
        last_note = False

midi.save_mid("teste.mid")

fs = FluidSynth("FluidR3_GM.sf2")
fs.midi_to_audio("teste.mid", "saida.wav")

