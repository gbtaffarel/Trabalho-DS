import pytest
from unittest.mock import patch, MagicMock
from src.interface import Interface


def test_excecoes_restritas_io():
    """
    Garante que falhas de disco (OSError) são capturadas e geram aviso,
    mas erros de lógica do programador (ex: TypeError) estouram a aplicação.
    """
    # Cria a instância da Interface BURLANDO o __init__ usando o __new__.
    # Isto impede que o CustomTkinter tente desenhar janelas e trave o terminal.
    app = Interface.__new__(Interface)

    # Injetamos mocks manuais estritamente necessários para os métodos testados
    app.caixa_texto = MagicMock()
    app._atualizar_status = MagicMock()

    with (
        patch("src.interface.filedialog.askopenfilename", return_value="dummy.txt"),
        patch("src.interface.messagebox.showerror") as mock_showerror,
    ):
        # 1. Simulamos um erro de disco (OSError) - DEVE ser capturado
        with patch("builtins.open", side_effect=OSError("Permissão negada")):
            app._carregar_arquivo()
            mock_showerror.assert_called_once()

        mock_showerror.reset_mock()

        # 2. Simulamos um erro de código (TypeError) - NÃO DEVE ser capturado
        with patch("builtins.open", side_effect=TypeError("Mock de erro do dev")):
            with pytest.raises(TypeError):
                app._carregar_arquivo()
            mock_showerror.assert_not_called()
