#!/bin/bash
# Script para ejecutar Playit en background con auto-restart
# Uso: ./start-playit.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Crear carpeta de logs si no existe
mkdir -p server_logs

PLAYIT_BIN="./playit-linux-amd64"
PLAYIT_LOG="server_logs/playit.log"
PLAYIT_PID_FILE="playit.pid"
RESTART_DELAY=5

# Verificar que playit existe
if [ ! -f "$PLAYIT_BIN" ]; then
    echo "❌ Error: No se encontró $PLAYIT_BIN"
    exit 1
fi

# Hacer ejecutable
chmod +x "$PLAYIT_BIN"

echo "🌐 Iniciando Playit en background con auto-restart..."
echo "📝 Logs: $PLAYIT_LOG"
echo ""

# Loop de auto-restart
RESTART_COUNT=0
while true; do
    RESTART_COUNT=$((RESTART_COUNT + 1))
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    
    echo "[$TIMESTAMP] Intento #$RESTART_COUNT - Iniciando Playit..." | tee -a "$PLAYIT_LOG"
    
    # Ejecutar playit en background
    nohup "$PLAYIT_BIN" >> "$PLAYIT_LOG" 2>&1 &
    PLAYIT_PID=$!
    
    # Guardar PID
    echo $PLAYIT_PID > "$PLAYIT_PID_FILE"
    
    echo "✅ Playit iniciado (PID: $PLAYIT_PID)"
    
    # Esperar a que el proceso termine
    wait $PLAYIT_PID 2>/dev/null || true
    
    # El proceso terminó, esperar antes de reiniciar
    echo "⚠️  Playit terminó (PID: $PLAYIT_PID). Reiniciando en ${RESTART_DELAY}s..."
    sleep $RESTART_DELAY
done
