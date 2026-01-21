#!/bin/bash

# Script para iniciar Hermes al encender la PC
# Ruta del proyecto
PROJECT_DIR="/home/srec/Hermes"

# Cambiar a directorio del proyecto
cd "$PROJECT_DIR"

# Activar entorno virtual y ejecutar make start-all
source .venv/bin/activate && make start-all >> /var/log/hermes-startup.log 2>&1
