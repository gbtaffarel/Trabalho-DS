class reader:

    def __init__(self, path):
        self.path = path
        self.content = ""
        self.pos = 0

    def load(self):
        with open(self.path, "r") as f:
            self.content = f.read()

    def next(self):
        if self.pos < len(self.content):
            c = self.content[self.pos]
            self.pos += 1
            return c
        return None
    
    def length(self):
        return len(self.content)