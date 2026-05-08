#!/bin/bash
# Script para ver los logs de Playit en tiempo real
# Uso: ./watch-playit.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PLAYIT_LOG="server_logs/playit.log"

if [ ! -f "$PLAYIT_LOG" ]; then
    echo "❌ No se encontró el archivo de log: $PLAYIT_LOG"
    echo "Inicia Playit primero con: ./start-playit.sh"
    exit 1
fi

echo "📺 Viendo logs de Playit: $PLAYIT_LOG"
echo "Presiona Ctrl+C para salir"
echo ""

tail -f "$PLAYIT_LOG"
