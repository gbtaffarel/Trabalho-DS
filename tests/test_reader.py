import pytest
from unittest.mock import patch, mock_open
from src.reader import Reader


def test_load_from_string():
    """Garante que o carregamento por string reinicia os cursores e separa as linhas."""
    leitor = Reader()
    texto = "linha 1\nlinha 2"
    leitor.load_from_string(texto)

    assert leitor.content == texto
    assert len(leitor.lines) == 2
    assert leitor.lines[0] == "linha 1"
    assert leitor.lines[1] == "linha 2"
    assert leitor.pos == 0
    assert leitor.line_pos == 0


def test_next_character():
    """Garante que o cursor de caracteres itera corretamente e retorna None no final."""
    leitor = Reader()
    leitor.load_from_string("ab")

    assert leitor.next() == "a"
    assert leitor.next() == "b"
    assert leitor.next() is None


def test_next_line_and_is_empty():
    """Garante que a iteração por linhas e o verificador de fim de arquivo funcionam."""
    leitor = Reader()
    leitor.load_from_string("voz1\nvoz2")

    assert not leitor.is_empty()
    assert leitor.next_line() == "voz1"

    assert not leitor.is_empty()
    assert leitor.next_line() == "voz2"

    assert leitor.is_empty()
    assert leitor.next_line() is None


def test_load_from_file():
    """Testa a leitura de arquivo físico usando mock do sistema de arquivos."""
    conteudo_mock = "A B C\nD E F"

    # O mock intercepta a chamada builtins.open e retorna nosso conteudo_mock
    with patch("builtins.open", mock_open(read_data=conteudo_mock)):
        leitor = Reader("caminho/falso.txt")
        leitor.load()

        assert leitor.content == conteudo_mock
        assert len(leitor.lines) == 2
        assert leitor.lines[0] == "A B C"
