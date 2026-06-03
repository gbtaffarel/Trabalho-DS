# Detecta o Sistema Operacional
ifeq ($(OS),Windows_NT)
    # Configurações para Windows
    OS_TYPE := Windows
    PYTHON := venv/Scripts/python.exe
    PIP := venv/Scripts/pip.exe
    RM := del /q /f
    RMDIR := rmdir /s /q
    # No Windows, comandos como 'test -f' não existem nativamente, 
    # usamos o shell do windows ou ignoramos erros simples.
    CHECK_FILE := if exist
else
    # Configurações para Linux / macOS
    OS_TYPE := POSIX
    PYTHON := venv/bin/python
    PIP := venv/bin/pip3
    RM := rm -f
    RMDIR := rm -rf
    CHECK_FILE := test -f
endif

# Dependências
DEPS := mido customtkinter midi2audio pygame

.PHONY: help install check run clean clean-all

# Meta-alvo padrão
.DEFAULT_GOAL := help

help:
	@echo "Gerador de Trilhas Sonoras MIDI - Sistema Detectado: $(OS_TYPE)"
	@echo ""
	@echo "  make install    - Instala as dependências necessárias"
	@echo "  make check      - Verifica se as dependências estão instaladas"
	@echo "  make run        - Executa o programa (interface gráfica)"
	@echo "  make run-cli    - Executa o programa em modo CLI"
	@echo "  make clean      - Remove arquivos MIDI e áudio gerados"
	@echo "  make clean-all  - Remove arquivos gerados e __pycache__"

install:
	@echo "Instalando dependências em $(OS_TYPE)..."
	$(PIP) install $(DEPS)
	@echo "Pronto!"

check:
	@echo "Verificando dependências..."
	@$(PYTHON) -c "import mido; print('✓ mido instalado')" || echo "✗ mido não encontrado"
	@$(PYTHON) -c "import customtkinter; print('✓ customtkinter instalado')" || echo "✗ customtkinter não encontrado"
	@$(PYTHON) -c "import midi2audio; print('✓ midi2audio instalado')" || echo "✗ midi2audio não encontrado"
	@echo ""
	@echo "Verificando SoundFont..."
ifeq ($(OS),Windows_NT)
	@if exist FluidR3_GM.sf2 (echo ✓ FluidR3_GM.sf2 encontrado) else (echo ⚠ FluidR3_GM.sf2 não encontrado)
else
	@test -f FluidR3_GM.sf2 && echo "✓ FluidR3_GM.sf2 encontrado" || echo "⚠ FluidR3_GM.sf2 não encontrado"
endif

run:
	@echo "Iniciando Gerador de Trilhas Sonoras..."
	$(PYTHON) src/interface.py

run-cli:
	@echo "Executando em modo CLI..."
	$(PYTHON) src/main.py --cli --file natal.txt

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
