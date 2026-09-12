#!/bin/bash

# 1. Matar el proceso exacto usando la ruta completa
pkill -9 -f "$HOME/Bot/.*bot\.py" || pkill -9 -f "python.*bot\.py"

# 2. Eliminar nohup.out donde sea que se haya creado
rm -f "$HOME/Bot/nohup.out" "$HOME/nohup.out"

# 3. Eliminar logs del bot en la carpeta Bot (incluidos los rotados log_file.log_X)
rm -f "$HOME/Bot/log_file.log"* "$HOME/Bot/bot.log"*

# 4. Si DOWNLOAD_BASEDIR está en .env y es distinto, limpiar allí solo los log_file (respetando chat_ids.log)
if [ -f "$HOME/Bot/.env" ]; then
    BASEDIR=$(grep -E '^DOWNLOAD_BASEDIR=' "$HOME/Bot/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    if [ -n "$BASEDIR" ] && [ -d "$BASEDIR" ]; then
        rm -f "$BASEDIR/log_file.log"*
    fi
fi

echo "Proceso detenido y logs/nohup eliminados."