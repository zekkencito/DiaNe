"""
COMPILAR EXE - Genera Dayan.exe con ícono personalizado
=========================================================
Ejecuta este script UNA VEZ para generar el ejecutable.
Requiere: pip install pyinstaller pillow
"""

import subprocess
import sys
import os
from pathlib import Path

BASE_DIR    = Path(__file__).parent
ICON_PNG    = BASE_DIR / "dayan_icon.png"
ICON_ICO    = BASE_DIR / "dayan_icon.ico"
LAUNCHER    = BASE_DIR / "iniciar_dayan.py"
EXE_NOMBRE  = "Dayan"

# ──────────────────────────────────────────────
#  PASO 1: Convertir PNG → ICO
# ──────────────────────────────────────────────
def convertir_icono():
    print("─" * 50)
    print("[1/3] Convirtiendo ícono PNG → ICO ...")
    try:
        from PIL import Image
        img = Image.open(ICON_PNG).convert("RGBA")
        # Generar múltiples tamaños para un .ico correcto en Windows
        sizes = [(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)]
        imgs  = [img.resize(s, Image.LANCZOS) for s in sizes]
        imgs[0].save(ICON_ICO, format="ICO", sizes=[(s[0], s[1]) for s in sizes],
                     append_images=imgs[1:])
        print(f"    ✓ Ícono generado: {ICON_ICO.name}")
        return True
    except ImportError:
        print("    [!] Pillow no instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "-q"], check=True)
        return convertir_icono()
    except FileNotFoundError:
        print(f"    [!] No se encontró {ICON_PNG.name}")
        print("        Copiando un ícono alternativo del sistema...")
        ICON_ICO_ALT = Path(os.environ.get("WINDIR","C:/Windows")) / "System32" / "shell32.dll"
        return False

# ──────────────────────────────────────────────
#  PASO 2: Instalar PyInstaller si falta
# ──────────────────────────────────────────────
def verificar_pyinstaller():
    print("─" * 50)
    print("[2/3] Verificando PyInstaller ...")
    try:
        import PyInstaller
        print(f"    ✓ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("    [!] PyInstaller no encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"], check=True)
        print("    ✓ PyInstaller instalado")

# ──────────────────────────────────────────────
#  PASO 3: Compilar el .exe
# ──────────────────────────────────────────────
def compilar():
    print("─" * 50)
    print("[3/3] Compilando Dayan.exe ...")
    
    icono_arg = f"--icon={ICON_ICO}" if ICON_ICO.exists() else ""

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",               # Todo en un solo .exe
        "--windowed",              # SIN ventana de consola
        "--name", EXE_NOMBRE,
        "--distpath", str(BASE_DIR),   # Poner el .exe en la carpeta del proyecto
        "--workpath", str(BASE_DIR / "build_tmp"),
        "--specpath", str(BASE_DIR / "build_tmp"),
        "--clean",
        "--noconfirm",
    ]

    if icono_arg:
        cmd.append(icono_arg)

    cmd.append(str(LAUNCHER))

    resultado = subprocess.run(cmd, cwd=str(BASE_DIR))

    if resultado.returncode == 0:
        exe_path = BASE_DIR / f"{EXE_NOMBRE}.exe"
        print("\n" + "═" * 50)
        print(f"  ✅  ¡Dayan.exe generado exitosamente!")
        print(f"  📁  Ubicación: {exe_path}")
        print("═" * 50)
        crear_acceso_directo(exe_path)
    else:
        print("\n  ❌  La compilación falló. Revisa los errores arriba.")

# ──────────────────────────────────────────────
#  PASO 4 (opcional): Crear acceso directo
# ──────────────────────────────────────────────
def crear_acceso_directo(exe_path: Path):
    escritorio = Path.home() / "Desktop"
    shortcut   = escritorio / "Dayan.lnk"
    
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        # winshell no disponible, usar pywin32 directo
        try:
            from win32com.client import Dispatch
        except ImportError:
            print("\n  [i] Para crear el acceso directo manualmente:")
            print(f"      Clic derecho en el escritorio → Nuevo → Acceso directo")
            print(f"      Destino: {exe_path}")
            return

    try:
        shell    = Dispatch("WScript.Shell")
        link     = shell.CreateShortCut(str(shortcut))
        link.Targetpath   = str(exe_path)
        link.WorkingDirectory = str(exe_path.parent)
        link.Description  = "DiaNe - Asistente de IA"
        if ICON_ICO.exists():
            link.IconLocation = str(ICON_ICO)
        link.save()
        print(f"\n  🖥️   Acceso directo creado en el Escritorio: {shortcut.name}")
    except Exception as e:
        print(f"\n  [i] No se pudo crear el acceso directo automáticamente: {e}")
        print(f"      Puedes hacerlo manualmente apuntando a: {exe_path}")


if __name__ == "__main__":
    print("\n" + "═" * 50)
    print("    COMPILADOR DE DAYAN.EXE")
    print("═" * 50)

    icono_ok = convertir_icono()
    verificar_pyinstaller()
    compilar()
