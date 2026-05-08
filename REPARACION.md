# 🔧 Guía de Reparación - Servidor Cerrándose Solo

## Problema Identificado
El servidor se cerraba porque:
1. **No hay auto-restart implementado** (la config lo tenía pero el código no)
2. **Terminal interactiva**: Si se cerraba la terminal o expiraba el timeout, el servidor moría
3. **Sin watchdog**: No había mecanismo para reiniciar si crasheaba

---

## ✅ Soluciones Implementadas

### 1. **Auto-restart en el código** (`mc.py`)
- Ahora el servidor respeta la configuración `auto_restart: true`
- Se reinicia automáticamente cuando termina
- Mantiene contador de reintentos
- Espera 10 segundos entre reinicios para evitar loops rápidos

### 2. **Scripts auxiliares**

#### `start-server.sh` - Ejecuta el servidor en background
```bash
./start-server.sh
```
✅ El servidor continuará ejecutándose aunque cierres la terminal
✅ Los logs se guardan con timestamp
✅ Se crea un archivo `server.pid` con el ID del proceso

#### `watch-server.sh` - Ver logs en tiempo real
```bash
./watch-server.sh
```
✅ Ve los logs mientras el servidor corre en background

---

## 🚀 Cómo Usar

### Opción 1: Ejecución interactiva (original)
```bash
python3 mc.py
```
- Podrás escribir comandos directamente
- Se cerrará si cierras la terminal

### Opción 2: Ejecución en background (RECOMENDADO)
```bash
# Terminal 1: Inicia el servidor
./start-server.sh

# Terminal 2: Ve los logs
./watch-server.sh

# Para detener: 
kill $(cat server.pid)
```
✅ El servidor continuará aunque cierres terminal 1

---

## 📊 Configuración

En `mexus_config.json`:
```json
{
  "auto_restart": true      // ✅ Ahora funciona
}
```

---

## 🐛 Si Aún Se Cierra

1. **Revisa los logs:**
   ```bash
   ./watch-server.sh
   ```
   Busca líneas rojas/errores antes del cierre

2. **Causas posibles:**
   - **OutOfMemory**: Aumenta RAM en opción 3
   - **Crash de mod**: Revisa la lista de mods en logs
   - **Timeout del contenedor**: Usa `start-server.sh`
   - **Límite de CPU**: Codespaces tiene límites (4 CPUs, 16GB RAM)

3. **Temporada fix rápido:**
   ```bash
   # Termina todos los procesos Java
   pkill -f "java.*server.jar"
   
   # Limpia y reinicia
   rm -f server.pid
   ./start-server.sh
   ```

---

## 📝 Cambios Realizados

**mc.py:**
- ✅ Agregado loop de auto-restart
- ✅ Contador de reintentos
- ✅ Timestamps en cada reinicio
- ✅ Mejor manejo de cierre (Ctrl+C)
- ✅ Playit solo inicia una vez

**Nuevos scripts:**
- ✅ `start-server.sh` - Ejecución en background
- ✅ `watch-server.sh` - Ver logs en vivo

---

## ⚡ Tips Avanzados

### Ejecutar 24/7 con tmux
```bash
tmux new-session -d -s minecraft "cd /ruta && ./start-server.sh"
tmux attach -t minecraft
```

### Ejecutar 24/7 con systemd
Crea `/etc/systemd/system/minecraft.service`:
```ini
[Unit]
Description=Minecraft Server
After=network.target

[Service]
Type=simple
User=codespace
WorkingDirectory=/workspaces/elserversex
ExecStart=/bin/bash start-server.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl daemon-reload
sudo systemctl start minecraft
sudo systemctl status minecraft
```

---

## 🆘 Contacto

Si aún tienes problemas:
1. Revisa los logs: `./watch-server.sh`
2. Busca errores de Java, mods o memoria
3. Aumenta RAM si ves OutOfMemory
4. Desactiva playit si es problema de networking
