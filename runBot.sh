#!/bin/bash

# Configuración de rutas
BOT_DIR="/home/arturoolvrs/Bot"
BOT_SCRIPT="bot.py"
LOG_FILE="/home/arturoolvrs/nohup.out"
PYTHON_EXEC="python3"

# 1. Comprobar si el bot ya está en ejecución
if pgrep -f "$BOT_DIR/$BOT_SCRIPT" > /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] El bot ya está corriendo (PID: $(pgrep -f "$BOT_DIR/$BOT_SCRIPT"))."
    exit 0
fi

# 2. Entrar en la carpeta del bot para que gestione sus archivos locales
cd "$BOT_DIR" || { echo "[ERROR] No se pudo acceder a $BOT_DIR"; exit 1; }

# 3. Lanzar el proceso redirigiendo a /home/arturoolvrs/nohup.out
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Bot no detectado. Iniciando..."
nohup "$PYTHON_EXEC" "$BOT_DIR/$BOT_SCRIPT" >> "$LOG_FILE" 2>&1 &

# 4. Esperar 2 segundos para validar que no falló al arrancar
sleep 2

# 5. Comprobar estado final
PID=$(pgrep -f "$BOT_DIR/$BOT_SCRIPT")
if [ -n "$PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [OK] Bot iniciado con éxito (PID: $PID)."
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] Falló el inicio. Últimas líneas de $LOG_FILE:"
    tail -n 15 "$LOG_FILE"
fi
