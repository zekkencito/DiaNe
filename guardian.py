import psutil
import time
import subprocess
from pathlib import Path

# Variables de control
proceso_dayan = None
BASE_DIR = Path(__file__).parent

def matar_procesos():
    print("[Guardián]: Batería detectada. Apagando micrófono y desactivando a Dayan para ahorrar energía...")
    global proceso_dayan
    if proceso_dayan is not None:
        proceso_dayan.terminate()
        proceso_dayan = None

print("Guardián de Dayan iniciado. Monitoreando energía...")

while True:
    try:
        bateria = psutil.sensors_battery()
        if bateria is None:
            time.sleep(5)
            continue
            
        enchufado = bateria.power_plugged

        # ESCENARIO 1: Acabas de enchufar la laptop
        if enchufado and proceso_dayan is None:
            print("[Guardián]: Corriente alterna detectada. Despertando a Dayan...")
            # Arrancamos el EXE directamente
            dayan_exe = BASE_DIR / "Dayan.exe"
            if dayan_exe.exists():
                proceso_dayan = subprocess.Popen([str(dayan_exe)], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                print(f"[!] Dayan.exe no encontrado en {dayan_exe}")

        # ESCENARIO 2: Acabas de desenchufar la laptop
        elif not enchufado and proceso_dayan is not None:
            matar_procesos()

    except Exception as e:
        print(f"[Error en Guardián]: {e}")

    # Duerme 3 segundos para que este mismo script no consuma nada de procesador
    time.sleep(3)