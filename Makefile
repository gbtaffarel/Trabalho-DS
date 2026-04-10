# Makefile para o Gerador de Trilhas Sonoras MIDI
# Fase 2 - Interface Gráfica com customtkinter

PYTHON := $(shell which python3 || which python)
PIP := $(shell which pip3 || which pip)

# Dependências necessárias
DEPS := mido customtkinter midi2audio

.PHONY: help install check run clean clean-all

help:
	@echo "Gerador de Trilhas Sonoras MIDI - Comandos disponíveis:"
	@echo ""
	@echo "  make install    - Instala as dependências necessárias"
	@echo "  make check      - Verifica se as dependências estão instaladas"
	@echo "  make run        - Executa o programa (interface gráfica)"
	@echo "  make run-cli    - Executa o programa em modo CLI (bypass)"
	@echo "  make clean      - Remove arquivos MIDI e áudio gerados"
	@echo "  make clean-all  - Remove arquivos gerados e __pycache__"
	@echo ""

install:
	@echo "Instalando dependências..."
	$(PIP) install $(DEPS)
	@echo "Pronto!"

check:
	@echo "Verificando dependências..."
	@$(PYTHON) -c "import mido; print('✓ mido instalado')" 2>/dev/null || echo "✗ mido não encontrado - rode: make install"
	@$(PYTHON) -c "import customtkinter; print('✓ customtkinter instalado')" 2>/dev/null || echo "✗ customtkinter não encontrado - rode: make install"
	@$(PYTHON) -c "import midi2audio; print('✓ midi2audio instalado')" 2>/dev/null || echo "✗ midi2audio não encontrado - rode: make install"
	@echo ""
	@echo "Verificando SoundFont..."
	@test -f FluidR3_GM.sf2 && echo "✓ FluidR3_GM.sf2 encontrado (conversão WAV disponível)" || echo "⚠ FluidR3_GM.sf2 não encontrado - apenas .mid será gerado"

run:
	@echo "Iniciando Gerador de Trilhas Sonoras..."
	$(PYTHON) main.py

run-cli:
	@echo "Executando em modo CLI (bypass da interface)..."
	@echo "natal.txt" | $(PYTHON) main.py

clean:
	@echo "Limpando arquivos de saída..."
	rm -f *.mid *.midi *.wav *.mp3 *.ogg
	@echo "Arquivos de áudio/MIDI removidos."

clean-all: clean
	@echo "Limpando caches Python..."
	rm -rf __pycache__ */__pycache__ *.pyc .pytest_cache
	@echo "Cache removido."

# Target padrão
.DEFAULT_GOAL := help
