# Variables
VENV_DIR=.venv
PYTHON=$(VENV_DIR)/bin/python
PIP=$(VENV_DIR)/bin/pip
APP=main:app

# Ruta del modelo usado con Ollama
MODEL=gpt-oss:20b

# Crear entorno virtual e instalar dependencias
setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Ejecutar Ollama con el modelo (debe estar instalado con 'ollama pull')
start-ollama:
	ollama run $(MODEL)

# Iniciar API FastAPI
start-api:
	$(PYTHON) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Ejecutar ambos en paralelo (requiere 'tmux' instalado)
start-all:
	trap 'tmux kill-session -t ollama' EXIT
	tmux new-session -d -s ollama 'make start-ollama'
	sleep 5
	tmux new-session -d -s api 'make start-api'
	tmux attach-session -t api

# Limpiar entorno
clean:
	rm -rf $(VENV_DIR) db.sqlite3 __pycache__ .pytest_cache

