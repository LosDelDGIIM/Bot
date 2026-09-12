#!/bin/bash

# Configuración del servidor
SERVER_USER="arturoolvrs"
SERVER_HOST="miserver"   # Puedes poner un alias de /etc/hosts o la IP directa (ej: "192.168.1.48")
REMOTE_TARGET="${SERVER_USER}@${SERVER_HOST}"

# 1. Detener el bot en el servidor
echo "Stopping bot on server..."
ssh -t "$REMOTE_TARGET" "~/Bot/stopBot.sh"

# 2. Copiar el nuevo archivo desde tu PC al servidor
echo "Deploying new bot.py..."
scp bot.py "${REMOTE_TARGET}:~/Bot/bot.py"
scp prompt_ocr.txt "${REMOTE_TARGET}:~/Bot/prompt_ocr.txt"

# 3. Iniciar el bot en el servidor
echo "Starting bot on server..."
ssh "$REMOTE_TARGET" "~/Bot/runBot.sh" < /dev/null > /dev/null 2>&1

echo "¡Bot actualizado con éxito!"