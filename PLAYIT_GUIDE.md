# 🌐 Guía Playit - Auto-restart e Independencia

## Problema con Playit
- Playit fallaba con error: `RenderError(Os { code: 6, ... "No such device or address" }`
- Se cerraba sin reintentar
- Interrupción de servicio de tunneling

## ✅ Solución: Scripts Independientes para Playit

### Nuevo: `start-playit.sh`
```bash
./start-playit.sh
```
✅ Ejecuta Playit en background
✅ **Auto-restart automático** (se reinicia cada 5s si falla)
✅ Logs guardados en `server_logs/playit.log`
✅ Independiente del servidor (pueden fallar por separado)
✅ PID guardado en `playit.pid`

### Nuevo: `watch-playit.sh`
```bash
./watch-playit.sh
```
✅ Ve los logs de Playit en tiempo real
✅ Detecta reintentos automáticos

### Nuevo: `start-all.sh` (RECOMENDADO)
```bash
./start-all.sh
```
✅ Inicia Servidor + Playit automáticamente
✅ Ambos con auto-restart
✅ Guía clara de comandos al finalizar

---

## 🏗️ Arquitectura

### Antes (problemas)
```
start-server.sh
    ↓
mc.py intenta iniciar Playit
    ↓
Si Playit falla → Servidor también se ve afectado
```

### Ahora (solución)
```
start-all.sh
    ├─ Playit (proceso independiente)
    │   └─ Auto-restart cada 5s si falla
    │
    └─ Servidor (proceso independiente)
        └─ Auto-restart cada 10s si falla
```

Ahora **Playit y Servidor son completamente independientes**.

---

## 🚀 Uso Recomendado

### Opción 1: Todo automático
```bash
./start-all.sh
```

Luego en otras terminales:
```bash
# Terminal 2: Ver Playit
./watch-playit.sh

# Terminal 3: Ver Servidor
./watch-server.sh
```

### Opción 2: Personalizadas
```bash
# Terminal 1: Playit solamente
./start-playit.sh

# Terminal 2: Servidor solamente
./start-server.sh

# Terminal 3: Ver Playit
./watch-playit.sh

# Terminal 4: Ver Servidor
./watch-server.sh
```

### Opción 3: Desactivar Playit (sin tunneling)
```bash
python3 mc.py  # Opción 4: Desactivar Playit
./start-server.sh
```

---

## 📊 Configuración

En `mexus_config.json`:
```json
{
  "use_playit": true,         // ✅ Habilitar/Deshabilitar
  "playit_path": "./playit-linux-amd64"
}
```

---

## 🛠️ Parámetros de Auto-Restart

**Playit:**
- Intenta reiniciar cada **5 segundos**
- Loop infinito (siempre se reinicia)
- Logs: `server_logs/playit.log`

**Servidor:**
- Intenta reiniciar cada **10 segundos**
- Depende de config `auto_restart: true`
- Logs: `server_logs/server_*.log`

---

## 📝 Ejemplos de Uso

### Ejecutar 24/7 ambos
```bash
nohup ./start-all.sh > server_logs/startup.log 2>&1 &
```

### Ejecutar solo Playit con tmux
```bash
tmux new-session -d -s playit "./start-playit.sh"
```

### Revisar auto-restartsgeneral el Playit
```bash
grep "Intento #" server_logs/playit.log
```

### Detener ambos
```bash
kill $(cat playit.pid) $(cat server.pid)
```

---

## 🐛 Debugging

### Ver errores de Playit
```bash
./watch-playit.sh

# Buscar específicamente errores
tail -f server_logs/playit.log | grep -i error
```

### Verificar que Playit está corriendo
```bash
ps aux | grep playit-linux
```

### Ver intentos de auto-restart
```bash
grep "Intento\|iniciado\|terminó" server_logs/playit.log
```

---

## ⚡ Performance

- **Playit**: ~5-10 MB RAM
- **Servidor**: 4-8 GB RAM (configurable)
- **Overhead de scripts**: < 100 MB

Con ambos corriendo continuamente: **~4.5 GB RAM mínimo**

---

## 🎯 Estados Esperados

### Playit funcionando correctamente
```
[2026-04-27 04:47:00] Intento #1 - Iniciando Playit...
✅ Playit iniciado (PID: 75786)
[2026-04-27 04:47:01] Intento #2 - Iniciando Playit...
✅ Playit iniciado (PID: 75790)
... (loops continuos)
```

### Servidor funcionando correctamente
```
[2026-04-27 04:47:00] Iniciando servidor (intento 1)
✅ Iniciando fabric 1.21.11
🔄 Servidor ejecutándose en background
[04:47:05] [Server thread/INFO]: Done (1.201s)! For help, type "help"
```

---

## 🆘 FAQ

**P: ¿Playit necesita internet?**
R: Sí, necesita conectarse a servidores de playit.gg. En contenedores sin internet, fallará pero seguirá reintentando.

**P: ¿Puedo usar solo el servidor sin Playit?**
R: Sí, desactívalo en opción 4 de `python3 mc.py`

**P: ¿Qué pasa si Playit crashea?**
R: Se reinicia automáticamente cada 5 segundos. El servidor NO se ve afectado.

**P: ¿Qué pasa si el servidor crashea?**
R: Se reinicia automáticamente cada 10 segundos (si `auto_restart: true`). Playit NO se ve afectado.

**P: ¿Puedo ejecutar en una RPi o servidor barato?**
R: Sí, aunque los recursos sean limitados. Los scripts de auto-restart funcionan en cualquier Linux.
