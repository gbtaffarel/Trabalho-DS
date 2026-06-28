# Esse modulo eh responsavel por ler o arquivo de entrada do programa


class Reader:
    def __init__(self, path=None):
        self.path = path
        self.content = ""
        self.pos = 0
        self.lines = []
        self.line_pos = 0

    def load(self):
        with open(self.path, "r") as f:
            self.content = f.read()
            self.lines = self.content.splitlines()

    def load_from_string(self, text):
        """Carrega o conteudo a partir de uma string."""
        self.content = text
        self.lines = text.splitlines()
        self.pos = 0
        self.line_pos = 0

    # Metodo para iterar sobre a string, caracter por caracter
    def next(self):
        if self.pos < len(self.content):
            c = self.content[self.pos]
            self.pos += 1
            return c
        return None

    def length(self):
        return len(self.content)

    # Metodo para obter a proxima linha
    def next_line(self):
        if self.line_pos < len(self.lines):
            line = self.lines[self.line_pos]
            self.line_pos += 1
            return line
        return None

    # Metodo para verificar se ha mais linhas
    def is_empty(self):
        return self.line_pos >= len(self.lines)

    # Metodo para resetar a posicao do cursor de leitura
    def reset(self):
        pass
