#!/bin/bash

# 1. Matar únicamente el proceso del bot (haciendo match exacto a bot.py dentro de tu carpeta)
pkill -9 -f '/home/arturoolvrs/Bot/.*bot\.py' || pkill -9 -f 'python.*bot\.py'

# 2. Eliminar el archivo nohup.out si existe
rm -f ~/Bot/nohup.out ~/nohup.out

# 3. Eliminar los archivos de logs (*.log dentro de la carpeta Bot)
rm -f ~/Bot/*.log

echo "Proceso detenido y logs/nohup eliminados."
