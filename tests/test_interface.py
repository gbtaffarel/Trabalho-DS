import pytest
from unittest.mock import patch, MagicMock
from src.interface import Interface


def test_excecoes_restritas_io():
    """
    Garante que falhas de disco (OSError) são capturadas e geram aviso,
    mas erros de lógica do programador (ex: TypeError) estouram a aplicação.
    """
    app = Interface.__new__(Interface)

    app.caixa_texto = MagicMock()
    app._atualizar_status = MagicMock()

    with (
        patch("src.interface.filedialog.askopenfilename", return_value="dummy.txt"),
        patch("src.interface.messagebox.showerror") as mock_showerror,
    ):
        with patch("builtins.open", side_effect=OSError("Permissão negada")):
            app._carregar_arquivo()
            mock_showerror.assert_called_once()

        mock_showerror.reset_mock()

        with patch("builtins.open", side_effect=TypeError("Mock de erro do dev")):
            with pytest.raises(TypeError):
                app._carregar_arquivo()
            mock_showerror.assert_not_called()


def test_salvar_texto_sucesso():
    """Testa salvar texto com sucesso."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app.caixa_texto.get.return_value = "teste musical"
    app._atualizar_status = MagicMock()

    with (
        patch("src.interface.filedialog.asksaveasfilename", return_value="musica.txt"),
        patch("builtins.open", MagicMock()) as mock_open,
    ):
        app._salvar_texto()
        mock_open.assert_called_once_with("musica.txt", "w", encoding="utf-8")
        app._atualizar_status.assert_called_once()


def test_salvar_texto_cancelado():
    """Testa quando usuário cancela salvar."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app._atualizar_status = MagicMock()

    with patch("src.interface.filedialog.asksaveasfilename", return_value=""):
        app._salvar_texto()
        app._atualizar_status.assert_not_called()


def test_salvar_texto_erro_io():
    """Testa erro de IO ao salvar."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app.caixa_texto.get.return_value = "teste"
    app._atualizar_status = MagicMock()

    with (
        patch("src.interface.filedialog.asksaveasfilename", return_value="musica.txt"),
        patch("builtins.open", side_effect=OSError("Erro de disco")),
        patch("src.interface.messagebox.showerror") as mock_showerror,
    ):
        app._salvar_texto()
        mock_showerror.assert_called_once()


def test_limpar_tudo():
    """Testa o método limpar_tudo."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app.slider_bpm = MagicMock()
    app.label_bpm = MagicMock()
    app._atualizar_status = MagicMock()
    app.tabela_vozes = MagicMock()

    app._limpar_tudo()

    app.caixa_texto.delete.assert_called_once()
    app.slider_bpm.set.assert_called_once_with(120)
    app.label_bpm.configure.assert_called_once()
    app.tabela_vozes.limpar_campos.assert_called_once()


def test_atualizar_status():
    """Testa o método _atualizar_status."""
    app = Interface.__new__(Interface)
    app.status_label = MagicMock()

    app._atualizar_status("Teste de mensagem")

    app.status_label.configure.assert_called_once_with(text="Teste de mensagem")


def test_gerar_midi_sem_texto():
    """Testa _gerar_midi quando não há texto."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app.caixa_texto.get.return_value = ""
    app.player_controller = MagicMock()
    app.player_controller.gerador_callback = None
    app._atualizar_status = MagicMock()

    with patch("src.interface.messagebox.showwarning") as mock_warning:
        result = app._gerar_midi()
        assert result is False
        mock_warning.assert_called_once()


def test_gerar_midi_sem_callback():
    """Testa _gerar_midi quando não há callback configurado."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app.caixa_texto.get.return_value = "texto musical"
    app.player_controller = MagicMock()
    app.player_controller.gerador_callback = None
    app._atualizar_status = MagicMock()
    app.janela = MagicMock()

    with patch("src.interface.messagebox.showinfo") as mock_info:
        result = app._gerar_midi()
        assert result is False
        mock_info.assert_called_once()


def test_gerar_midi_sucesso():
    """Testa _gerar_midi com sucesso."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app.caixa_texto.get.return_value = "ABC"
    app.slider_bpm = MagicMock()
    app.slider_bpm.get.return_value = 120
    app.tabela_vozes = MagicMock()
    app.tabela_vozes.obter_configs.return_value = []
    app.player_controller = MagicMock()
    app.player_controller.gerador_callback = MagicMock(return_value="saida.mid")
    app._atualizar_status = MagicMock()
    app.janela = MagicMock()

    result = app._gerar_midi()

    assert result is True
    app.player_controller.gerador_callback.assert_called_once()


def test_gerar_midi_erro_callback():
    """Testa _gerar_midi quando callback retorna erro."""
    app = Interface.__new__(Interface)
    app.caixa_texto = MagicMock()
    app.caixa_texto.get.return_value = "ABC"
    app.slider_bpm = MagicMock()
    app.slider_bpm.get.return_value = 120
    app.tabela_vozes = MagicMock()
    app.tabela_vozes.obter_configs.return_value = []
    app.player_controller = MagicMock()
    app.player_controller.gerador_callback = MagicMock(return_value=False)
    app._atualizar_status = MagicMock()
    app.janela = MagicMock()

    result = app._gerar_midi()

    assert result is False
