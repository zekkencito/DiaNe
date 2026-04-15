"""
INICIAR DAYAN - Launcher Ejecutable
====================================
Arranca jarvis.py en segundo plano sin consola.
El splash de tkinter corre en el hilo PRINCIPAL (obligatorio en Windows).
"""

import subprocess
import sys
import os
import time
import threading
import socket
from pathlib import Path

# ──────────────────────────────────────────────
#  Rutas base (funciona tanto como .py como .exe)
# ──────────────────────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

JARVIS_SCRIPT = BASE_DIR / "jarvis.py"
PYTHON_EXE    = BASE_DIR / ".venv" / "Scripts" / "python.exe"

if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)


# ──────────────────────────────────────────────
#  Utilidades
# ──────────────────────────────────────────────
# Objeto de proceso global para monitoreo
PROCESO_JARVIS = None
SINGLE_INSTANCE_SOCKET = None

def limpiar_temporales():
    for nombre in ["comando_gui.txt", "voz_estado.txt", "desactivar_protocolos.txt", "dayan_pausado.txt", "forzar_escucha.txt"]:
        ruta = BASE_DIR / nombre
        if ruta.exists():
            try:
                ruta.unlink()
            except Exception:
                pass


def adquirir_bloqueo_instancia():
    """Evita abrir múltiples instancias simultáneas de DiaNe."""
    global SINGLE_INSTANCE_SOCKET
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 52991))
        sock.listen(1)
        SINGLE_INSTANCE_SOCKET = sock
        return True
    except OSError:
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk(); root.withdraw()
            messagebox.showinfo("DiaNe", "DiaNe ya está ejecutándose.")
            root.destroy()
        except Exception:
            pass
        return False


def lanzar_jarvis():
    """Lanza jarvis.py SILENCIOSAMENTE sin consola visible"""
    global PROCESO_JARVIS
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Logs a archivo para debugging
        log_file = open(BASE_DIR / "_jarvis_runtime.log", "a", encoding="utf-8")
        
        # CREATE_NO_WINDOW = No aparece la terminal
        PROCESO_JARVIS = subprocess.Popen(
            [str(PYTHON_EXE), str(JARVIS_SCRIPT)],
            cwd=str(BASE_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            env=env
        )
        print("[✓] Motor DiaNe iniciado silenciosamente (solo web visible)")
    except Exception as e:
        (BASE_DIR / "_launch_error.txt").write_text(str(e), encoding="utf-8")


# ──────────────────────────────────────────────
#  Splash — corre en el HILO PRINCIPAL
# ──────────────────────────────────────────────
def mostrar_splash():
    import tkinter as tk

    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="#0a0a14")
    splash.attributes("-topmost", True)
    splash.attributes("-alpha", 0.0)

    ancho, alto = 430, 230
    x = (splash.winfo_screenwidth()  - ancho) // 2
    y = (splash.winfo_screenheight() - alto)  // 2
    splash.geometry(f"{ancho}x{alto}+{x}+{y}")

    # ── Borde brillante simulado ──
    borde = tk.Frame(splash, bg="#00ff88", bd=1)
    borde.place(x=0, y=0, width=ancho, height=alto)

    interior = tk.Frame(borde, bg="#0a0a14")
    interior.place(x=1, y=1, width=ancho-2, height=alto-2)

    # ── Contenido ──
    tk.Label(interior, text="DiaNe",
             font=("Courier", 34, "bold"),
             bg="#0a0a14", fg="#00ff88").pack(pady=(28, 0))

    tk.Label(interior, text="Asistente de Inteligencia Artificial",
             font=("Courier", 9),
             bg="#0a0a14", fg="#336699").pack()

    tk.Label(interior, text="Iniciando sistema...",
             font=("Courier", 8),
             bg="#0a0a14", fg="#444466").pack(pady=(14, 2))

    canvas = tk.Canvas(interior, width=320, height=6,
                       bg="#111133", highlightthickness=0)
    canvas.pack()
    barra = canvas.create_rectangle(0, 0, 0, 6, fill="#00ff88", width=0)

    tk.Label(interior, text="v9.0",
             font=("Courier", 7),
             bg="#0a0a14", fg="#222244").pack(side=tk.BOTTOM, pady=8)

    # ── Fade-in ──
    def fade_in(alpha=0.0):
        if alpha < 0.95:
            splash.attributes("-alpha", alpha)
            splash.after(15, fade_in, round(alpha + 0.05, 2))
        else:
            splash.attributes("-alpha", 0.95)

    # ── Barra de progreso ──
    def animar_barra(paso=0):
        if paso <= 160:
            canvas.coords(barra, 0, 0, paso * 2, 6)
            splash.after(12, animar_barra, paso + 2)
        else:
            # Cerrar splash con fade-out
            fade_out()

    def fade_out(alpha=0.95):
        if alpha > 0.0:
            splash.attributes("-alpha", alpha)
            splash.after(15, fade_out, round(alpha - 0.05, 2))
        else:
            splash.destroy()

    fade_in()
    splash.after(200, animar_barra)
    splash.mainloop()


# ──────────────────────────────────────────────
#  Punto de entrada
# ──────────────────────────────────────────────
def main():
    if not adquirir_bloqueo_instancia():
        return

    limpiar_temporales()

    # Verificar que jarvis.py existe antes de continuar
    if not JARVIS_SCRIPT.exists():
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk(); root.withdraw()
            messagebox.showerror(
                "DiaNe — Error",
                f"No se encontro jarvis.py en:\n{JARVIS_SCRIPT}"
            )
            root.destroy()
        except Exception:
            pass
        return

    # Lanzar SOLO el motor de Jarvis (interfaz web se abre automáticamente)
    t_jarvis = threading.Thread(target=lanzar_jarvis, daemon=True)
    t_jarvis.start()

    # Mostrar splash en el hilo principal (REQUERIDO por tkinter/Windows)
    mostrar_splash()

    # Si hubo error al lanzar, mostrarlo ahora
    err_file = BASE_DIR / "_launch_error.txt"
    if err_file.exists():
        msg = err_file.read_text(encoding="utf-8")
        err_file.unlink()
        _mostrar_error_final(msg)
        return

    # --- NUEVO: Heartbeat check ---
    # Después del splash (~2.5s), verificamos si los procesos siguen vivos
    time.sleep(1.0) 
    if PROCESO_JARVIS and PROCESO_JARVIS.poll() is not None:
        # El proceso del motor murió
        log_hint = ""
        log_file = BASE_DIR / "_jarvis_debug.log"
        if log_file.exists():
            try:
                lineas = log_file.read_text(encoding="utf-8").splitlines()
                if lineas:
                    log_hint = "\n\nÚltimas líneas del log:\n" + "\n".join(lineas[-5:])
            except:
                pass
        
        _mostrar_error_final(
            f"El motor de DiaNe se cerró inesperadamente tras iniciar.{log_hint}\n\n"
            "Verifica que no haya otras instancias abiertas y que el entorno virtual sea válido."
        )


def _mostrar_error_final(mensaje):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("DiaNe - Error de Ejecucion", mensaje)
        root.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    main()
