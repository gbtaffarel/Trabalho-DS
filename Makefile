# Detecta o Sistema Operacional
ifeq ($(OS),Windows_NT)
    # Configurações para Windows
    OS_TYPE := Windows
    SYS_PYTHON := python
    PYTHON := .venv/Scripts/python.exe
    PIP := .venv/Scripts/pip.exe
    ACTIVATE := call .venv\Scripts\activate.bat
    RM := del /q /f
    RMDIR := rmdir /s /q
    # No Windows, comandos como 'test -f' não existem nativamente, 
    # usamos o shell do windows ou ignoramos erros simples.
    CHECK_FILE := if exist
else
    # Configurações para Linux / macOS
    OS_TYPE := POSIX
    SYS_PYTHON := python3
    PYTHON := .venv/bin/python
    PIP := .venv/bin/pip3
    ACTIVATE := . .venv/bin/activate
    RM := rm -f
    RMDIR := rm -rf
    CHECK_FILE := test -f
endif

# Dependências
DEPS := mido customtkinter midi2audio pygame-ce pytest

.PHONY: help install check run test clean clean-all

# Meta-alvo padrão
.DEFAULT_GOAL := help

help:
	@echo "Gerador de Trilhas Sonoras MIDI - Sistema Detectado: $(OS_TYPE)"
	@echo ""
	@echo "  make install    - Cria a venv (se não existir) e instala as dependências"
	@echo "  make check      - Verifica se as dependências estão instaladas"
	@echo "  make run        - Executa o programa (interface gráfica)"
	@echo "  make test       - Executa toda a suite de testes unitários"
	@echo "  make clean      - Remove arquivos MIDI e áudio gerados"
	@echo "  make clean-all  - Remove arquivos gerados e __pycache__"

# Alvo responsável por criar a venv se a pasta não existir
.venv:
	@echo "Criando ambiente virtual (.venv)..."
	$(SYS_PYTHON) -m venv .venv
	@echo "Ambiente virtual criado com sucesso!"

# Ao chamar install, o Make verifica se .venv existe primeiro
install: .venv
	@echo "Instalando dependências em $(OS_TYPE)..."
	$(PIP) install $(DEPS)
	@echo "Pronto!"

check:
	@echo "Verificando dependências..."
	@$(PYTHON) -c "import mido; print('✓ mido instalado')" || echo "✗ mido não encontrado"
	@$(PYTHON) -c "import customtkinter; print('✓ customtkinter instalado')" || echo "✗ customtkinter não encontrado"
	@$(PYTHON) -c "import midi2audio; print('✓ midi2audio instalado')" || echo "✗ midi2audio não encontrado"
	@$(PYTHON) -W ignore -c "import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'; import pygame; print('✓ pygame instalado')" || echo "✗ pygame não encontrado"
	@echo ""
	@echo "Verificando SoundFont..."
ifeq ($(OS),Windows_NT)
	@echo "✓ Windows detectado (Sintetizador nativo será utilizado para reprodução)"
else
	@test -f /usr/share/soundfonts/FluidR3_GM.sf2 && echo "✓ FluidR3_GM.sf2 encontrado" || echo "⚠ FluidR3_GM.sf2 não encontrado"
endif

run: .venv
	@echo "Iniciando Gerador de Trilhas Sonoras..."
	@$(ACTIVATE) && $(PYTHON) src/interface.py

test: .venv
	@echo "Executando a suite de testes..."
	@$(ACTIVATE) && PYTHONPATH=src pytest tests/ -v

clean:
	@echo "Limpando arquivos de saída..."
ifeq ($(OS),Windows_NT)
	-$(RM) *.mid *.midi *.wav *.mp3 *.ogg 2>nul
else
	-$(RM) *.mid *.midi *.wav *.mp3 *.ogg
endif
	@echo "Arquivos removidos."

clean-all: clean
	@echo "Limpando caches Python..."
ifeq ($(OS),Windows_NT)
	-for /d /r . %%d in (__pycache__) do @if exist "%%d" $(RMDIR) "%%d" 2>nul
else
	$(RMDIR) __pycache__ */__pycache__ .pytest_cache
endif
	@echo "Caches removidos."
