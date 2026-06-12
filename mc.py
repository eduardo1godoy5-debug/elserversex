import subprocess
import time
import os
import json
import threading
import zipfile
import signal
import sys
import shutil
import glob
from datetime import datetime

# ------------------------------------
#       DEPENDENCIAS
# ------------------------------------
def ensure_package(package):
    try:
        __import__(package)
        return True
    except ImportError:
        print(f"📦 Instalando {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
            return True
        except:
            return False

ensure_package('requests')
import requests

# ------------------------------------
#       UI MEJORADA
# ------------------------------------
class UI:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;129m'
    PINK = '\033[38;5;198m'
    
    @staticmethod
    def box(content, width=52, color=CYAN):
        lines = content.split('\n')
        top = f"{color}╔{'═' * width}╗{UI.RESET}"
        bottom = f"{color}╚{'═' * width}╝{UI.RESET}"
        result = [top]
        for line in lines:
            visible_len = len(line.replace(UI.RESET, '').replace(UI.BOLD, '').replace(UI.DIM, '').replace(UI.RED, '').replace(UI.GREEN, '').replace(UI.YELLOW, '').replace(UI.BLUE, '').replace(UI.MAGENTA, '').replace(UI.CYAN, '').replace(UI.WHITE, '').replace(UI.ORANGE, '').replace(UI.PURPLE, '').replace(UI.PINK, ''))
            padding = max(0, width - visible_len)
            result.append(f"{color}║{UI.RESET} {line}{' ' * padding} {color}║{UI.RESET}")
        result.append(bottom)
        return '\n'.join(result)
    
    @staticmethod
    def banner():
        banner = f"""
{UI.PINK}╔══════════════════════════════════════════════════════════════╗{UI.RESET}
{UI.PINK}║{UI.RESET} {UI.CYAN}███╗░░░███╗███████╗██╗░░██╗██╗░░░██╗░██████╗{UI.RESET} {UI.PINK}║{UI.RESET}
{UI.PINK}║{UI.RESET} {UI.CYAN}████╗░████║██╔════╝╚██╗██╔╝██║░░░██║██╔════╝{UI.RESET} {UI.PINK}║{UI.RESET}
{UI.PINK}║{UI.RESET} {UI.CYAN}██╔████╔██║█████╗░░░╚███╔╝░██║░░░██║╚█████╗░{UI.RESET} {UI.PINK}║{UI.RESET}
{UI.PINK}║{UI.RESET} {UI.CYAN}██║╚██╔╝██║██╔══╝░░░██╔██╗░██║░░░██║░╚═══██╗{UI.RESET} {UI.PINK}║{UI.RESET}
{UI.PINK}║{UI.RESET} {UI.CYAN}██║░╚═╝░██║███████╗██╔╝╚██╗╚██████╔╝██████╔╝{UI.RESET} {UI.PINK}║{UI.RESET}
{UI.PINK}║{UI.RESET} {UI.CYAN}╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝░╚═════╝░╚═════╝░{UI.RESET} {UI.PINK}║{UI.RESET}
{UI.PINK}║{UI.RESET} {UI.ORANGE}🎮 Minecraft Server Manager v2.1 - By MEXUS 🎮{UI.RESET} {UI.PINK}║{UI.RESET}
{UI.PINK}╚══════════════════════════════════════════════════════════════╝{UI.RESET}
"""
        return banner
    
    @staticmethod
    def success(msg): print(f"{UI.GREEN}✔ {msg}{UI.RESET}")
    @staticmethod
    def error(msg): print(f"{UI.RED}✖ {msg}{UI.RESET}")
    @staticmethod
    def warning(msg): print(f"{UI.YELLOW}⚠ {msg}{UI.RESET}")
    @staticmethod
    def info(msg): print(f"{UI.BLUE}ℹ {msg}{UI.RESET}")
    @staticmethod
    def highlight(msg): print(f"{UI.MAGENTA}{msg}{UI.RESET}")
    @staticmethod
    def separator(char='─', length=60, color=YELLOW): print(f"{color}{char * length}{UI.RESET}")

# ------------------------------------
#       CONFIGURACIÓN GLOBAL ÚNICA
# ------------------------------------
class Config:
    _instance = None
    FILE = "mexus_config.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        self.data = {
            "version": "",
            "type": "paper",
            "ram_min": "2G",
            "ram_max": "4G",
            "auto_backup": True,
            "auto_restart": True,
            "use_playit": True,
            "playit_path": "./playit-linux-amd64"
        }
        if os.path.exists(self.FILE):
            try:
                with open(self.FILE, 'r') as f:
                    self.data.update(json.load(f))
            except:
                pass
    
    def save(self):
        with open(self.FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        self.save()
    
    def is_valid(self):
        v = self.get('version', '')
        return v and v.strip() != ""

# ------------------------------------
#       DESCARGADOR
# ------------------------------------
class ServerDownloader:
    @staticmethod
    def get_versions(server_type):
        try:
            if server_type == "paper":
                r = requests.get("https://api.papermc.io/v2/projects/paper", timeout=10)
                versions = sorted(r.json()['versions'], reverse=True)
                versions = [v for v in versions if "1.1.1" <= v <= "1.21.11"]
                return versions
            elif server_type == "fabric":
                r = requests.get("https://meta.fabricmc.net/v2/versions/game", timeout=10)
                versions = [v['version'] for v in r.json() if v['stable']]
                versions = [v for v in versions if "1.1.1" <= v <= "1.21.11"]
                return sorted(versions, reverse=True)
            elif server_type == "vanilla":
                r = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest.json", timeout=10)
                versions = [v['id'] for v in r.json()['versions']]
                versions = [v for v in versions if "1.1.1" <= v <= "1.21.11"]
                return sorted(versions, reverse=True)
            elif server_type == "forge":
                r = requests.get("https://bmclapi2.bangbang93.com/forge/list", timeout=10)
                versions = sorted([v['version'] for v in r.json()], reverse=True)
                versions = [v for v in versions if v.split('-')[0] >= "1.1.1" and v.split('-')[0] <= "1.21.11"]
                return versions
        except Exception as e:
            UI.error(f"Error obteniendo versiones: {e}")
            return []
    
    @staticmethod
    def download(server_type, version, filename="server.jar"):
        try:
            url = None

            if server_type == "paper":
                build_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
                builds = requests.get(build_url, timeout=10).json()['builds']
                if not builds:
                    return False
                build = builds[-1]
                url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar"

            elif server_type == "fabric":
                # ✅ URL CORREGIDA: necesita loader + installer version
                meta_base = "https://meta.fabricmc.net/v2/versions"

                loader_resp = requests.get(f"{meta_base}/loader", timeout=10)
                loader_version = loader_resp.json()[0]['version']

                installer_resp = requests.get(f"{meta_base}/installer", timeout=10)
                installer_version = installer_resp.json()[0]['version']

                UI.info(f"Fabric loader: {loader_version} | installer: {installer_version}")
                url = f"{meta_base}/loader/{version}/{loader_version}/{installer_version}/server/jar"

            elif server_type == "vanilla":
                manifest = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest.json", timeout=10).json()
                for v in manifest['versions']:
                    if v['id'] == version:
                        pkg = requests.get(v['url'], timeout=10).json()
                        url = pkg['downloads']['server']['url']
                        break

            elif server_type == "forge":
                url = f"https://files.minecraftforge.net/net/minecraftforge/forge/{version}/forge-{version}-installer.jar"

            if not url:
                UI.error("No se pudo construir la URL de descarga")
                return False

            UI.info(f"Descargando {server_type} {version}...")
            UI.info(f"URL: {url}")

            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                pct = int(downloaded / total * 100)
                                print(f"\r  {UI.CYAN}Descargando... {pct}%{UI.RESET}", end='', flush=True)
            print()

            # Verificar que el archivo tiene contenido real
            size = os.path.getsize(filename)
            if size < 10000:
                UI.error(f"El archivo descargado es muy pequeño ({size} bytes), puede estar corrupto")
                return False

            UI.success(f"Descarga completa ({size // 1024} KB)")
            return True

        except Exception as e:
            UI.error(f"Error descargando: {e}")
            return False

# ------------------------------------
#       GESTOR PLAYIT
# ------------------------------------
class PlayitManager:
    def __init__(self, config):
        self.config = config
        self.process = None
        self.log_file = "playit.log"

    def start(self):
        playit_path = self.config.get('playit_path', './playit-linux-amd64')

        if not os.path.exists(playit_path):
            UI.warning(f"⚠ No se encontró playit en '{playit_path}'. Omitiendo...")
            return False

        if not os.access(playit_path, os.X_OK):
            os.chmod(playit_path, 0o755)

        try:
            UI.info(f"🌐 Iniciando playit en segundo plano...")

            # ✅ Output redirigido a archivo de log — NO toca la terminal
            log_fd = open(self.log_file, 'w')
            self.process = subprocess.Popen(
                [playit_path],
                stdout=log_fd,
                stderr=log_fd,
                stdin=subprocess.DEVNULL,   # sin input
                start_new_session=True       # proceso completamente separado del grupo
            )
            time.sleep(1)

            if self.process.poll() is not None:
                UI.error("Playit terminó inesperadamente. Revisa playit.log")
                return False

            UI.success(f"✅ Playit corriendo (PID: {self.process.pid}) → log en playit.log")
            return True

        except Exception as e:
            UI.error(f"Error iniciando playit: {e}")
            return False

    def stop(self):
        if self.process and self.process.poll() is None:
            UI.info("Deteniendo playit...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            UI.success("Playit detenido")

# ------------------------------------
#       GESTOR DEL SERVIDOR
# ------------------------------------
class ServerManager:
    def __init__(self):
        self.config = Config()
        self.process = None
        self.playit = PlayitManager(self.config)

    def start(self):
        self.config._load()

        if not self.config.is_valid():
            UI.error("No hay versión configurada")
            UI.info("Ve a 'Cambiar Versión/Tipo' primero (opción 2)")
            return False

        version = self.config.get('version')
        server_type = self.config.get('type')

        if not os.path.exists("server.jar"):
            UI.info("Descargando servidor...")
            if not ServerDownloader.download(server_type, version):
                UI.error("No se pudo descargar el servidor")
                return False

        if server_type == "forge":
            UI.info("Instalando Forge...")
            try:
                subprocess.run(["java", "-jar", "server.jar", "--installServer"], check=True)
                jars = glob.glob("forge-*-universal.jar")
                if jars:
                    os.rename(jars[0], "server.jar")
                else:
                    UI.error("No se pudo encontrar el jar del servidor Forge")
                    return False
            except subprocess.CalledProcessError:
                UI.error("Error instalando Forge")
                return False

        if not os.path.exists("eula.txt"):
            with open("eula.txt", "w") as f:
                f.write("eula=true\n")

        # ✅ Crear carpeta de logs si no existe
        if not os.path.exists("server_logs"):
            os.makedirs("server_logs")

        # ✅ Auto-restart loop
        auto_restart = self.config.get('auto_restart', False)
        restart_count = 0
        
        # ✅ Iniciar playit solo UNA VEZ en modo background (si está habilitado)
        use_playit = self.config.get('use_playit', True)
        if use_playit:
            UI.warning(f"ℹ️  Playit está configurado para usar. ")
            UI.warning(f"    Si quieres ejecutarlo de forma independiente:")
            UI.warning(f"    Terminal 1: ./start-playit.sh")
            UI.warning(f"    Terminal 2: ./watch-playit.sh")
            UI.warning(f"    El servidor se ejecutará sin intentar iniciar playit.")
            time.sleep(2)
        
        while True:
            restart_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            UI.info(f"[{timestamp}] Iniciando servidor (intento {restart_count})")

            args = [
                f"-Xms{self.config.get('ram_min')}",
                f"-Xmx{self.config.get('ram_max')}",
                "-XX:+UseG1GC",
                "-jar", "server.jar", "nogui"
            ]

            UI.success(f"Iniciando {server_type} {version}")
            self.process = subprocess.Popen(
                ["java"] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            threading.Thread(target=self._read_output, daemon=True).start()

            # ✅ Detectar si hay entrada interactiva
            is_interactive = sys.stdin.isatty()
            
            if is_interactive:
                # Modo interactivo: aceptar comandos
                # ✅ LISTA NEGRA DE COMANDOS PELIGROSOS
                dangerous_commands = [
                    "op",
                    "deop",
                    "gamemode",
                    "give",                    
                    "reload",
                    "pex",
                    "lp",
                    "luckperms",
                    "minecraft:op",
                    "minecraft:deop",
                    "minecraft:gamemode",
                    "minecraft:give",
                    "minecraft:reload"
                ]
                
                # ✅ CARACTERES PELIGROSOS
                dangerous_chars = ["|", ";", "&", ">", "<"]
                
                try:
                    while True:
                        try:
                            cmd = input()

                            if self.process.poll() is None:
                                # ✅ LIMPIAR COMANDO
                                clean_cmd = cmd.strip().lower()
                                blocked = False

                                # ------------------------------------
                                # BLOQUEAR CARACTERES PELIGROSOS
                                # ------------------------------------
                                for char in dangerous_chars:
                                    if char in clean_cmd:
                                        blocked = True
                                        UI.warning(f"⛔ Caracter peligroso detectado: {char}")
                                        break

                                # ------------------------------------
                                # BLOQUEAR COMANDOS PELIGROSOS
                                # ------------------------------------
                                if not blocked:
                                    for dc in dangerous_commands:
                                        if (
                                            clean_cmd == dc or
                                            clean_cmd.startswith(dc + " ") or
                                            clean_cmd == "/" + dc or
                                            clean_cmd.startswith("/" + dc + " ")
                                        ):
                                            blocked = True
                                            UI.warning(f"⛔ Comando bloqueado: {cmd}")
                                            break

                                # ------------------------------------
                                # ENVIAR COMANDO AL SERVIDOR
                                # ------------------------------------
                                if not blocked:
                                    self.process.stdin.write(cmd + "\n")
                                    self.process.stdin.flush()
                            else:
                                UI.warning("⚠ El servidor ya no está corriendo")
                                break
                        except EOFError:
                            UI.warning("Terminal cerrada")
                            break
                except KeyboardInterrupt:
                    UI.info("\n⏹ Deteniendo completamente el servidor...")
                    break
                
                # Apagado graceful del servidor (modo interactivo)
                if self.process and self.process.poll() is None:
                    try:
                        UI.info("🛑 Deteniendo servidor...")
                        self.process.stdin.write("stop\n")
                        self.process.stdin.flush()
                    except:
                        pass

                time.sleep(5)

                if self.process and self.process.poll() is None:
                    UI.warning("Forzando terminación del servidor...")
                    self.process.terminate()
                    time.sleep(2)
                    if self.process.poll() is None:
                        self.process.kill()

                self.process.wait()
                
                # Verificar en modo interactivo si hace auto-restart
                if not auto_restart:
                    break
                
                # Esperar antes de reiniciar
                UI.warning(f"⏳ Auto-restart en 10 segundos (reinicio #{restart_count})")
                time.sleep(10)
            else:
                # Modo background: solo esperar infinitamente
                UI.info("🔄 Servidor ejecutándose en background (escuchando forever)")
                self.process.wait()  # Esperar a que el proceso termine
                
                # Si llegó aquí, el servidor terminó (crash o comando stop)
                if auto_restart:
                    UI.warning(f"⏳ Auto-restart en 10 segundos (reinicio #{restart_count})")
                    time.sleep(10)
                else:
                    break  # Salir si auto_restart está deshabilitado

        UI.success("Servidor detenido completamente")
        return True

    def _read_output(self):
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    print(line, end='')
            except:
                break

# ------------------------------------
#       MENÚ PRINCIPAL
# ------------------------------------
def main():
    config = Config()
    manager = ServerManager()

    # ✅ Detectar si hay terminal interactiva
    import sys
    is_interactive = sys.stdin.isatty()

    if not is_interactive:
        # Si se ejecuta con nohup/background, iniciar directamente sin menú
        UI.info("🔧 Ejecutando en modo background (sin terminal)")
        if config.is_valid():
            manager.start()
        else:
            UI.error("❌ No hay versión configurada en mexus_config.json")
            UI.info("Configura el servidor primero ejecutando: python3 mc.py")
            sys.exit(1)
        return

    # --- MODO INTERACTIVO ---
    print(UI.banner())
    print()

    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        config._load()

        version_str = f"{config.get('type').upper()} {config.get('version')}" if config.is_valid() else "No configurado"
        status = "✅ Configurado" if config.is_valid() else "❌ Falta configurar"
        playit_status = "Sí" if config.get('use_playit') else "No"

        header = f"""  🎮  MEXUS.PY - Server Manager v2.1
  {status}
  
  📦 {version_str}
  💾 RAM: {config.get('ram_min')} - {config.get('ram_max')}
  🌐 Playit: {playit_status}
  🔄 Auto-restart: {'Sí' if config.get('auto_restart') else 'No'}"""

        print(UI.box(header))
        print()

        options = [
            ("1", "Iniciar Servidor", UI.GREEN),
            ("2", "Cambiar Versión/Tipo", UI.CYAN),
            ("3", "Configurar RAM", UI.YELLOW),
            ("4", "Configurar Playit", UI.PURPLE),
            ("0", "Salir", UI.RED)
        ]

        for num, text, color in options:
            print(f"  {color}{num}.{UI.RESET} {text}")
        print()

        choice = input(f"{UI.MAGENTA}➤ Selecciona: {UI.RESET}").strip()

        if choice == "1":
            if not config.is_valid():
                UI.error("❌ No hay versión configurada")
                UI.info("ℹ Ve a 'Cambiar Versión/Tipo' primero (opción 2)")
                input(f"\n{UI.CYAN}Presiona Enter para continuar...{UI.RESET}")
            else:
                manager.start()
                input(f"\n{UI.CYAN}Presiona Enter para continuar...{UI.RESET}")

        elif choice == "2":
            UI.separator()
            print(f"{UI.CYAN}Tipos disponibles: paper, fabric, vanilla, forge{UI.RESET}")
            t = input(f"{UI.MAGENTA}Tipo (default paper): {UI.RESET}").strip() or "paper"
            config.set('type', t)

            versions = ServerDownloader.get_versions(t)
            if versions:
                print(f"\n{UI.YELLOW}Versiones disponibles:{UI.RESET}")
                UI.separator('─', 40, UI.BLUE)
                for i, v in enumerate(versions[:20], 1):
                    print(f"  {UI.CYAN}{i:2d}.{UI.RESET} {v}")
                UI.separator('─', 40, UI.BLUE)
                try:
                    idx = int(input(f"{UI.MAGENTA}Número de versión: {UI.RESET}")) - 1
                    if 0 <= idx < len(versions):
                        config.set('version', versions[idx])
                        if os.path.exists("server.jar"):
                            os.remove("server.jar")
                        UI.success(f"✅ Configurado: {t.upper()} {versions[idx]}")
                    else:
                        UI.error("Número inválido")
                except ValueError:
                    UI.error("Entrada inválida")
            else:
                UI.error("No se pudieron obtener las versiones")
            time.sleep(2)

        elif choice == "3":
            UI.separator()
            print(f"{UI.YELLOW}Configuración de RAM{UI.RESET}")
            print(f"  {UI.GREEN}1.{UI.RESET} 2G - 4G (Pequeño)")
            print(f"  {UI.GREEN}2.{UI.RESET} 4G - 8G (Mediano)")
            print(f"  {UI.GREEN}3.{UI.RESET} Personalizado")
            UI.separator()
            p = input(f"{UI.MAGENTA}Opción: {UI.RESET}").strip()
            if p == "1":
                config.set('ram_min', "2G"); config.set('ram_max', "4G")
                UI.success("RAM: 2G - 4G")
            elif p == "2":
                config.set('ram_min', "4G"); config.set('ram_max', "8G")
                UI.success("RAM: 4G - 8G")
            elif p == "3":
                min_ram = input(f"{UI.MAGENTA}RAM mínima (ej: 2G): {UI.RESET}").strip()
                max_ram = input(f"{UI.MAGENTA}RAM máxima (ej: 4G): {UI.RESET}").strip()
                if min_ram and max_ram:
                    config.set('ram_min', min_ram); config.set('ram_max', max_ram)
                    UI.success(f"RAM: {min_ram} - {max_ram}")
                else:
                    UI.error("Configuración inválida")
            time.sleep(2)

        elif choice == "4":
            UI.separator()
            print(f"{UI.PURPLE}Configuración de Playit{UI.RESET}")
            print(f"  Estado actual: {'Activado' if config.get('use_playit') else 'Desactivado'}")
            print(f"  Path actual: {config.get('playit_path')}")
            print()
            print(f"  {UI.GREEN}1.{UI.RESET} Activar/Desactivar playit")
            print(f"  {UI.GREEN}2.{UI.RESET} Cambiar ruta del ejecutable")
            UI.separator()
            p = input(f"{UI.MAGENTA}Opción: {UI.RESET}").strip()
            if p == "1":
                current = config.get('use_playit', True)
                config.set('use_playit', not current)
                UI.success(f"Playit {'activado' if not current else 'desactivado'}")
            elif p == "2":
                path = input(f"{UI.MAGENTA}Ruta del ejecutable (ej: ./playit-linux-amd64): {UI.RESET}").strip()
                if path:
                    config.set('playit_path', path)
                    UI.success(f"Ruta actualizada: {path}")
            time.sleep(2)

        elif choice == "0":
            UI.highlight("👋 ¡Hasta luego! Gracias por usar MEXUS.PY")
            break

        else:
            UI.error("Opción inválida")
            time.sleep(1)

if __name__ == "__main__":
    main()
