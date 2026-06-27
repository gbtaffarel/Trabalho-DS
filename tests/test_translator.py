import pytest
from src.translator import Translator, Nota, Comando


@pytest.fixture
def tradutor():
    """Fixture que fornece uma instância limpa do Translator para cada teste."""
    return Translator()


def test_traducao_notas_puras(tradutor):
    """Testa o mapeamento de notas musicais exatas, incluindo os bemóis."""
    assert tradutor._traduzir_token("A") == Nota(valor=69)
    assert tradutor._traduzir_token("C") == Nota(valor=60)
    assert tradutor._traduzir_token("Mb") == Nota(valor=63)
    assert tradutor._traduzir_token("mb") == Nota(valor=63)
    assert tradutor._traduzir_token("H") == Nota(valor=70)


def test_traducao_comandos_diretos(tradutor):
    """Testa o mapeamento estático de caracteres para comandos."""
    assert tradutor._traduzir_token(" ") == Comando(acao="volume", parametro=2)
    assert tradutor._traduzir_token("?") == Comando(acao="oitava", parametro=1)
    assert tradutor._traduzir_token(">") == Comando(acao="bpm", parametro=10)
    assert tradutor._traduzir_token("!") == Comando(acao="instrumento", parametro=24)


def test_traducao_pausas(tradutor):
    """Testa se as letras minúsculas (a-h) são corretamente lidas como pausas."""
    assert tradutor._traduzir_token("a") == Comando(acao="pausa", parametro=None)
    assert tradutor._traduzir_token("f") == Comando(acao="pausa", parametro=None)


def test_traducao_digitos(tradutor):
    """Testa a regra algorítmica: pares somam ao instrumento, ímpares mudam para 15."""
    assert tradutor._traduzir_token("2") == Comando(acao="instrumento_add", parametro=2)
    assert tradutor._traduzir_token("8") == Comando(acao="instrumento_add", parametro=8)
    assert tradutor._traduzir_token("3") == Comando(acao="instrumento", parametro=15)
    assert tradutor._traduzir_token("9") == Comando(acao="instrumento", parametro=15)


def test_traducao_fallback_consoantes(tradutor):
    """Garante que caracteres desconhecidos acionam o fallback de repetição (consoante)."""
    assert tradutor._traduzir_token("z") == Comando(acao="consoante", parametro=None)
    assert tradutor._traduzir_token("I") == Comando(acao="consoante", parametro=None)
    assert tradutor._traduzir_token("@") == Comando(acao="consoante", parametro=None)


def test_analisar_linha_completa(tradutor):
    """
    Testa o processamento regex da linha inteira.
    Verifica a extração do atraso [n] no início e a quebra de linha simulada no fim.
    """
    # A linha "[4]C a2" deve resultar em:
    # 1. Atraso 4 (do [4])
    # 2. Nota C
    # 3. Aumentar Volume (do espaço em branco)
    # 4. Pausa (do 'a')
    # 5. Adicionar instrumento 2 (do '2')
    # 6. Instrumento 123 (comportamento injetado no final de analisar_linha)

    instrucoes = tradutor.analisar_linha("[4]C a2")

    assert len(instrucoes) == 6
    assert instrucoes[0] == Comando(acao="atraso", parametro=4)
    assert instrucoes[1] == Nota(valor=60)
    assert instrucoes[2] == Comando(acao="volume", parametro=2)
    assert instrucoes[3] == Comando(acao="pausa", parametro=None)
    assert instrucoes[4] == Comando(acao="instrumento_add", parametro=2)
    assert instrucoes[5] == Comando(acao="instrumento", parametro=123)
