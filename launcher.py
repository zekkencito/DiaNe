"""
LAUNCHER - Inicia Jarvis con GUI + Voz en paralelo
Ejecuta:
1. jarvis_gui.py (interfaz gráfica)
2. jarvis.py (motor de voz + IA en background)
"""

import subprocess
import os
import sys
import time
from pathlib import Path

def limpiar_archivos_temporales():
    """Limpia archivos temporales de sesiones anteriores"""
    archivos_temp = ["comando_gui.txt", "voz_estado.txt", "respuesta.mp3"]
    for archivo in archivos_temp:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
            except:
                pass

def iniciar_jarvis_dual():
    """Inicia GUI y Jarvis en procesos separados"""
    print("=" * 60)
    print("🤖 JARVIS v9.0 - MODO DUAL (GUI + VOZ)")
    print("=" * 60)
    print("[+] Iniciando interfaz gráfica...")
    print("[+] Iniciando motor de voz...")
    print()
    
    limpiar_archivos_temporales()
    
    # Obtener rutas del script actual
    script_dir = Path(__file__).parent
    gui_script = script_dir / "jarvis_gui.py"
    jarvis_script = script_dir / "jarvis.py"
    
    procesos = []
    
    try:
        # Spawnear GUI en proceso separado (mantiene la terminal de jarvis limpia)
        print("[✓] Abriendo GUI...")
        p_gui = subprocess.Popen(
            [sys.executable, str(gui_script)],
            cwd=str(script_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        procesos.append(("GUI", p_gui))
        
        time.sleep(1)
        
        # Ejecutar Jarvis (voz + IA) en el proceso principal
        print("[✓] Iniciando Jarvis (presiona CTRL+C para salir)...")
        print()
        
        subprocess.run(
            [sys.executable, str(jarvis_script)],
            cwd=str(script_dir)
        )
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⚫ Apagando Jarvis...")
        for nombre, proc in procesos:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
        print("✓ Todos los procesos cerrados")
        print("=" * 60)
        
    except Exception as e:
        print(f"[!] Error: {e}")
        for nombre, proc in procesos:
            try:
                proc.kill()
            except:
                pass

if __name__ == "__main__":
    iniciar_jarvis_dual()
