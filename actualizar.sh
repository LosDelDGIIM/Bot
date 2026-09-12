#!/bin/bash
set -e

# Configuración del servidor y rutas
SERVER_USER="arturoolvrs"
SERVER_HOST="miserver"   # Alias de /etc/hosts o IP directa
REMOTE_TARGET="${SERVER_USER}@${SERVER_HOST}"
REMOTE_DIR="~/Bot"
LOCAL_CHAT_LOG="chat_ids.log"

# 1. Detener el bot en el servidor
echo "Stopping bot on server..."
ssh -t "$REMOTE_TARGET" "${REMOTE_DIR}/stopBot.sh"

# 2. Sincronizar y fusionar chat_ids.log
echo "Syncing chat_ids.log..."
TMP_REMOTE_LOG=$(mktemp)

# Descargamos el del servidor si existe
if scp "${REMOTE_TARGET}:${REMOTE_DIR}/chat_ids.log" "$TMP_REMOTE_LOG" 2>/dev/null; then
    # Si no tienes archivo en local todavía, lo inicializamos vacío
    touch "$LOCAL_CHAT_LOG"

    # Fusión inteligente:
    # Lee primero el del servidor y luego el local.
    # Si un ID ya se leyó (del servidor), ignora la versión local antigua.
    awk -F';' '!visto[$1]++' "$TMP_REMOTE_LOG" "$LOCAL_CHAT_LOG" > "${LOCAL_CHAT_LOG}.tmp"
    mv "${LOCAL_CHAT_LOG}.tmp" "$LOCAL_CHAT_LOG"
    rm -f "$TMP_REMOTE_LOG"

    # Subimos el archivo combinado y definitivo al servidor
    scp "$LOCAL_CHAT_LOG" "${REMOTE_TARGET}:${REMOTE_DIR}/chat_ids.log"
    echo "chat_ids.log fusionado y sincronizado en local y servidor."
else
    echo "No se encontró chat_ids.log en el servidor; conservando versión local."
fi

# 3. Copiar los archivos nuevos al servidor
echo "Deploying new bot.py and prompt_ocr.txt..."
scp bot.py "${REMOTE_TARGET}:${REMOTE_DIR}/bot.py"
scp prompt_ocr.txt "${REMOTE_TARGET}:${REMOTE_DIR}/prompt_ocr.txt"

# 4. Iniciar el bot en el servidor
echo "Starting bot on server..."
ssh "$REMOTE_TARGET" "${REMOTE_DIR}/runBot.sh" < /dev/null > /dev/null 2>&1

echo "¡Bot actualizado con éxito!"