#!/bin/bash
# Script para iniciar TODO: Servidor + Playit en background
# Uso: ./start-all.sh
# 
# Este script inicia:
# 1. Playit (con auto-restart)
# 2. Servidor Minecraft (con auto-restart)
# Todo en background

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎮 Iniciando servidor Minecraft + Playit..."
echo ""

# Hacer ejecutables
chmod +x start-server.sh start-playit.sh 2>/dev/null

# Iniciar Playit en background
echo "1️⃣  Iniciando Playit..."
./start-playit.sh &
PLAYIT_SCRIPT_PID=$!
sleep 2

# Iniciar Servidor
echo ""
echo "2️⃣  Iniciando Servidor Minecraft..."
./start-server.sh
SERVER_SCRIPT_PID=$!
sleep 2

echo ""
echo "✅ SISTEMA OPERACIONAL"
echo ""
echo "📊 Estados:"
echo "  - Playit: $([ -f playit.pid ] && echo "✅ Corriendo (PID: $(cat playit.pid))" || echo "❌ No iniciado")"
echo "  - Servidor: $([ -f server.pid ] && echo "✅ Corriendo (PID: $(cat server.pid))" || echo "❌ No iniciado")"
echo ""
echo "📺 Ver logs:"
echo "  Terminal 1: ./watch-playit.sh"
echo "  Terminal 2: ./watch-server.sh"
echo ""
echo "🛑 Para detener:"
echo "  kill $(cat server.pid)  # Servidor"
echo "  kill $(cat playit.pid)  # Playit"
echo "  pkill -f 'start-server.sh'  # Todo"
echo ""
echo "Los procesos continúan ejecutándose aunque cierres esta terminal"
