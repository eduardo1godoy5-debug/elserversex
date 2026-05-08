#!/bin/bash
# Script para ver los logs del servidor en tiempo real
# Uso: ./watch-server.sh
# Escribe "stop" para detener el servidor

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Buscar el archivo de log más reciente
LATEST_LOG=$(ls -t server_logs/server_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ No se encontró ningún archivo de log"
    echo "Inicia el servidor primero con: ./start-server.sh"
    exit 1
fi

echo "📺 Viendo logs: $LATEST_LOG"
echo "💡 Escribe 'stop' para detener el servidor gracefully"
echo ""

# Iniciar tail en background
tail -f "$LATEST_LOG" &
TAIL_PID=$!

# Trap para limpiar tail cuando salimos
cleanup() {
    kill $TAIL_PID 2>/dev/null
}
trap cleanup EXIT

# Verificar que FIFO existe
if [ ! -p "server.fifo" ]; then
    echo "❌ Error: server.fifo no encontrado"
    echo "Asegúrate de ejecutar ./start-server.sh primero"
    exit 1
fi

# Leer input del usuario
while read -p "" input; do
    if [[ "$input" == "stop" ]]; then
        echo ""
        echo "🛑 Enviando comando 'stop' al servidor..."
        echo "$input" > server.fifo
        sleep 5
        break
    else
        # Enviar otros comandos al servidor
        echo "$input" > server.fifo
    fi
done

kill $TAIL_PID 2>/dev/null
