# Esse modulo contem o conjunto de regras para traduriz os caracteres
# em notas, instrumentos, oitavas e volume.
class translator:
    def __init__(self):
        self.notas = {
            # Notas padroes
            "C": 0,
            "D": 2,
            "E": 4,
            "F": 5,
            "G": 7,
            "A": 9,
            "B": 11,
            # Notas sustenidas / bemol
            "H": 10,  # Si Bemol
        }

    def translate(self, char):
        if char in self.notas:
            teste = self.notas.get(char)
            return teste

        # Transforma o caractere para minusculo para facilitar comparacoes
        c = char.lower()

        if c in "abcdefgh":
            return ["volume", 0]

        if c == " ":
            return ["volume", 2]

        if c == "!":
            return ["instrument", 24]

        if c in "oiu":
            return ["instrument", 110]

        if c in "jklmnpqrstvwxyz":
            return ["consonant"]

        if char.isdigit() and int(char) % 2 == 0:
            return ["instrument+", int(char)]

        if c == "?":
            return ["oitava"]

        if c == "\n":
            return ["instrument", 123]

        if c == ";" or (char.isdigit() and int(char) % 2 != 0):
            return ["instrument", 15]

        if c == ",":
            return ["instrument", 114]

        return ["consonant"]
