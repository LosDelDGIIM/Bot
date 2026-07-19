#!/bin/bash

# 1. Detener el bot en el servidor
echo "Stopping bot on server..."
ssh -t arturo@serverJesus "~/stopBot.sh"

# 2. Copiar el nuevo archivo desde tu PC al servidor
echo "Deploying new bot.py..."
scp bot.py arturo@serverJesus:~/Bot/bot.py
scp prompt_ocr.txt arturo@serverJesus:~/Bot/prompt_ocr.txt

# 3. Iniciar el bot en el servidor
echo "Starting bot on server..."
ssh arturo@serverJesus "~/runBot.sh" < /dev/null > /dev/null 2>&1

echo "¡Bot actualizado con éxito!"
