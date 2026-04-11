# Esse modulo eh responsavel por ler o arquivo de entrada do programa


class reader:
    def __init__(self, path):
        self.path = path  # caminho do arquivo de entrada
        self.content = ""
        self.pos = 0  # Posicao do cursor de leitura

    def load(self):
        with open(self.path, "r") as f:
            self.content = f.read()

    # Metodo para iterar sobre a string, caracter por caracter
    def next(self):
        if self.pos < len(self.content):
            c = self.content[self.pos]
            self.pos += 1
            return c
        return None

    def length(self):
        return len(self.content)

