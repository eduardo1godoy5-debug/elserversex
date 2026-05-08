#!/bin/bash
# Script para ejecutar el servidor Minecraft en background de forma persistente
# Uso: ./start-server.sh
# 
# Nota: Playit se ejecuta de forma INDEPENDIENTE con: ./start-playit.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Crear carpeta de logs si no existe
mkdir -p server_logs

# Crear FIFO para comandos del servidor
FIFO="server.fifo"
if [ -e "$FIFO" ]; then
    rm "$FIFO"
fi
mkfifo "$FIFO"

# Timestamp para logs
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="server_logs/server_${TIMESTAMP}.log"

echo "🚀 Iniciando servidor Minecraft en background..."
echo "📝 Logs: $LOG_FILE"
echo "💾 PID guardado en: server.pid"
echo ""
echo "💡 Nota: Playit se ejecuta INDEPENDIENTEMENTE"
echo "    Para ejecutar Playit: ./start-playit.sh"
echo ""

# Ejecutar en background, stdin desde FIFO para aceptar comandos
nohup python3 mc.py < "$FIFO" >> "$LOG_FILE" 2>&1 &
PID=$!

# Guardar PID
echo $PID > server.pid

# Mantener el FIFO abierto en background
exec 3>"$FIFO"

echo "✅ Servidor iniciado (PID: $PID)"
echo ""
echo "Comandos útiles:"
echo "  Ver logs:     tail -f $LOG_FILE"
echo "  Ver logs en tiempo real y enviar comandos: ./watch-server.sh"
echo "  Apagar servidor: echo stop > server.fifo"

