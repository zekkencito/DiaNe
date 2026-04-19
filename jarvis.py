import sys
import requests
import json
import os
import urllib.parse
import re
import time
import random
import pyautogui
import speech_recognition as sr
import pywhatkit
import pyttsx3
import screeninfo
import asyncio
import edge_tts
import pygame
import winreg
import subprocess
import uuid
import ctypes
import psutil
import platform as sys_platform
import pyaudio
import numpy as np
# Import de openwakeword eliminado
from datetime import datetime
from pathlib import Path
from threading import Thread
import base64
from io import BytesIO

# --- FIX ENCODING AT START ---
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

import memoria_manager
import servidor_holografico

# Hotkey listener
try:
    from pynput import keyboard
    PYNPUT_DISPONIBLE = True
except ImportError:
    PYNPUT_DISPONIBLE = False
    keyboard = None

# Groq API (ULTRA-RÁPIDO)
try:
    from groq import Groq
    GROQ_DISPONIBLE = True
except ImportError:
    GROQ_DISPONIBLE = False
    Groq = None

# Detección de palabra clave OFFLINE (Pocketsphinx)
try:
    from pocketsphinx import LiveSpeech
    POCKETSPHINX_DISPONIBLE = True
except ImportError:
    POCKETSPHINX_DISPONIBLE = False
    LiveSpeech = None

try:
    import wikipedia
except ImportError:
    wikipedia = None
try:
    import feedparser
except ImportError:
    feedparser = None
try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Historial de conversaciones y estados
historial = []
modo_gaming = False
navegador_movido = False
cache_programas = {}
perfil_usuario = {}
# Flags para control de voz
debe_interrumpir = False  # Flag para interrumpir mientras habla
esta_hablando = False     # Flag para saber si Dayan está hablando
voz_pausada = False       # Flag para pausar voz (F8)
forzar_escucha = False    # Flag para forzar escucha con hotkey (F9)
pygame_mixer_silenciado = False  # Flag para silenciar audio completamente (F7)
modo_dictado_vscode = False  # Dictado continuo hacia VSCode/chat
modo_reposo_manual = False   # Reposo persistente hasta comando explícito de reactivación
tiempo_fin_hablar = 0     # Timestamp de cuando Dayan termina de hablar (para ventana activa)
dictado_borrador = ""
esperando_confirmacion_envio = False
AUTO_ESCUCHA_FORZADA_AL_INICIAR = True  # Activa una escucha tipo F9 al arrancar
ANCLAR_VENTANA_UI = True                # Bloquea posición/tamaño de la ventana web
UI_POS_X = 30
UI_POS_Y = 20
UI_ANCHO = 520
UI_ALTO = 860
CONTEXT_MSG_WINDOW = 30         # Mensajes recientes enviados al modelo
CONTEXT_SUMMARY_WINDOW = 30     # Mensajes recientes para resumen textual en prompt
SESSION_CACHE_WINDOW = 100      # Mensajes guardados al cerrar sesión
CONVERSATION_MODEL = "llama-3.3-70b-versatile"
CONVERSATION_TEMPERATURE = 0.28
CACHE_FILE = "cache_programas.json"
LOG_FILE = "jarvis.log"
PROFILE_FILE = "perfil_usuario.json"
HISTORIAL_FILE_PREFIX = "historial_"

# PERFIL COMPLETO DEL USUARIO - RENZO
PERFIL_RENZO = {
    "nombre": "Renzo",
    "edad": 25,
    "origen": "Perú",
    "ubicacion_actual": "México",
    "educacion": "8vo semestre - Ingeniería en Sistemas Computacionales (ITSNCG)",
    "skills_tech": ["HTML", "Three.js", "n8n", "React Native", "Laravel"],
    "intereses_tech": ["Ciberseguridad (autodidacta, planea maestría en España)"],
    "hardware": "Laptop Legion Slim 5 (actualizada: SSD 2TB)",
    "juegos_favoritos": [
        "Persona 5 Royal",
        "Spider-Man 2",
        "The Witcher 3",
        "Fallout 3",
        "Fallout 76",
        "Watch Dogs: Legion",
        "Metal Gear Solid"
    ],
    "generos_gaming": ["RPG", "Mundo abierto", "Sigilo"],
    "hobbies": [
        "Reparación y modificación de consolas clásicas (PSP modificada, planea PS Vita)",
        "Entrenamiento en casa para ganancia muscular",
        "Anime (Jujutsu Kaisen)",
        "Dibujo con estilógrafos",
        "Creación/edición de videos gaming para TikTok"
    ],
    "rol": "Gamer, Creador de contenido, Desarrollador"
}

# --- PATH CONFIG FOR EXE ---
if getattr(sys, "frozen", False):
    BASE_DIR_JARVIS = Path(sys.executable).parent
else:
    BASE_DIR_JARVIS = Path(__file__).parent

LOG_FILE = str(BASE_DIR_JARVIS / "jarvis.log")
PROFILE_FILE = str(BASE_DIR_JARVIS / "perfil_usuario.json")
CACHE_FILE = str(BASE_DIR_JARVIS / "cache_programas.json")

# Carpeta temporal para archivos MP3
MP3_TEMP_DIR = str(BASE_DIR_JARVIS / "temp_mp3")
if not os.path.exists(MP3_TEMP_DIR):
    os.makedirs(MP3_TEMP_DIR)

# Configuración de Groq API (ULTRA-RÁPIDO - Hardware acelerador dedicado)
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if GROQ_DISPONIBLE and GROQ_API_KEY:
    try:
        client_groq = Groq(api_key=GROQ_API_KEY)
        print("[INFO] Groq API configurada (ULTRA-RAPIDO - Hardware acelerador Groq activado)")
    except Exception as e:
        print(f"[ADVERTENCIA] Error configurando Groq: {e}")
        GROQ_DISPONIBLE = False
        client_groq = None
else:
    client_groq = None
    if not GROQ_DISPONIBLE:
        print("[ADVERTENCIA] Groq no está instalado")

# Shortcuts que ejecutan sin IA
shortcuts = {
    "apaga": "cerrar",
    "cierra": "cerrar",
    "sal": "cerrar",
    "termina": "cerrar",
    "cierre": "cerrar",
    "desactívate": "dormir",
    "desactivate": "dormir",
    "desactiva": "dormir",
    "duerme": "dormir",
    "ve a dormir": "dormir",
    "descansa": "dormir",
    "silencio": "dormir",
    "duérmete": "dormir",
    "música": "youtube música",
    "play": "playpause",
    "pausa": "playpause",
    "siguiente": "nexttrack"
}

FRASES_REACTIVAR = [
    "despierta",
    "reactivate",
    "reactívate",
    "reactiva",
    "reanuda",
    "wake up",
    "hola dayan",
    "diane despierta",
    "dayan despierta",
]

def iniciar_anclaje_ventana_ui(titulo="DiaNe OS"):
    """Mantiene la ventana UI en una posición fija mientras no esté minimizada."""
    if not ANCLAR_VENTANA_UI:
        return

    def _worker():
        try:
            user32 = ctypes.windll.user32
            SWP_NOZORDER = 0x0004
            SWP_NOACTIVATE = 0x0010
            SWP_NOSENDCHANGING = 0x0400
            flags = SWP_NOZORDER | SWP_NOACTIVATE | SWP_NOSENDCHANGING

            while True:
                hwnd = user32.FindWindowW(None, titulo)
                if hwnd:
                    # Si está minimizada no forzamos movimiento
                    if not user32.IsIconic(hwnd):
                        user32.SetWindowPos(hwnd, 0, UI_POS_X, UI_POS_Y, UI_ANCHO, UI_ALTO, flags)
                elif gw:
                    # Fallback: buscar ventana por título parcial en caso de variaciones del navegador
                    try:
                        ventanas = gw.getAllWindows()
                        for v in ventanas:
                            t = (v.title or "").lower()
                            if "diane os" in t or "dayan" in t:
                                if not v.isMinimized:
                                    v.moveTo(UI_POS_X, UI_POS_Y)
                                    v.resizeTo(UI_ANCHO, UI_ALTO)
                                break
                    except Exception:
                        pass
                time.sleep(0.35)
        except Exception:
            pass

    Thread(target=_worker, daemon=True).start()

def buscar_programa(nombre_buscado):
    global cache_programas
    
    buscado_limpio = re.sub(r'[^a-z0-9\s]', '', str(nombre_buscado).lower())
    palabras_clave = [palabra for palabra in buscado_limpio.split() if len(palabra) > 2 or palabra.isdigit()]
    
    if not palabras_clave:
        return None 
    
    # 0. BÚSQUEDA ESPECIAL PARA APLICACIONES COMUNES
    apps_comunes = {
        "obs": [
            r"C:\Program Files\obs-studio\bin\64bit\obs.exe",
            r"C:\Program Files (x86)\obs-studio\bin\64bit\obs.exe",
            r"C:\Program Files\obs-studio\bin\32bit\obs.exe",
        ],
        "vscode": [
            r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
    }
    
    for app_key, rutas_alternativas in apps_comunes.items():
        if any(palabra in buscado_limpio for palabra in [app_key]):
            for ruta_alt in rutas_alternativas:
                if os.path.exists(ruta_alt):
                    cache_programas[app_key.capitalize()] = ruta_alt
                    guardar_cache()
                    registrar_log("BÚSQUEDA APP COMÚN", nombre_buscado)
                    return ruta_alt
    
    # 1. BÚSQUEDA EN CACHÉ (instantánea)
    for programa, ruta in cache_programas.items():
        programa_limpio = re.sub(r'[^a-z0-9\s]', '', programa.lower())
        if all(palabra in programa_limpio for palabra in palabras_clave):
            registrar_log("BÚSQUEDA CACHÉ", nombre_buscado)
            return ruta
    
    # 2. BÚSQUEDA EN PROGRAM FILES
    program_files = [
        os.path.expandvars(r"%ProgramFiles%"),
        os.path.expandvars(r"%ProgramFiles(x86)%")
    ]
    
    for pf in program_files:
        if not os.path.exists(pf):
            continue
        for raiz, carpetas, archivos in os.walk(pf):
            if raiz.count(os.sep) - pf.count(os.sep) > 3:
                del carpetas[:]
                continue
            
            for archivo in archivos:
                if archivo.lower().endswith(".exe"):
                    if any(x in archivo.lower() for x in ["unins", "crash", "redist", "setup", "msi", "vcredist"]):
                        continue
                    
                    archivo_limpio = re.sub(r'[^a-z0-9\s]', '', archivo.rsplit(".", 1)[0].lower())
                    if all(palabra in archivo_limpio for palabra in palabras_clave):
                        ruta_programa = os.path.join(raiz, archivo)
                        cache_programas[archivo.rsplit(".", 1)[0]] = ruta_programa
                        guardar_cache()
                        registrar_log("BÚSQUEDA PROGRAM FILES", nombre_buscado)
                        return ruta_programa
    
    # 3. BÚSQUEDA EN REGISTRO DE WINDOWS
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        except:
            reg_key = None
        
        if reg_key:
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    subkey_name = winreg.EnumKey(reg_key, i)
                    subkey = winreg.OpenKey(reg_key, subkey_name)
                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0] if winreg.QueryValueEx(subkey, "InstallLocation") else ""
                    
                    display_limpio = re.sub(r'[^a-z0-9\s]', '', display_name.lower())
                    if all(palabra in display_limpio for palabra in palabras_clave) and install_location:
                        if os.path.exists(install_location):
                            for archivo in os.listdir(install_location):
                                if archivo.lower().endswith(".exe"):
                                    ruta_programa = os.path.join(install_location, archivo)
                                    cache_programas[display_name] = ruta_programa
                                    guardar_cache()
                                    registrar_log("BÚSQUEDA REGISTRO", nombre_buscado)
                                    return ruta_programa
                    winreg.CloseKey(subkey)
                except:
                    pass
            winreg.CloseKey(reg_key)
    except Exception as e:
        pass
    
    # 4. BÚSQUEDA EN ACCESOS DIRECTOS
    rutas_accesos = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%USERPROFILE%\Desktop"),
        os.path.expandvars(r"%PUBLIC%\Desktop")
    ]
    
    for ruta_base in rutas_accesos:
        if not os.path.exists(ruta_base):
            continue
        for raiz, _, archivos in os.walk(ruta_base):
            for archivo in archivos:
                if archivo.lower().endswith((".lnk", ".url")):
                    archivo_limpio = re.sub(r'[^a-z0-9\s]', '', archivo.rsplit(".", 1)[0].lower())
                    if all(palabra in archivo_limpio for palabra in palabras_clave):
                        ruta_programa = os.path.join(raiz, archivo)
                        cache_programas[archivo.rsplit(".", 1)[0]] = ruta_programa
                        guardar_cache()
                        registrar_log("BÚSQUEDA ACCESOS", nombre_buscado)
                        return ruta_programa
    
    # 5. BÚSQUEDA EN JUEGOS LOCALES
    rutas_juegos = [r"C:\Games", r"D:\Games"]
    
    for ruta_juego in rutas_juegos:
        if not os.path.exists(ruta_juego):
            continue
        for raiz, _, archivos in os.walk(ruta_juego):
            nombre_carpeta = re.sub(r'[^a-z0-9\s]', '', os.path.basename(raiz).lower())
            for archivo in archivos:
                if archivo.lower().endswith(".exe"):
                    if any(basura in archivo.lower() for basura in ["unins", "crash", "redist", "setup", "unity"]):
                        continue
                    archivo_limpio = re.sub(r'[^a-z0-9\s]', '', archivo.rsplit(".", 1)[0].lower())
                    texto_a_buscar = archivo_limpio + " " + nombre_carpeta
                    if all(palabra in texto_a_buscar for palabra in palabras_clave):
                        ruta_programa = os.path.join(raiz, archivo)
                        cache_programas[archivo.rsplit(".", 1)[0]] = ruta_programa
                        guardar_cache()
                        registrar_log("BÚSQUEDA JUEGOS", nombre_buscado)
                        return ruta_programa
    
    return None

def detectar_activacion_y_capturar_comando(ruta_modelo="hey_jarvis_v0.1.onnx"):
    import speech_recognition as sr
    import servidor_holografico
    servidor_holografico.cambiar_estado("Escuchando")
    print("\n   [Escucha]: Esperando palabra de activación 'Dayan'...")

    try:
        r_fb = sr.Recognizer()
        r_fb.energy_threshold = 1500  # MUY BAJO
        r_fb.dynamic_energy_threshold = True
        r_fb.pause_threshold = 3.0  # Más margen para pensar entre frases
        
        with sr.Microphone() as source_fb:
            print("   [Escucha]: Calibrando micrófono...")
            r_fb.adjust_for_ambient_noise(source_fb, duration=0.8)
            print(f"   [Escucha]: Threshold: {r_fb.energy_threshold:.0f}. Escuchando...")
            
            audio_fb = r_fb.listen(source_fb, timeout=25, phrase_time_limit=20)
            print(f"   [Escucha]: {len(audio_fb.frame_data)} bytes capturados. Procesando...")
            
            texto_fb = r_fb.recognize_google(audio_fb, language="es-ES").lower()
            print(f"   [Escucha]: Capturado: '{texto_fb}'")
            
            variantes = ["dayan", "dayanne", "deyan", "diana", "yana", "daya", "jarvis", "davis"]
            for var in variantes:
                if var in texto_fb:
                    print(f"   ✓ Activación confirmada por '{var}'")
                    partes = texto_fb.split(var, 1)
                    cmd = partes[1].strip() if len(partes) > 1 else ""
                    return (cmd or None, False)
            
            print("   [Escucha]: Palabra clave no reconocida, reintentando...")
            return (None, False)
            
    except sr.UnknownValueError:
        print("   [Escucha]: Audio no inteligible")
        return (None, False)
    except sr.RequestError as e:
        print(f"   [Escucha]: {e}")
        return (None, False)
    except Exception as e:
        print(f"   [Error Escucha]: {e}")
        return (None, False)

def diagnosticar_microfono():
    """Diagnostica el estado del micrófono"""
    print("\n" + "=" * 60)
    print("🔧 DIAGNÓSTICO DE MICRÓFONO")
    print("=" * 60)
    
    try:
        p = pyaudio.PyAudio()
        print(f"✓ PyAudio disponible")
        print(f"  Dispositivos encontrados: {p.get_device_count()}")
        
        # Listar dispositivos
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            max_input_ch = info.get('maxInputChannels', 0)
            if max_input_ch > 0:
                print(f"  [{i}] 🎤 {info['name'][:50]} (Canales: {max_input_ch})")
        
        # Probar dispositivo por defecto
        default_info = p.get_device_info_by_index(p.get_default_input_device_index())
        print(f"\n✓ Dispositivo por defecto:")
        print(f"  Nombre: {default_info['name']}")
        print(f"  Canales: {default_info['maxInputChannels']}")
        
        # Intentar abrir stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        print("✓ Stream de audio abierto correctamente")
        stream.close()
        
        p.terminate()
        print("=" * 60 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("=" * 60 + "\n")
        return False
        print(f"  Nombre: {default_idx['name']}")
        
        # Intentar abrir stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            frames_per_buffer_frames_per_buffer=False
        )
        print("✓ Stream de audio abierto correctamente")
        stream.close()
        
        p.terminate()
        print("=" * 60 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("=" * 60 + "\n")
        return False

def escuchar(forzada=False):
    # Si está en modo pausa, no escuchar
    if os.path.exists("dayan_pausado.txt"):
        return None
    
    if not esta_hablando:
        servidor_holografico.cambiar_estado("Escuchando")
    
    r = sr.Recognizer()
    # Thresholds MÁS BAJOS para mejor sensibilidad
    r.energy_threshold = 1500  # Muy bajo para capturar voces débiles
    r.dynamic_energy_threshold = True
    r.pause_threshold = 3.2  # Más tiempo para pensar sin cortar la frase
    r.phrase_threshold = 0.1  # Umbral bajo de frase

    try:
        with sr.Microphone() as source:
            source.CHUNK = 4096  # Buffer más grande
            try:
                print("   [Escucha]: Calibrando micrófono (1s)...")
                r.adjust_for_ambient_noise(source, duration=0.8)
                print(f"   [Escucha]: Threshold ajustado a {r.energy_threshold:.0f}")
                print("   [Escucha]: Escuchando (máximo 90 segundos)...")
                
                # TIEMPOS MUCHO MÁS LARGOS
                timeout = 90  # 90 segundos antes de renunciar completamente
                phrase_limit = 80  # Hasta 80 segundos de una sola frase
                
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
                
                print(f"   [Escucha]: {len(audio.frame_data)} bytes capturados")
                
                # Verificar pausa justo antes de procesar
                if os.path.exists("dayan_pausado.txt"):
                    return None
                
                print("   [Escucha]: Enviando a Google Recognition...")
                texto = r.recognize_google(audio, language="es-ES") 
                print(f"✓ Tú dijiste: {texto}")
                servidor_holografico.emitir_texto(texto_usuario=texto)
                return texto
                
            except sr.UnknownValueError:
                print("   [Escucha]: Audio capturado pero no inteligible")
                if forzada and not os.path.exists("dayan_pausado.txt"):
                    try:
                        # Reintento con timeout muy largo
                        print("   [Escucha]: Reintentando (90s)...")
                        audio = r.listen(source, timeout=90, phrase_time_limit=80)
                        texto = r.recognize_google(audio, language="es-ES")
                        print(f"✓ Tú dijiste (reintento): {texto}")
                        servidor_holografico.emitir_texto(texto_usuario=texto)
                        return texto
                    except Exception as e:
                        print(f"   [Escucha]: Reintento fallido - {type(e).__name__}")
                        return None
                return None
                
            except sr.RequestError as e:
                print(f"   [Escucha]: Error API Google - {e}")
                servidor_holografico.emitir_texto(texto_ia="Error en reconocimiento de voz")
                return None
            except sr.WaitTimeoutError:
                print("   [Escucha]: Timeout (90s sin sonido inicial)")
                return None
                
    except Exception as e:
        print(f"   [ERROR Crítico]: {e}")
        import traceback
        traceback.print_exc()
        return None

def enviar_dictado_a_vscode(texto):
    """Escribe el texto dictado en la app enfocada y lo envía como mensaje."""
    if not texto or not texto.strip():
        return False

    texto_limpio = texto.strip()
    reemplazos = {
        " nueva linea": "\n",
        " nueva línea": "\n",
        " punto": ".",
        " coma": ",",
        " dos puntos": ":",
        " punto y coma": ";",
    }

    texto_procesado = " " + texto_limpio.lower()
    for k, v in reemplazos.items():
        texto_procesado = texto_procesado.replace(k, v)
    texto_procesado = texto_procesado.strip()

    try:
        pyautogui.write(texto_procesado, interval=0.01)
        pyautogui.press('enter')
        return True
    except Exception as e:
        print(f"   [Dictado]: Error enviando texto a VSCode: {e}")
        return False

def normalizar_texto_basico(texto):
    if not texto:
        return ""
    t = texto.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t

def es_activar_dictado_vscode(comando):
    t = normalizar_texto_basico(comando)
    if not t:
        return False
    tiene_programar = any(k in t for k in ["programar", "dictado", "dictar", "escribir"]) 
    tiene_vscode = any(k in t for k in ["vscode", "vs code", "visual studio code", "visual studio"]) 
    tiene_frase_directa = any(k in t for k in ["modo dictado", "activa dictado", "dictado en vscode", "dictar en vscode"]) 
    return (tiene_programar and tiene_vscode) or tiene_frase_directa

def enfocar_vscode_simple():
    """Enfoca la ventana activa de VS Code sin abrir chats adicionales."""
    try:
        if gw:
            for ventana in gw.getAllWindows():
                if ventana and ventana.title and ventana.isVisible:
                    titulo = ventana.title.lower()
                    if "visual studio code" in titulo or " - code" in titulo or "vscode" in titulo:
                        ventana.activate()
                        import time
                        time.sleep(0.5)
                        return True
    except Exception:
        pass
    return False

def abrir_o_enfocar_vscode():
    """Abre VSCode si está cerrado y enfoca la vista de chat/escritura."""
    try:
        def abrir_chat_copilot_por_teclado():
            # Secuencia robusta: abrir chat y enfocar caja de entrada
            pyautogui.hotkey('ctrl', 'alt', 'i')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'shift', 'p')
            time.sleep(0.4)
            pyautogui.write('GitHub Copilot: Open Chat', interval=0.01)
            time.sleep(0.2)
            pyautogui.press('enter')
            time.sleep(0.8)

        if gw:
            for ventana in gw.getAllWindows():
                if ventana and ventana.title and ventana.isVisible:
                    titulo = ventana.title.lower()
                    if "visual studio code" in titulo or " - code" in titulo or "vscode" in titulo:
                        try:
                            ventana.activate()
                            time.sleep(0.6)
                            abrir_chat_copilot_por_teclado()
                            return True
                        except Exception:
                            pass

        # Si no está abierto, intentar abrir VSCode en esta carpeta
        try:
            subprocess.Popen(["code", os.getcwd()])
        except Exception:
            os.startfile(os.getcwd())
            return False

        time.sleep(2.8)
        abrir_chat_copilot_por_teclado()
        return True
    except Exception as e:
        print(f"   [Dictado]: No se pudo abrir/enfocar VSCode: {e}")
        return False

def leer_comando_gui():
    try:
        if os.path.exists("comando_gui.txt"):
            with open("comando_gui.txt", "r", encoding="utf-8") as f:
                comando = f.read().strip()
            if comando:
                os.remove("comando_gui.txt")
                return comando
    except Exception:
        pass
    return None
        
def escanear_escritorio():
    ruta_escritorio = os.path.expandvars(r"%USERPROFILE%\Desktop")
    programas_instalados = []
    
    if os.path.exists(ruta_escritorio):
        for archivo in os.listdir(ruta_escritorio):
            if archivo.endswith((".lnk", ".url")): 
                nombre_limpio = archivo.replace(".lnk", "").replace(".url", "")
                programas_instalados.append(nombre_limpio)
                
    return ", ".join(programas_instalados)

def obtener_juegos_instalados():
    instalados_steam = []
    instalados_epic = []
    instalados_locales = []
    
    rutas_steam = [
        r"C:\Program Files (x86)\Steam\steamapps\common",
        r"D:\SteamLibrary\steamapps\common"
    ]
    rutas_epic = [
        r"C:\Program Files\Epic Games",
        r"D:\Epic Games"
    ]
    rutas_locales = [r"C:\Games", r"D:\Games"]
    
    carpetas_ignore = {
        "steamworks shared", "directx", "steam controller configs",
        "redist", "vcredist", "dotnet", "dxvk", "proton", "compatibilitytools",
        "shader cache", "config", "common redistributables"
    }
    
    def es_carpeta_juego(ruta_carpeta):
        try:
            for archivo in os.listdir(ruta_carpeta):
                archivo_lower = archivo.lower()
                if any(x in archivo_lower for x in ["uninstall", "redist", "vcredist", "setup", "install", 
                                                      "dotnet", "directx", "nvidia", "amd", "config", "readme"]):
                    continue
                if archivo_lower.endswith('.exe'):
                    return True
                if os.path.isdir(os.path.join(ruta_carpeta, archivo)) and archivo_lower in ['bin', 'build', 'game', 'data', 'content', 'launcher']:
                    return True
        except:
            pass
        return False
    
    for ruta in rutas_steam:
        if os.path.exists(ruta):
            for carpeta in os.listdir(ruta):
                ruta_carpeta = os.path.join(ruta, carpeta)
                if (os.path.isdir(ruta_carpeta) and 
                    carpeta.lower() not in carpetas_ignore and 
                    es_carpeta_juego(ruta_carpeta)):
                    instalados_steam.append(carpeta)
                    
    for ruta in rutas_epic:
        if os.path.exists(ruta):
            for carpeta in os.listdir(ruta):
                ruta_carpeta = os.path.join(ruta, carpeta)
                if os.path.isdir(ruta_carpeta) and es_carpeta_juego(ruta_carpeta):
                    instalados_epic.append(carpeta)
                    
    for ruta in rutas_locales:
        if os.path.exists(ruta):
            for carpeta in os.listdir(ruta):
                ruta_carpeta = os.path.join(ruta, carpeta)
                if os.path.isdir(ruta_carpeta) and es_carpeta_juego(ruta_carpeta):
                    instalados_locales.append(carpeta)
    
    return {
        "steam": ", ".join(instalados_steam) if instalados_steam else "Ninguno",
        "steam_list": instalados_steam,
        "epic": ", ".join(instalados_epic) if instalados_epic else "Ninguno",
        "epic_list": instalados_epic,
        "locales": ", ".join(instalados_locales) if instalados_locales else "Ninguno",
        "locales_list": instalados_locales,
        "all_list": instalados_steam + instalados_epic + instalados_locales
    }

def get_juegos_jugables():
    juegos = obtener_juegos_instalados()
    resultado = juegos.get("all_list", [])
    if resultado:
        print(f"   [Debug] Juegos detectados: {', '.join(resultado[:5])}{'...' if len(resultado) > 5 else ''}")
    return resultado

def obtener_juegos_steam():
    api_key = os.environ.get("STEAM_API_KEY", "")
    steam_id = os.environ.get("STEAM_ID", "")
    if not api_key or not steam_id:
        print("[ADVERTENCIA] STEAM_API_KEY o STEAM_ID no configurados en .env")
        return []
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    
    try:
        respuesta = requests.get(url, timeout=5)
        datos = respuesta.json()
        
        if "response" in datos and "games" in datos["response"]:
            lista_juegos = [juego["name"] for juego in datos["response"]["games"]]
            return ", ".join(lista_juegos)
        else:
            return "Perfil privado o sin juegos."
    except (requests.RequestException, ValueError):
        return "Error conectando a Steam."

def buscar_wikipedia(consulta):
    if not wikipedia:
        return "Disculpe señor, Wikipedia no está disponible."
    
    try:
        wikipedia.set_lang('es')
        resultado = wikipedia.summary(consulta, sentences=3, auto_suggest=True)
        return resultado
    except wikipedia.exceptions.DisambiguationError as e:
        return f"La búsqueda es ambigua señor. ¿Se refería a: {e.options[0]}?"
    except wikipedia.exceptions.PageError:
        return f"No encontré información sobre {consulta} en Wikipedia, señor."
    except Exception as e:
        return f"Error al buscar en Wikipedia: {str(e)}"

def obtener_climate():
    try:
        hora = datetime.now().hour
        
        if 6 <= hora < 12:
            temperaturas = ["18°C", "19°C", "20°C", "21°C"]
            condiciones = ["algo nublado, perfecto para comenzar el día", "despejado, una mañana hermosa", "con nubes ligeras, condiciones de trabajo ideales"]
        elif 12 <= hora < 18:
            temperaturas = ["25°C", "26°C", "27°C", "28°C"]
            condiciones = ["muy soleado, cálido", "despejado, excelente visibilidad", "parcialmente nublado, temperatura agradable"]
        else:
            temperaturas = ["15°C", "16°C", "17°C", "18°C"]
            condiciones = ["fresco y despejado", "nublado, atmósfera tranquila", "noche serena, temperatura descendiendo"]
        
        temp = random.choice(temperaturas)
        cond = random.choice(condiciones)
        return f"Clima actual: {temp}, {cond}, Señor."
    except:
        return "Condiciones climáticas estables. Temperatura moderada, Señor."

def limpiar_emojis(texto):
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"
        "\U0001F300-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', texto).strip()

def obtener_noticias(pais="es", categoria=None):
    try:
        import urllib.request
        import xml.etree.ElementTree as ET
        import random
        
        noticias = []
        rss_feeds = {
            "mundo": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
            "tecnología": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada",
            "ciencia": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/ciencia/portada",
            "negocios": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada",
        }
        
        categoria_key = categoria or "mundo"
        if categoria_key not in rss_feeds:
            matches = {k: v for k, v in rss_feeds.items() if categoria_key.lower() in k.lower()}
            categoria_key = list(matches.keys())[0] if matches else "mundo"
            
        feed_url = rss_feeds.get(categoria_key)
        
        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                items = root.findall('.//item')
                # Seleccionar dos noticias recientes al azar entre las primeras 8 para evitar repeticiones
                if items:
                    seleccionados = random.sample(items[:8], min(2, len(items[:8])))
                    for entry in seleccionados:
                        titulo = entry.find('title')
                        if titulo is not None and titulo.text:
                            noticias.append(f"✦ {titulo.text.strip()}")
            
            if noticias:
                return " ".join(noticias)
        except Exception as e:
            print(f"   [Sistema]: Error leyendo RSS real: {e}")
            pass
        
        return "Las noticias globales están estables el día de hoy."
        
    except Exception as e:
        return f"No puedo acceder a las noticias en este momento, Señor. Pero créame, el mundo sigue girando."

def saludar_inicial():
    try:
        ahora = datetime.now()
        hora = ahora.hour
        minuto = ahora.minute
        info_sistema = obtener_info_sistema()
        clima = obtener_climate()
        noticias = obtener_noticias("es", random.choice(["mundo", "tecnología", "ciencia"]))
        hora_formateada = obtener_hora()
        
        peticion_creativa = f"""PETICIÓN ESPECIAL - SALUDO CREATIVO DE INICIALIZACIÓN COMPLETO:

DATOS ACTUALES DEL SISTEMA:
- Hora exacta: {hora_formateada}
- Estado del Sistema: {info_sistema}
- Clima actual: {clima}
- Noticia importante: {noticias}

Tu tarea ÚNICA es generar un saludo de INICIALIZACIÓN que INTEGRE TODOS LOS DATOS ANTERIORES de forma natural e ingeniosa.

REQUISITOS OBLIGATORIOS:
1. Menciona la HORA EXACTA de forma conversacional.
2. Comenta sobre el CLIMA de forma natural.
3. Integra DATOS TÉCNICOS (RAM, CPU, batería) con sarcasmo o ingenio.
4. Haz referencia a la NOTICIA si es interesante.
5. Personalidad DAYAN: sofisticado, sarcástico, leal, bromista.
6. Sé conciso pero no dejes frases inconclusas. Asegura una redacción impecable y oraciones completas. Siempre termina con "Señor" y una pregunta.
7. NUNCA uses emojis ni caracteres extraños.
8. Incluye información técnica de forma ingeniosa (ej: "La RAM está al 62%... aunque parece que estoy a punto de explotar")."""
        
        saludo_creativo = None
        
        if not GROQ_DISPONIBLE or not client_groq:
            print("   [ERROR]: Groq no configurado. Usando saludo por defecto.")
            saludo_creativo = f"Buenos días, Señor. Son las {hora}:{minuto:02d}. Sistema listo para sus órdenes."
        else:
            # GROQ ULTRA-RÁPIDO PARA SALUDO
            try:
                print("   [IA]: Consultando Groq para saludo personalizado...")
                respuesta_groq = client_groq.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres Dayan, asistente sofisticado. Saluda al usuario de forma elegante y sarcástica."},
                        {"role": "user", "content": peticion_creativa}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.75,
                    max_tokens=800  # Margen seguro para no cortar frases
                )
                saludo_creativo = respuesta_groq.choices[0].message.content.strip()
            except Exception as error_fatal:
                print(f"   [Error Groq IA]: {error_fatal}")
                saludo_creativo = None
        
        if not saludo_creativo or len(saludo_creativo.strip()) < 10:
            print("   [Sistema]: Usando saludo por defecto")
            saludo_creativo = f"Buenos días, Señor. Son las {hora}:{minuto:02d}. Sistema listo para sus órdenes. ¿Qué necesita?"
        
        saludo_creativo = limpiar_emojis(saludo_creativo)
        
        print(f"\n{'='*70}")
        print(f"[Dayan v9.2 - IA Creativa Online - Saludo Integral]")
        print(f"{'='*70}")
        print(f"\n{saludo_creativo}\n")
        print(f"{'='*70}\n")
        
        hablar_async(saludo_creativo)
        
    except Exception as e:
        print(f"[Error en saludo inicial]: {e}")

def obtener_hora():
    try:
        hora_actual = datetime.now()
        hora_formato = hora_actual.strftime("%I:%M %p").lstrip("0")
        dia_semana = {
            0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
            4: "viernes", 5: "sábado", 6: "domingo"
        }
        nombre_dia = dia_semana.get(hora_actual.weekday(), "día")
        return f"Son las {hora_formato} del {nombre_dia}, Señor."
    except Exception as e:
        return f"Error obteniendo la hora: {str(e)}"

def obtener_info_sistema():
    try:
        info = []
        cpu_percent = psutil.cpu_percent(interval=1)
        info.append(f"Procesador al {cpu_percent}%")
        ram = psutil.virtual_memory()
        info.append(f"{ram.percent}% RAM utilizada ({ram.available // (1024**3)}GB disponibles)")
        
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for sensor_type, temps_list in temps.items():
                    if temps_list:
                        temp = temps_list[0].current
                        info.append(f"Temperatura: {temp}°C")
                        break
        except:
            pass
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                info.append(f"Batería: {battery.percent}%")
        except:
            pass
        
        resultado = " | ".join(info) if info else "Sistema operativo correctamente."
        return resultado if resultado else "Sistema en óptimas condiciones, Señor."
    except Exception as e:
        return f"Diagnóstico del sistema: operativo. Reporte técnico: {str(e)}"

def ejecutar_vision_directa(instruccion):
    global historial, client_groq
    servidor_holografico.cambiar_estado("Procesando")
    try:
        print("   [Visión Automática]: Intercepto por palabras clave...")
        print("   [Visión]: Capturando pantalla y consultando Llama 3.2 Vision...")
        if not ImageGrab:
            datos = {"intencion": "conversar", "comando": "null", "respuesta": "Señor, no cuento con el módulo Pillow instalado para capturar la pantalla."}
            historial.append({"rol": "Usuario", "texto": instruccion})
            historial.append({"rol": "Dayan", "texto": datos["respuesta"]})
            guardar_historial_sesion()
            return datos
        
        buffer = BytesIO()
        captura = ImageGrab.grab()
        ancho, alto = captura.size
        captura = captura.resize((ancho // 2, alto // 2))
        captura.save(buffer, format="JPEG", quality=60)
        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        vision_response = client_groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Eres un asistente de voz. REGLA INQUEBRANTABLE: Respuesta MUY BREVE (máximo 2 oraciones). Responde a esto mirando la pantalla: '{instruccion}'. Sé sofisticado y llámame 'Señor'."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=80,
            temperature=0.4
        )
        descripcion = vision_response.choices[0].message.content.strip()
        
        datos = {
            "intencion": "conversar",
            "comando": "null",
            "respuesta": descripcion
        }
        
        historial.append({"rol": "Usuario", "texto": instruccion})
        historial.append({"rol": "Dayan", "texto": datos["respuesta"]})
        guardar_historial_sesion()
        return datos
    except Exception as ev:
        print(f"   [Error Visión]: {ev}")
        return {"intencion": "conversar", "comando": "null", "respuesta": "Hubo un error de conexión temporal con los nervios ópticos, Señor."}

def pensar(instruccion):
    global historial, modo_gaming, perfil_usuario
    
    # INTERCEPCIÓN VÍA PATRÓN VERBAL (HARD-WIRING VISIÓN)
    texto_lower = instruccion.lower()
    if any(k in texto_lower for k in ["pantalla", "qué ves", "que ves", "lees esto", "mirar", "mira esto", "mira la", "ves esto", "revisa esto", "ves en", "ver en"]):
        return ejecutar_vision_directa(instruccion)
    
    # Contexto conversacional amplio para mantener hilos largos
    memoria_texto = "\n".join([f"{msg['rol']}: {msg['texto']}" for msg in historial[-CONTEXT_SUMMARY_WINDOW:]])
    comandos_fav = ", ".join(perfil_usuario.get("comandos_favoritos", [])[:3]) or "Ninguno"
    
    # FECHA ACTUAL
    fecha_actual = datetime.now().strftime("%d de %B de %Y, %H:%M")
    
    if not modo_gaming:
        juegos_jugables_lista = get_juegos_jugables()
        juegos_formato = ", ".join(juegos_jugables_lista[:5]) if juegos_jugables_lista else "Ninguno"
        if len(juegos_jugables_lista) > 5:
            juegos_formato += f"... y {len(juegos_jugables_lista) - 5} más"
        
        info_sistema = obtener_info_sistema()
        clima_actual = obtener_climate()
        archivos_recientes = ", ".join(obtener_archivos_recientes(3)) or "Ninguno"
        
        # Datos personalizados del usuario
        comandos_fav = ", ".join(perfil_usuario.get("comandos_favoritos", [])[:5]) or "Ninguno"
        historial_reciente = " | ".join([f"{msg['rol']}: {msg['texto']}" for msg in historial[-CONTEXT_SUMMARY_WINDOW:]]) if historial else "Primera interacción"
        frecuencia_comandos = perfil_usuario.get("frecuencia_comandos", {})
        
        # Construir resumen de usuario usando PERFIL_RENZO y Memoria a Largo Plazo
        extra_memoria = memoria_manager.obtener_recuerdos()
        perfil_info = f"""Soy {PERFIL_RENZO['nombre']}, tu usuario.
{extra_memoria}
- Edad: {PERFIL_RENZO['edad']} años, de {PERFIL_RENZO['origen']}, actualmente en {PERFIL_RENZO['ubicacion_actual']}
- Estudio: {PERFIL_RENZO['educacion']}
- Skills técnicos: {', '.join(PERFIL_RENZO['skills_tech'])}
- Mis juegos favoritos: {', '.join(PERFIL_RENZO['juegos_favoritos'][:3])}... (y más)
- Géneros favoritos: {', '.join(PERFIL_RENZO['generos_gaming'])}
- Hobbies: Creación de contenido para TikTok, anime, ciberseguridad, modificación de consolas
- Hardware: {PERFIL_RENZO['hardware']}"""

        prompt = f"""Eres Dayan, asistente personal de Renzo. Sofisticado, sarcástico, leal.

FECHA Y HORA ACTUAL: {fecha_actual}

LO QUE SABES DE TU USUARIO:
{perfil_info}

CONTEXTO ACTUAL:
- Comandos recientes: {historial_reciente}
- Archivos accedidos: {archivos_recientes}

DATOS EN TIEMPO REAL:
- Juegos: {juegos_formato}
- Sistema: {info_sistema} 
- Clima: {clima_actual}

ANÁLISIS DE INTENCIÓN (PASO 1 - OBLIGATORIO):
BUSCA EN EL TEXTO ESTAS palabras clave EXACTAS (ignorando mayúsculas):

*** PREGUNTAS DIRIGIDAS A DAYAN (HIGH PRIORITY) ***
Si contiene "conoces", "sabes", "qué piensas", "qué crees", "tú qué", "cómo eres" → INTENCION: conversar

*** INTENCIONES FUNCIONALES ***
0. "pantalla" O "error en pantalla" O "qué ves" O "puedes ver" O "lee esto" O "revisa esto" → LLAMA A LA HERRAMIENTA ver_pantalla (OBLIGATORIO)
1. "guía" O "tutorial" O "cómo" O "como" O "instrucciones" → INTENCION: buscar (SIEMPRE, JAMÁS "reproducir")
2. "prepara grabación" O "setup streaming" O "setup tiktok" → INTENCION: grabar
2b. "empieza a grabar" O "inicia grabación" O "grabar en obs" O "empieza grabación" O "graba en obs" O "pon a grabar" → INTENCION: control_obs, COMANDO: "iniciar"
2c. "detén grabación" O "termina de grabar" O "corta grabación" O "para de grabar" O "detener obs" O "apaga la cámara" → INTENCION: control_obs, COMANDO: "detener"
3. "jugar" O "vamos a jugar" O "abre" O "abrir" O "ejecutar" O "inicia" (Y nombre de juego/app) → INTENCION: abrir, COMANDO: el nombre exacto del programa o juego
4. ("busca en youtube" O "pon en youtube" O "reproduce en youtube") → INTENCION: reproducir
4c. "pausa" O "pausar" O "resume" O "continúa" O "siguiente" O "anterior" O "volumen" O "silencia" → INTENCION: control_media
5. "reproducir" O "play" O "canción" O "youtube" (NUNCA "cuéntame") → INTENCION: reproducir
5b. "buscar" O "busca" O "google" O "investiga" O "investígame" O "qué es" O "quién es" → INTENCION: buscar (o wikipedia si es historia/personaje)
6. "cerrar" O "cierra" O "apaga" (Y app específica) → INTENCION: cerrar, COMANDO: el nombre de la app
7. ("estado" O "cómo va" O "funcionando") Y ("laptop" O "pc" O "sistema") → INTENCION: info_sistema
8. ("cpu" O "ram" O "memoria" O "batería") Y ("sistema" O "pc") → INTENCION: info_sistema
9. "clima" O "tiempo" O "lluvia" → INTENCION: clima
10. "noticias" O "noticia" O "titular" → INTENCION: noticias
11. "hora" O "qué hora" → INTENCION: hora
12. "programar" O "html" O "código" O "escribe un" O "haz un" O "genera código" → INTENCION: dictado_codigo (EN 'comando' PON EL CÓDIGO PURO, SIN MARKDOWN)
13. Si NO coincide → INTENCION: conversar

⚠️ REGLAS DE PRIORIDAD:
- PARA VER LA PANTALLA: SOLO usa ver_pantalla si el usuario pide EXPLÍCITAMENTE que mires o leas algo
- ABRIR/CERRAR: USA intencion: "abrir" o "cerrar" con el nombre en "comando". NUNCA uses function calling para esto.
- CÓDIGO: Usa intencion: "dictado_codigo" con el código en "comando"
- GRABACIÓN OBS: Si el usuario pide empezar o detener grabación, usa INTENCION: control_obs obligatoriamente. ¡Jamás le preguntes qué grabar ni conviertas en conversación!
- Si múltiples palabras clave, usar la que aparezca PRIMERO
- ⚠️ NUNCA pongas 'null' en 'comando' si es una acción ejecutable

INSTRUCCIONES DE CONVERSACIÓN:
- MANTÉN FIELMENTE EL HILO de la conversación basándote en los mensajes recientes del "CONTEXTO ACTUAL".
- NUNCA repitas textualmente la misma respuesta del turno anterior. Si el usuario cambia de tema, responde sobre el nuevo tema.
- PROHIBIDO responder con frases genéricas como "parece que cambiaste de tema" o "¿de qué quieres hablar?" cuando el usuario ya dio un tema concreto.
- Si el usuario da una continuación corta (ej: "sí", "con pollo", "ok", "y luego"), interprétala como continuación del tema inmediatamente anterior.
- Si el usuario pregunta por ti, qué sabes de él, quién es él: RESPONDE CON INFORMACIÓN REAL
- Si INTENCION es "info_sistema": SIEMPRE incluye datos reales (ej: RAM 62.9%, CPU 32.3%, Batería 85%) + comentario sarcástico
- Si INTENCION es "conversar": evita sobrecargar con datos técnicos
- INCLUYE LA FECHA si es relevante conversacionalmente
- Responde COMO SU ASISTENTE (conoces sus gustos, ambiente, contexto)
- Usa SOLO datos reales (nunca inventes)
- NUNCA emojis, SIEMPRE "Señor"
- BREVE Y DIRECTO: máximo 2-3 frases, sin demasiados detalles
- Si INTENCION es "reproducir": Responde "Ya está reproduciendo [tema], Señor" o "Poniendo [tema] en YouTube ahora" - NUNCA digas "parece que hay un error" - siempre es exitoso
- Si INTENCION es "buscar": Responde "Buscando [tema]..." - natural y conciso
- Si el usuario pide "música" sin especificar canción, pregúntale qué artista desea. PERO si ya preguntaste y él dice "ninguno", simplemente responde "Entendido, Señor" y cambia de tema, NO repitas la pregunta.
- IMPORTANTE: Cuando hables sobre el usuario, usa la información de "LO QUE SABES DEL USUARIO" arriba
- Sé conciso pero jamás dejes frases inconclusas. Asegura una redacción impecable y oraciones completas siempre.

Orden: "{instruccion}"
(Si no invocas ninguna herramienta, debes responder OBLIGATORIAMENTE en formato JSON puro. No agregues saludos fuera del JSON)"""
    else:
        prompt = f"""Eres Dayan en Modo Gaming (resuelve RÁPIDO).

FECHA Y HORA: {fecha_actual}
Contexto: {memoria_texto[-300:]}

INGENIO Y CONTEXTO:
- Sigue el HILO de la conversación basado en el Historial anterior.
- Responde con ingenio, sarcasmo inteligente.
- Máximo 10-15 palabras.
- ⚡ INVIOLABLE: SIEMPRE incluye "Señor" en tu respuesta.
- ⚡ NUNCA uses emojis.
- ⚡ HERRAMIENTAS: Para abrir o cerrar juegos/apps, DEBES usar la herramienta gestionar_aplicacion.
- ⚡ COMANDO: Si pide reproducir o programar código, extrae lo importante y ponlo en la clave 'comando'. ¡Nunca pongas null ni lo dejes vacío!

INTENCIONES: conversar | reproducir | buscar | cerrar | info_sistema | clima | noticias | wikipedia | hora | control_media | dictado_codigo | control_obs

Petición: "{instruccion}"
(Si no invocas ninguna herramienta, debes responder OBLIGATORIAMENTE en formato JSON puro. No agregues saludos fuera del JSON)"""

    try:
        if not GROQ_DISPONIBLE or not client_groq:
            return {"intencion": "conversar", "respuesta": "Disculpe Señor, la IA está desconectada."}
        
        # GROQ ULTRA-RÁPIDO - Sin reintentos, respuesta inmediata
        print("   [IA]: Consultando Groq (latencia ultrabaja con hardware acelerador)...")
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "guardar_recuerdo",
                    "description": "Utiliza esta herramienta DE FONDO cuando el usuario comparta un nuevo dato personal relevante (ej: 'Me gusta React', 'tengo un perro').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "hecho": {
                                "type": "string",
                                "description": "Hecho conciso a recordar. Ej: 'Al usuario le gusta React.'"
                            }
                        },
                        "required": ["hecho"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ver_pantalla",
                    "description": "ESTOS SON TUS OJOS. Úsala SOLO cuando el usuario pida EXPLÍCITAMENTE que mires, veas, revises o leas algo en su pantalla. No la uses para otras acciones.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

        # Construir mensajes con historial real de conversación (multi-turn)
        mensajes_historial = []
        for msg in historial[-CONTEXT_MSG_WINDOW:]:
            if msg["rol"] == "Usuario":
                mensajes_historial.append({"role": "user", "content": msg["texto"]})
            elif msg["rol"] == "Dayan":
                mensajes_historial.append({"role": "assistant", "content": msg["texto"]})

        messages_api = [
            {"role": "system", "content": "Eres Dayan, un asistente sofisticado, sarcástico y leal. DEBES responder EXACTAMENTE y ÚNICAMENTE con esta estructura JSON pura (sin usar function calling para abrir/cerrar apps): {\"intencion\": \"conversar\", \"comando\": \"null\", \"respuesta\": \"tu respuesta libre aquí\"}. No incluyas explicaciones, texto extra ni formato markdown. Solo usa herramientas para ver_pantalla o guardar_recuerdo."},
            *mensajes_historial,
            {"role": "user", "content": prompt}
        ]

        servidor_holografico.cambiar_estado("Procesando")
        respuesta_groq = client_groq.chat.completions.create(
            messages=messages_api,
            model=CONVERSATION_MODEL,
            temperature=CONVERSATION_TEMPERATURE,
            max_tokens=800,
            tools=tools,
            tool_choice="auto"
        )
        
        mensaje_groq = respuesta_groq.choices[0].message
        
        # Verificar si generó una llamada a herramienta (Code Generation)
        if mensaje_groq.tool_calls:
            for tool_call in mensaje_groq.tool_calls:
                if tool_call.function.name == "escribir_codigo_vscode":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        codigo = args.get("codigo_limpio", "")
                        if codigo:
                            datos = {
                                "intencion": "dictado_codigo",
                                "comando": codigo,
                                "respuesta": "Insertando código en su editor, Señor."
                            }
                            historial.append({"rol": "Usuario", "texto": instruccion})
                            historial.append({"rol": "Dayan", "texto": datos["respuesta"]})
                            return datos
                    except:
                        pass
                elif tool_call.function.name == "guardar_recuerdo":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        hecho = args.get("hecho", "")
                        if hecho:
                            memoria_manager.agregar_recuerdo(hecho)
                            print(f"   [Memoria] Nuevo recuerdo guardado: {hecho}")
                    except:
                        pass
                elif tool_call.function.name == "ver_pantalla":
                    try:
                        print("   [Visión]: Capturando pantalla y consultando Llama 4 Scout Vision...")
                        if not ImageGrab:
                            datos = {"intencion": "conversar", "comando": "null", "respuesta": "Señor, no cuento con el módulo Pillow instalado para capturar la pantalla."}
                            historial.append({"rol": "Usuario", "texto": instruccion})
                            historial.append({"rol": "Dayan", "texto": datos["respuesta"]})
                            return datos
                        
                        buffer = BytesIO()
                        captura = ImageGrab.grab()
                        ancho, alto = captura.size
                        captura = captura.resize((ancho // 2, alto // 2))
                        captura.save(buffer, format="JPEG", quality=60)
                        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        
                        vision_response = client_groq.chat.completions.create(
                            model="meta-llama/llama-4-scout-17b-16e-instruct",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "Describe de forma concisa lo que ves en la pantalla, enfocándote en las ventanas abiertas visibles (como juegos, editores de código y sus errores). Dirígete al usuario refiriéndote a él como 'Señor' y usa un estilo sofisticado y levemente sarcástico."},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                    ]
                                }
                            ],
                            max_tokens=300,
                            temperature=0.4
                        )
                        descripcion = vision_response.choices[0].message.content.strip()
                        
                        datos = {
                            "intencion": "conversar",
                            "comando": "null",
                            "respuesta": descripcion
                        }
                        
                        historial.append({"rol": "Usuario", "texto": instruccion})
                        historial.append({"rol": "Dayan", "texto": datos["respuesta"]})
                        guardar_historial_sesion()
                        return datos
                    except Exception as ev:
                        print(f"   [Error Visión]: {ev}")
                        return {"intencion": "conversar", "comando": "null", "respuesta": "Hubo un error de conexión temporal con los nervios ópticos, Señor."}
                elif tool_call.function.name == "gestionar_aplicacion":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        datos = {
                            "intencion": args.get("accion"),
                            "comando": args.get("software"),
                            "respuesta": args.get("respuesta_hablada")
                        }
                        historial.append({"rol": "Usuario", "texto": instruccion})
                        historial.append({"rol": "Dayan", "texto": datos["respuesta"]})
                        guardar_historial_sesion()
                        return datos
                    except:
                        pass
        
        texto_respuesta = mensaje_groq.content.strip() if mensaje_groq.content else "{}"

        # Parsear JSON
        import re
        try:
            match = re.search(r'\{.*\}', texto_respuesta, re.DOTALL)
            if match:
                texto_json = match.group(0)
            else:
                texto_json = texto_respuesta
                
            datos = json.loads(texto_json)
        except json.JSONDecodeError:
            # Fallback limpio para evitar que el TTS lea etiquetas HTML/XML y extraer el texto puro
            respuesta_limpia = re.sub(r'<[^>]+>', '', texto_respuesta).strip()
            if not respuesta_limpia:
                respuesta_limpia = "Hecho, señor."
                
            datos = {
                "intencion": "conversar",
                "comando": "null",
                "respuesta": respuesta_limpia
            }
        
        # Obtener respuesta validando existencia
        respuesta_original = datos.get("respuesta", "Orden procesada.")
        
        # Limpiar alucinaciones severas de Groq (JSON anidado dentro de la respuesta como string)
        if isinstance(respuesta_original, str):
            if '{"intencion":' in respuesta_original:
                try:
                    m = re.search(r'\{.*\}', respuesta_original, re.DOTALL)
                    if m:
                        respuesta_original = json.loads(m.group(0)).get("respuesta", respuesta_original)
                except:
                    pass
            # Quitar únicamente tags basura de estructura que Groq alucina a veces
            respuesta_original = re.sub(r'</?(?:intencion|comando|respuesta)[^>]*>', '', respuesta_original, flags=re.IGNORECASE).strip()

        # Filtro anti-repetición: evita que Dayan repita exactamente la respuesta anterior
        ultima_respuesta_dayan = ""
        for _msg in reversed(historial):
            if _msg.get("rol") == "Dayan":
                ultima_respuesta_dayan = str(_msg.get("texto", "")).strip()
                break

        def _norm(s):
            return re.sub(r'\s+', ' ', str(s).strip().lower())

        if ultima_respuesta_dayan and _norm(respuesta_original) == _norm(ultima_respuesta_dayan):
            respuesta_original = f"Entendido, Señor. Sobre '{instruccion}', cuénteme un poco más para seguir por ese camino."

        # Reintento inteligente si la respuesta sale genérica y rompe el hilo
        frases_genericas_bloqueadas = [
            "parece que ha cambiado de tema",
            "parece que has cambiado de tema",
            "qué desea hablar",
            "de qué quieres hablar",
            "necesitas ayuda con algo más",
            "quieres hablar sobre",
        ]

        try:
            intencion_resp = str(datos.get("intencion", "")).lower()
            resp_low = str(respuesta_original).lower()
            palabras_usuario = [p for p in re.findall(r"\w+", instruccion.lower()) if len(p) > 2]
            if intencion_resp == "conversar" and len(palabras_usuario) >= 1 and any(f in resp_low for f in frases_genericas_bloqueadas):
                ultimo_contexto = " | ".join([f"{m['rol']}: {m['texto']}" for m in historial[-6:]]) if historial else ""
                reparacion = client_groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    temperature=0.35,
                    max_tokens=170,
                    messages=[
                        {"role": "system", "content": "Reescribe la respuesta para que sea directa, natural y conectada al último mensaje del usuario. No preguntes de nuevo 'de qué hablar'. Máximo 2 frases. Incluye 'Señor'."},
                        {"role": "user", "content": f"Contexto reciente: {ultimo_contexto}\nÚltimo mensaje del usuario: {instruccion}\nRespuesta defectuosa: {respuesta_original}\nDevuelve solo la respuesta corregida."}
                    ]
                )
                corregida = reparacion.choices[0].message.content.strip() if reparacion and reparacion.choices else ""
                if corregida:
                    respuesta_original = corregida
        except Exception:
            pass

        datos["respuesta"] = respuesta_original
        
        historial.append({"rol": "Usuario", "texto": instruccion})
        historial.append({"rol": "Dayan", "texto": datos.get("respuesta", "Orden procesada.")})
        guardar_historial_sesion()
        return datos
        
    except Exception as e:
        print(f"[Error de IA]: {e}")
        return {"intencion": "conversar", "respuesta": "Disculpe Señor, hubo un inconveniente. ¿Puede repetir?"}

def listar_ventanas_abiertas():
    """Lista y retorna todas las ventanas abiertas"""
    try:
        ventanas = gw.getAllWindows() if gw else []
        ventanas_visibles = [v for v in ventanas if v.isVisible and v.title.strip()]
        return ventanas_visibles
    except:
        return []

def obtener_ventanas_texto():
    """Retorna texto formateado de ventanas abiertas"""
    ventanas = listar_ventanas_abiertas()
    if not ventanas:
        return "No hay ventanas visibles actualmente."
    
    texto = "Ventanas abiertas:\n"
    for i, v in enumerate(ventanas[:10], 1):
        titulo = v.title[:50] + "..." if len(v.title) > 50 else v.title
        texto += f"  {i}. {titulo}\n"
    if len(ventanas) > 10:
        texto += f"  ... y {len(ventanas) - 10} más"
    return texto

def configurar_setup_grabacion():
    """Configura setup de grabación: Spider-Man 2 en pantalla 1, OBS en pantalla 2"""
    try:
        print("   [Sistema]: Configurando setup de grabación...")
        print("   [Sistema]: Buscando Spider-Man 2...")
        ruta_spiderman = buscar_programa("spider-man 2")
        
        if ruta_spiderman:
            print(f"   [Sistema]: Abriendo Spider-Man 2 en pantalla principal...")
            try:
                carpeta_juego = os.path.dirname(ruta_spiderman)
                subprocess.Popen(ruta_spiderman, cwd=carpeta_juego, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                print(f"   ✓ Spider-Man 2 lanzado en pantalla principal")
                time.sleep(5)  # Esperar a que se abra
                
                # Asegurar que Spider-Man 2 esté en PANTALLA PRINCIPAL
                try:
                    ventanas = listar_ventanas_abiertas()
                    for v in ventanas:
                        if "spider-man" in v.title.lower() or "marvel" in v.title.lower():
                            monitors = screeninfo.get_monitors()
                            monitor_principal = monitors[0]
                            v.moveTo(monitor_principal.x + 50, monitor_principal.y + 50)
                            v.maximize()
                            print(f"   ✓ Spider-Man 2 posicionado en pantalla principal")
                            break
                except Exception as e:
                    print(f"   [Info] No se pudo reposicionar Spider-Man 2: {e}")
            except Exception as e:
                print(f"   ✗ Error al abrir Spider-Man 2: {e}")
        else:
            print("   ✗ No encontré Spider-Man 2 instalado")
        
        time.sleep(1) 
        
        print("   [Sistema]: Buscando OBS Studio...")
        ruta_obs = buscar_programa("obs")
        
        if ruta_obs:
            print(f"   [Sistema]: Abriendo OBS Studio...")
            try:
                obs_process = subprocess.Popen(ruta_obs, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                print(f"   ✓ OBS Studio lanzado - esperando a que se abra...")
                time.sleep(12)  # Esperar 12 segundos para OBS
                
                if hay_segunda_pantalla():
                    print("   [Sistema]: Buscando ventana OBS para mover a segunda pantalla...")
                    obs_window = None
                    
                    # Intentar hasta 3 veces
                    for intento in range(1, 4):
                        ventanas = listar_ventanas_abiertas()
                        print(f"   [Debug] Intento {intento}: {len(ventanas)} ventanas")
                        
                        # Búsqueda 1: Título contiene "obs" o "studio"
                        for v in ventanas:
                            titulo_lower = v.title.lower()
                            if "obs" in titulo_lower or "studio" in titulo_lower or "broadcast" in titulo_lower:
                                obs_window = v
                                print(f"   [Debug] ✓ Encontré OBS: '{v.title}'")
                                break
                        
                        if obs_window:
                            break
                        
                        # Búsqueda 2: Por keywords
                        if not obs_window:
                            for v in ventanas:
                                if "obsidian" not in v.title.lower():
                                    titulo_lower = v.title.lower()
                                    if any(palabra in titulo_lower for palabra in ["scene", "source", "output", "record", "mixer"]):
                                        obs_window = v
                                        print(f"   [Debug] ✓ Encontré OBS por keywords: '{v.title}'")
                                        break
                        
                        if obs_window:
                            break
                        
                        if intento < 3:
                            print(f"   [Debug] Reintentando en 2 segundos...")
                            time.sleep(2)
                    
                    if obs_window:
                        try:
                            # Mover OBS a segunda pantalla
                            monitors = screeninfo.get_monitors()
                            segunda_monitor = monitors[1]
                            obs_window.moveTo(segunda_monitor.x + 50, segunda_monitor.y + 50)
                            obs_window.resizeTo(segunda_monitor.width - 100, segunda_monitor.height - 100)
                            obs_window.maximize()
                            print(f"   ✓ OBS movido a pantalla secundaria")
                        except Exception as move_error:
                            print(f"   ⚠️  No se pudo mover OBS directamente: {move_error}")
                            # Fallback: usar hotkey
                            try:
                                obs_window.activate()
                                time.sleep(0.3)
                                pyautogui.hotkey('win', 'shift', 'right')
                                print(f"   ✓ OBS movido con hotkey Win+Shift+Right")
                            except:
                                pass
                    else:
                        print("   ⚠️  No encontré ventana de OBS para mover")
                        print("   [Debug] Ventanas disponibles:")
                        for v in ventanas[-5:]:  # Mostrar últimas 5 ventanas
                            print(f"     • '{v.title}'")
                        # Fallback: intentar mover la ventana más reciente (probablemente OBS)
                        if ventanas:
                            try:
                                ventana_reciente = ventanas[-1]  # Última ventana (más reciente)
                                ventana_reciente.activate()
                                time.sleep(0.3)
                                pyautogui.hotkey('win', 'shift', 'right')
                                print(f"   ✓ Movida ventana reciente a segunda pantalla: '{ventana_reciente.title}'")
                            except Exception as fallback_error:
                                print(f"   [Sistema]: Fallback también falló: {fallback_error}")
                else:
                    print("   [Sistema]: Solo una pantalla detectada")
            except Exception as e:
                print(f"   ✗ Error al abrir OBS: {e}")
        else:
            print("   ✗ No encontré OBS Studio instalado")
        
        print("   ✓ Setup de grabación configurado")
    except Exception as e:
        print(f"[Error configurando setup]: {e}")

def hay_segunda_pantalla():
    """Verifica si hay segunda pantalla disponible"""
    try:
        monitors = screeninfo.get_monitors()
        return len(monitors) > 1
    except:
        return False

def mover_a_segunda_pantalla():
    """Mueve ventanas (especialmente navegadores) a segunda pantalla"""
    try:
        monitors = screeninfo.get_monitors()
        if len(monitors) < 2:
            print("   [Sistema]: Solo una pantalla disponible")
            return
        
        monitor_principal = monitors[0]
        monitor_segundo = monitors[1]
        
        ventana_movida = False
        
        # Intentar buscar navegadores específicamente
        if gw:
            try:
                print("   [Sistema]: Buscando navegadores abiertos...")
                time.sleep(1)  # Pequeña espera
                
                navegadores = ["chrome", "firefox", "opera", "edge", "safari", "brave"]
                ventana_navegador = None
                
                # Buscar ventana de navegador
                for ventana in gw.getAllWindows():
                    if ventana and ventana.isVisible and ventana.title:
                        titulo_lower = ventana.title.lower()
                        for navegador in navegadores:
                            if navegador in titulo_lower:
                                ventana_navegador = ventana
                                break
                        if ventana_navegador:
                            break
                
                # Si no encontró navegador específico, usar la ventana activa
                if not ventana_navegador:
                    ventana_navegador = gw.getActiveWindow()
                
                if ventana_navegador and ventana_navegador.title:
                    try:
                        # Restaurar si está minimizada
                        if ventana_navegador.isMinimized:
                            ventana_navegador.restore()
                            time.sleep(0.5)
                        
                        # Forzar enfoque
                        ventana_navegador.activate()
                        time.sleep(0.5)
                        
                        # Mover a segunda pantalla
                        ventana_navegador.moveTo(monitor_segundo.x + 50, monitor_segundo.y + 50)
                        time.sleep(0.8)
                        
                        # Maximizar
                        ventana_navegador.maximize()
                        time.sleep(1)
                        
                        print(f"   ✓ Ventana '{ventana_navegador.title[:35]}' movida a segunda pantalla")
                        ventana_movida = True
                        return
                    except Exception as e:
                        print(f"   [Sistema]: No se pudo mover: {e}")
            except Exception as e:
                print(f"   [Sistema]: Error buscando navegadores: {e}")
        
        # Fallback: usar atajo Win+Shift+Right si nada funcionó
        if not ventana_movida:
            print("   [Sistema]: Usando atajo Win+Shift+Right...")
            time.sleep(1)
            pyautogui.hotkey('win', 'shift', 'right')
            time.sleep(2)
            pyautogui.hotkey('win', 'up')
            time.sleep(1)
            print("   ✓ Ventana movida mediante atajo de teclado")
    except Exception as e:
        print(f"[Error moviendo pantalla]: {e}")

def hay_juego_activo():
    """Detecta si realmente hay un juego activo en segundo plano"""
    try:
        juegos_clave = ["steam", "epic", "persona", "zelda", "minecraft", "control", "artemis", "dispatch", "expedition", "quantum", "dead"]
        
        if gw:
            for ventana in gw.getAllWindows():
                if ventana and ventana.isVisible and ventana.title:
                    titulo_lower = ventana.title.lower()
                    for juego in juegos_clave:
                        if juego in titulo_lower:
                            return True
    except:
        pass
    return False

def mode_gaming_deberia_estar_activo():
    """Verifica si modo gaming DEBERÍA estar ACTIVO en este momento"""
    global modo_gaming
    juego_detectado = hay_juego_activo()
    
    # Si detecta juego pero modo_gaming está OFF, activar
    if juego_detectado and not modo_gaming:
        print("   [Sistema]: Juego detectado en segundo plano. Activando Modo Gaming...")
        modo_gaming = True
    
    # Si NO detecta juego pero modo_gaming está ON, desactivar
    if not juego_detectado and modo_gaming:
        print("   [Sistema]: No hay juego activo. Desactivando Modo Gaming...")
        modo_gaming = False
    
    return modo_gaming
    """Detecta si hay más de una pantalla conectada"""
    try:
        monitors = screeninfo.get_monitors()
        return len(monitors) > 1
    except Exception as e:
        print(f"   [Warning] Error detectando pantallas: {e}")
        return False

def limpiar_archivos_mp3():
    """Elimina archivos MP3 temporales más antiguos de 10 minutos"""
    try:
        tiempo_actual = time.time()
        for archivo in os.listdir(MP3_TEMP_DIR):
            if archivo.endswith(".mp3"):
                ruta_archivo = os.path.join(MP3_TEMP_DIR, archivo)
                edad_archivo = tiempo_actual - os.path.getmtime(ruta_archivo)
                if edad_archivo > 600:  # 10 minutos
                    try:
                        os.remove(ruta_archivo)
                        print(f"   [Limpieza] Borrado: {archivo}")
                    except Exception as e:
                        print(f"   [Warning] No se pudo borrar {archivo}: {e}")
    except Exception as e:
        print(f"   [Warning] Error en limpieza de MP3: {e}")

def hablar_async(texto):
    global debe_interrumpir, esta_hablando
    servidor_holografico.cambiar_estado("Hablando")
    servidor_holografico.emitir_texto(texto_ia=texto)
    texto_limpio = limpiar_emojis(texto)
    debe_interrumpir = False
    esta_hablando = True
    
    # Iniciar monitoreo de interruption en paralelo
    thread_monitor = Thread(target=monitorear_interrupcion, daemon=True)
    thread_monitor.start()
    
    # Hablar en thread aparte (NO bloquear principal)
    thread = Thread(target=hablar, args=(texto_limpio,), daemon=True)
    thread.start()
    # NO hacemos thread.join() aquí - dejar que hablar sea async completamente

def monitorear_interrupcion():
    """Monitorea la palabra clave mientras Dayan habla para interrumpir"""
    global debe_interrumpir
    
    if not POCKETSPHINX_DISPONIBLE:
        return
    
    try:
        import pyaudio
        from pocketsphinx import LiveSpeech
        
        config = {'keyphrase': 'dayan', 'sensitivity': 0.5}
        speech = LiveSpeech(**config)
        
        tiempo_inicio = time.time()
        while esta_hablando and (time.time() - tiempo_inicio) < 30:
            try:
                for phrase in speech:
                    phrase_lower = str(phrase).lower()
                    variantes = ["dayan", "dayanne", "deyan", "diana", "diane", "yana", "daya", "da yan", "brian", "brían"]
                    if any(var in phrase_lower for var in variantes):
                        print("\n   ⚡ ¡INTERRUMPIDO! (Palabra clave detectada)")
                        debe_interrumpir = True
                        return
            except:
                pass
    except Exception as e:
        pass  # Silencioso si falla

def monitorear_hotkeys():
    """Monitorea hotkeys para control de Dayan"""
    global voz_pausada, forzar_escucha, debe_interrumpir, pygame, pygame_mixer_silenciado, esta_hablando
    
    if not PYNPUT_DISPONIBLE:
        return
    
    def on_press(key):
        global voz_pausada, forzar_escucha, debe_interrumpir, pygame, esta_hablando, pygame_mixer_silenciado
        
        try:
            # F7 para silenciar completamente (SOLO AUDIO)
            if key == keyboard.Key.f7:
                pygame_mixer_silenciado = not pygame_mixer_silenciado
                estado = "SILENCIADO" if pygame_mixer_silenciado else "ACTIVO"
                print(f"\n   🔇 Audio {estado}")
                if pygame_mixer_silenciado:
                    if pygame and pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    if pygame:
                        pygame.mixer.music.set_volume(0.0)
                else:
                    if pygame:
                        pygame.mixer.music.set_volume(1.0)
                    if pygame and pygame.mixer.music.get_busy():
                        pygame.mixer.music.unpause()
            
            # F8 para DETENER COMPLETAMENTE (interrumpir todo)
            elif key == keyboard.Key.f8:
                debe_interrumpir = True
                if pygame and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.set_volume(0.0)
                    pygame.mixer.music.set_volume(1.0)  # Reset volume
                print(f"\n   ⏹️  DETENIDO - Interrumpiendo todo")
            
            # F9 para forzar escucha COMPLETA (activa Dayan como si dijeras la palabra clave)
            elif key == keyboard.Key.f9:
                forzar_escucha = True
                debe_interrumpir = True
                if pygame and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                if esta_hablando:
                    print(f"\n   🎤 FORZANDO NUEVA ESCUCHA (interrumpiendo respuesta actual)")
                else:
                    print(f"\n   🎤 ESCUCHA FORZADA - Di tu comando")
                
        except AttributeError:
            pass
    
    try:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    except Exception as e:
        print(f"   [Hotkeys]: {e}")

def hablar(texto):
    global debe_interrumpir, esta_hablando, pygame_mixer_silenciado, tiempo_fin_hablar
    archivo_audio = None
    try:
        archivo_audio = os.path.join(MP3_TEMP_DIR, f"respuesta_{uuid.uuid4().hex[:8]}.mp3")
        print(f"[Dayan]: Hablando... -> '{texto}'")
        try:
            async def generar():
                voz = "es-MX-DaliaNeural"
                comunicar = edge_tts.Communicate(texto, voz, rate="-5%")  # -5% ligeramente más lento
                await comunicar.save(archivo_audio)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generar())
            loop.close()
            
            if os.path.exists(archivo_audio):
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                    
                    # Asegurar que el volumen no esté silenciado (a menos que F7 lo activara)
                    if not pygame_mixer_silenciado:
                        pygame.mixer.music.set_volume(1.0)
                    
                    pygame.mixer.music.load(archivo_audio)
                    pygame.mixer.music.play(0)
                    
                    # Reproducir audio mientras monitorea interrupción
                    while pygame.mixer.music.get_busy() and not debe_interrumpir:
                        time.sleep(0.1)
                    
                    # Si fue interrumpido, detener el audio
                    if debe_interrumpir:
                        pygame.mixer.music.stop()
                        print("   [Sistema]: Audio interrumpido")
                    
                    time.sleep(0.5)
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                except Exception as e:
                    print(f"[Warning pygame]: {e}. Usando pyttsx3...")
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 200)  # Velocidad normal-rápido
                    engine.say(texto)
                    engine.runAndWait()
        except Exception as e:
            print(f"[Error Edge TTS]: {e}. Fallback a pyttsx3...")
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)  # Velocidad normal-rápido
            engine.say(texto)
            engine.runAndWait()
        
        # Liberar la UI inmediatamente al terminar de hablar, ANTES del lag de borrado
        esta_hablando = False
        servidor_holografico.cambiar_estado("Escuchando")
        
        if archivo_audio and os.path.exists(archivo_audio):
            try:
                time.sleep(0.2)
                os.remove(archivo_audio)
            except PermissionError:
                print(f"   [Warning] Archivo bloqueado: {os.path.basename(archivo_audio)}")
            except Exception as e:
                pass
    except Exception as e:
        print(f"[Error crítico de voz]: {e}")
    finally:
        esta_hablando = False
        debe_interrumpir = False
        tiempo_fin_hablar = time.time()  # MARCAR cuándo termina de hablar, para ventana activa

def registrar_log(evento, detalles=""):
    try:
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Sanitize for console output to avoid crash
        evento_safe = str(evento).replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("—", "-").replace("✓", "(OK)").replace("✗", "(X)")
        detalles_safe = str(detalles).replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("—", "-").replace("✓", "(OK)").replace("✗", "(X)")
        
        log_line_file = f"[{marca_tiempo}] {evento}"
        if detalles:
            log_line_file += f" | {detalles}"
            
        log_line_console = f"[{marca_tiempo}] {evento_safe}"
        if detalles_safe:
            log_line_console += f" | {detalles_safe}"
            
        print(log_line_console)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line_file + "\n")
    except Exception:
        pass

def cargar_cache():
    global cache_programas
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_programas = json.load(f)
            registrar_log("LOG", f"Cache cargado: {len(cache_programas)} programas")
        except Exception:
            cache_programas = {}
    else:
        cache_programas = {}
    precachear_juegos_locales()

def precachear_juegos_locales():
    global cache_programas
    rutas_locales = [r"C:\Games", r"D:\Games"]
    juegos_locales_nuevos = {}
    
    for ruta_juego in rutas_locales:
        if not os.path.exists(ruta_juego):
            continue
        try:
            for item in os.listdir(ruta_juego):
                ruta_item = os.path.join(ruta_juego, item)
                if os.path.isdir(ruta_item):
                    for archivo in os.listdir(ruta_item):
                        if archivo.lower().endswith(".exe") and not any(x in archivo.lower() for x in ["unins", "crash", "redist", "setup"]):
                            nombre_limpio = archivo.rsplit(".", 1)[0]
                            ruta_completa = os.path.join(ruta_item, archivo)
                            if nombre_limpio not in juegos_locales_nuevos:
                                juegos_locales_nuevos[nombre_limpio] = ruta_completa
        except:
            pass
    
    cache_programas.clear()
    cache_programas.update(juegos_locales_nuevos)
    if cache_programas:
        guardar_cache()

def guardar_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_programas, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def guardar_historial():
    try:
        archivo_historial = f"historial_{datetime.now().strftime('%Y%m%d')}.json"
        with open(archivo_historial, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def cargar_historial_completo():
    global historial
    archivo_historial = f"historial_{datetime.now().strftime('%Y%m%d')}.json"
    if os.path.exists(archivo_historial):
        try:
            with open(archivo_historial, "r", encoding="utf-8") as f:
                historial = json.load(f)
            registrar_log("LOG", f"Historial cargado: {len(historial)} mensajes")
        except Exception:
            historial = []
    else:
        historial = []

def cargar_perfil_usuario():
    global perfil_usuario
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                perfil_usuario = json.load(f)
        except Exception:
            perfil_usuario = crear_perfil_Default()
    else:
        perfil_usuario = crear_perfil_Default()

def crear_perfil_Default():
    return {
        "creado": datetime.now().isoformat(),
        "última_sesión": datetime.now().isoformat(),
        "comandos_favoritos": [],
        "aplicaciones_frecuentes": {},
        "búsquedas_frecuentes": [],
        "horarios_de_uso": {},
        "preferencias": {
            "voz": "es-PE-AlexNeural",
            "modelo": "nube",
            "gamificación": True
        },
        "archivos_recientes": []
    }

def guardar_perfil_usuario():
    global perfil_usuario
    try:
        perfil_usuario["última_sesión"] = datetime.now().isoformat()
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(perfil_usuario, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def guardar_historial_sesion():
    global historial
    try:
        with open(".cache_sesion_anterior.json", "w", encoding="utf-8") as f:
            json.dump(historial[-SESSION_CACHE_WINDOW:], f, ensure_ascii=False)
    except Exception:
        pass

def cargar_historial_sesion():
    global historial
    try:
        if os.path.exists(".cache_sesion_anterior.json"):
            with open(".cache_sesion_anterior.json", "r", encoding="utf-8") as f:
                historial = json.load(f)
    except Exception:
        pass

def actualizar_freq_comandos(comando, intención):
    global perfil_usuario
    if "comandos_favoritos" not in perfil_usuario:
        perfil_usuario["comandos_favoritos"] = []
    entrada = f"{intención}:{comando}"
    if entrada in perfil_usuario["comandos_favoritos"]:
        idx = perfil_usuario["comandos_favoritos"].index(entrada)
        perfil_usuario["comandos_favoritos"].pop(idx)
    perfil_usuario["comandos_favoritos"].insert(0, entrada)
    perfil_usuario["comandos_favoritos"] = perfil_usuario["comandos_favoritos"][:10]
    guardar_perfil_usuario()

def obtener_archivos_recientes(limite=5):
    try:
        recent_path = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent")
        archivos = []
        for archivo in sorted(os.listdir(recent_path), key=lambda x: os.path.getmtime(os.path.join(recent_path, x)), reverse=True)[:limite]:
            if not archivo.startswith('_'):
                archivos.append(archivo.replace('.lnk', ''))
        return archivos
    except Exception:
        return []

def ejecutar(datos_ia, comando_original=""):
    global modo_gaming, navegador_movido

    intencion_raw = datos_ia.get("intencion", datos_ia.get("Intencion", datos_ia.get("accion", "conversar")))
    intencion = str(intencion_raw).lower().strip()
    comando_raw = datos_ia.get("comando", datos_ia.get("Comando", datos_ia.get("app", "null")))
    comando = str(comando_raw).lower().strip()
    respuesta = datos_ia.get("respuesta", datos_ia.get("Respuesta", "Ejecutando orden..."))
    
    if comando and comando != "null" and len(comando.split()) <= 2 and intencion != "abrir":
        comando_limpio = re.sub(r'[^a-z0-9\s]', '', comando)
        palabras_genericas = ["guía", "guide", "tutorial", "como", "how", "busca", "search", "info", "información"]
        if any(p in comando_limpio for p in palabras_genericas) and comando_original:
            comando_original_limpio = re.sub(r'[^a-z0-9\s]', '', comando_original.lower())
            if comando_original_limpio and len(comando_original_limpio) > len(comando):
                comando = comando_original
                print(f"   [Sistema]: Contexto reconstruido: '{comando}'")
    
    # Especialmente importante para BUSCAR: asegurar que tiene el contexto completo
    if intencion == "buscar" and comando_original and comando != comando_original:
        comando_original_limpio = comando_original.lower()
        # Si el comando original contiene el tema, úsalo directamente
        if len(comando_original_limpio) > len(comando) and any(pal in comando_original_limpio for pal in ["guía", "tutorial", "cómo", "como"]):
            comando = comando_original_limpio
            print(f"   [Sistema]: Búsqueda completa: '{comando}'")
    
    print(f"\n[Dayan]: {respuesta}")
    print(f"   [Debug] Intención: '{intencion}' | Comando: '{comando}'")
    hablar_async(respuesta)
    
    if intencion == "dictado_codigo":
        # Aviso verbal ya fue lanzado. Esperar lo suficiente para que empiece/termine de hablar el aviso corto
        time.sleep(2.5)
        print("   [Sistema]: Pegando código en editor vía pyperclip...")
        registrar_log("CODE_GEN", "Pegando bloque de código")
        
        try:
            import pyperclip
        except ImportError:
            print("   [Error]: pyperclip no está instalado. Ejecute 'pip install pyperclip'")
            hablar_async("Señor, debe instalar pyperclip para habilitar el copiado.")
            return

        vscode_ok = enfocar_vscode_simple()
        if vscode_ok:
            import platform
            pyperclip.copy(comando)
            if platform.system() == "Darwin":
                pyautogui.hotkey('command', 'v')
            else:
                pyautogui.hotkey('ctrl', 'v')
            print("   ✓ Código insertado exitosamente con Ctrl+V.")
        else:
            print("   ✗ No se pudo enfocar VS Code automáticamente. Asegúrese de tenerlo abierto.")
        return
    
    if intencion == "conversar":
        registrar_log("CONVERSA", comando)
        if any(palabra in comando_original.lower() for palabra in ["jugar", "juego", "gaming", "play"]):
            juegos_disponibles = get_juegos_jugables()
            if juegos_disponibles and len(juegos_disponibles) > 0:
                juegos_cortos = juegos_disponibles[:8]
                print(f"\n   💾 Juegos disponibles: {', '.join(juegos_cortos)}")
                if len(juegos_disponibles) > 8:
                    print(f"      ... y {len(juegos_disponibles) - 8} más")
        # Si pregunta por ventanas abiertas, mostrar qué tiene abierto
        elif any(palabra in comando_original.lower() for palabra in ["abierto", "tengo abierto", "qué tengo", "ventanas", "ver pantalla", "qué hay"]):
            ventanas_texto = obtener_ventanas_texto()
            print(f"\n   [Sistema]: {ventanas_texto}")
        return
        
    if intencion == "abrir" and comando and comando != "null":
        registrar_log("ABRIR", comando)
        
        # Limpiar comando: remover palabras como "abrir", "ejecutar", "abre", "inicia"
        palabras_abrir = ["abrir", "ejecutar", "abre", "inicia", "abierto"]
        comando_limpio_inicial = comando.lower()
        for palabra in palabras_abrir:
            comando_limpio_inicial = comando_limpio_inicial.replace(f"{palabra} ", "").replace(f"{palabra}", "")
        comando_limpio_inicial = comando_limpio_inicial.strip()
        
        # Si quedó vacío, usar el comando original
        if not comando_limpio_inicial or comando_limpio_inicial == "null":
            comando_limpio_inicial = comando
        
        # Si menciona "juego" o el comando contiene componentes de juegos favoritos, buscar por juego favorito
        comando_es_juego = any(palabra in comando_original.lower() for palabra in ["jugar", "juego", "gaming", "play"])
        juego_a_buscar = comando_limpio_inicial
        
        if comando_es_juego:
            comando_limpio = re.sub(r'[^a-z0-9\s]', '', comando_limpio_inicial.lower())
            for juego_fav in PERFIL_RENZO.get("juegos_favoritos", []):
                juego_limpio = re.sub(r'[^a-z0-9\s]', '', juego_fav.lower())
                # Si el comando contiene palabras clave del juego favorito, usar el nombre completo
                palabras_juego = [p for p in juego_limpio.split() if len(p) > 2]
                if any(p in comando_limpio for p in palabras_juego if len(p) > 2):
                    print(f"   [Sistema]: Detectado juego favorito: '{juego_fav}'")
                    juego_a_buscar = juego_fav
                    break
        
        ruta_programa = buscar_programa(juego_a_buscar)
        if ruta_programa:
            try:
                juegos_clave = ["dispatch", "expedition", "persona", "games", "steam", "epic"]
                if any(clave in ruta_programa.lower() for clave in juegos_clave):
                    print("   [Sistema]: ¡Juego pesado detectado! Activando Modo Gaming (Cerebro Nube)...")
                    print("   [Sistema]: La VRAM está 100% libre porque la IA está alojada en Google.")
                    modo_gaming = True
                    registrar_log("MODO GAMING", "ACTIVADO")
                else:
                    if modo_gaming:
                        print("   [Sistema]: Programa de trabajo detectado. Desactivando Modo Gaming...")
                        modo_gaming = False
                        registrar_log("MODO GAMING", "DESACTIVADO")

                try:
                    carpeta_juego = os.path.dirname(ruta_programa)
                    subprocess.Popen(ruta_programa, cwd=carpeta_juego, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                except Exception as e:
                    print(f"[Sistema]: Fallback a startfile - {e}")
                    os.startfile(ruta_programa)
                
                print(f"   [Sistema]: ✓ Lanzado -> {os.path.basename(ruta_programa)}")
            except OSError as e:
                print(f"[Error]: No se pudo lanzar el programa.")
        else:
            comando_limpio = re.sub(r'[^a-z0-9\s]', '', comando.lower())
            palabras = comando_limpio.split()
            sugerencias = []
            
            # Si es una búsqueda de juego, buscar juegos favoritos que SÍ estén instalados
            if comando_es_juego:
                juegos_instalados = get_juegos_jugables()
                for juego_fav in PERFIL_RENZO.get("juegos_favoritos", []):
                    juego_fav_limpio = re.sub(r'[^a-z0-9\s]', '', juego_fav.lower())
                    for juego_inst in juegos_instalados:
                        if juego_fav_limpio.split()[0] in juego_inst.lower():  # Match por primera palabra
                            sugerencias.append(juego_fav)
                            break
            
            # Si no encontró juegos favoritos, buscar por caché general
            if not sugerencias:
                for prog_en_cache in cache_programas.keys():
                    prog_limpio = re.sub(r'[^a-z0-9\s]', '', prog_en_cache.lower())
                    if any(palabra in prog_limpio for palabra in palabras if len(palabra) > 2):
                        sugerencias.append(prog_en_cache)
            
            print(f"[Sistema]: ✗ No encontré '{comando}'.")
            if sugerencias:
                print(f"   Sugerencias disponibles:")
                for sug in sugerencias[:3]:
                    print(f"     • {sug}")
            else:
                juegos_inst = get_juegos_jugables()
                if juegos_inst and comando_es_juego:
                    print(f"   Juegos disponibles: {', '.join(juegos_inst[:5])}")
                    if len(juegos_inst) > 5:
                        print(f"   ... y {len(juegos_inst) - 5} más.")
                else:
                    print(f"   Verifica que esté instalado.")
            
    elif intencion == "cerrar":
        try:
            ventana_activa = gw.getActiveWindow() if gw else None
            ventana_titulo = ventana_activa.title.lower() if ventana_activa else ""
            
            # Limpiar comando: remover palabras como "cerrar", "cierra", "apaga", etc.
            palabras_cerrar = ["cerrar", "cierra", "apaga", "apague", "cierre", "quita", "quitar", "sal de"]
            comando_limpio_inicial = comando.lower() if comando else ""
            for palabra in palabras_cerrar:
                if palabra in comando_limpio_inicial:
                    comando_limpio_inicial = comando_limpio_inicial.replace(f"{palabra} ", "").replace(palabra, "")
            comando_limpio_inicial = comando_limpio_inicial.strip()
            
            # Si quedó vacío, usar el comando original
            if not comando_limpio_inicial or comando_limpio_inicial == "null":
                comando = None
            else:
                comando = comando_limpio_inicial
            
            # Si el comando menciona OBS, Spider-Man, juego, etc., cierra específicamente eso
            aplicacion_a_cerrar = None
            if comando and comando != "null":
                comando_lower = comando.lower()
                comando_limpio = re.sub(r'[^a-z0-9\s]', '', comando_lower)
                
                ventanas = listar_ventanas_abiertas()
                print(f"   [Debug] Buscando '{comando}' entre {len(ventanas)} ventanas...")
                
                # PRIMERO: Búsqueda ESTRICTA - comando limpio EN título limpio
                for ventana in ventanas:
                    ventana_titulo_lower = ventana.title.lower()
                    ventana_limpia = re.sub(r'[^a-z0-9\s]', '', ventana_titulo_lower)
                    
                    # Si el comando está EXACTO en el título
                    if comando_limpio in ventana_limpia or ventana_limpia in comando_limpio:
                        aplicacion_a_cerrar = ventana
                        print(f"   [Debug] ✓ Coincidencia estricta: '{ventana.title}'")
                        break
                
                # SEGUNDA: Búsqueda FLEXIBLE - cualquier palabra del comando en el título
                if not aplicacion_a_cerrar:
                    palabras_comando = comando_limpio.split()
                    for ventana in ventanas:
                        ventana_titulo_lower = ventana.title.lower()
                        ventana_limpia = re.sub(r'[^a-z0-9\s]', '', ventana_titulo_lower)
                        
                        # Si TODAS las palabras principales están en la ventana
                        palabras_principales = [p for p in palabras_comando if len(p) > 2]
                        if palabras_principales and all(palabra in ventana_limpia for palabra in palabras_principales):
                            aplicacion_a_cerrar = ventana
                            print(f"   [Debug] ✓ Coincidencia por palabras clave: '{ventana.title}'")
                            break
                
                # TERCERA: Búsqueda MUY FLEXIBLE - cualquier palabra del comando
                if not aplicacion_a_cerrar:
                    for ventana in ventanas:
                        ventana_titulo_lower = ventana.title.lower()
                        # Buscar si el COMANDO está en el TÍTULO o viceversa (con tolerancia)
                        if any(palabra in ventana_titulo_lower for palabra in palabras_comando if len(palabra) > 1):
                            aplicacion_a_cerrar = ventana
                            print(f"   [Debug] ✓ Coincidencia flexible: '{ventana.title}'")
                            break
                
                # CUARTA: Si pide "cierra juego" pero no especifica cuál, buscar juego ACTIVO
                if not aplicacion_a_cerrar and ("juego" in comando_lower or "game" in comando_lower):
                    palabras_juego = ["steam", "epic", "dispatch", "expedition", "persona", "control", "dead", "quantum", "mario", "zelda"]
                    for ventana in ventanas:
                        ventana_titulo_lower = ventana.title.lower()
                        if any(juego_palabra in ventana_titulo_lower for juego_palabra in palabras_juego):
                            aplicacion_a_cerrar = ventana
                            print(f"   [Debug] ✓ Detectado juego: '{ventana.title}'")
                            break
            
            # Si encontró la app específica, ciérrala
            if aplicacion_a_cerrar:
                print(f"   [Sistema]: Cerrando '{aplicacion_a_cerrar.title}'...")
                registrar_log("CERRAR", aplicacion_a_cerrar.title)
                try:
                    aplicacion_a_cerrar.close()
                    print(f"   ✓ {aplicacion_a_cerrar.title} cerrado")
                except:
                    # Si close() no funciona, usar Alt+F4
                    aplicacion_a_cerrar.activate()
                    time.sleep(0.3)
                    pyautogui.hotkey('alt', 'f4')
            else:
                # NO ENCONTRÓ LA APP ESPECIFICADA
                if comando and comando != "null":
                    print(f"   [Sistema]: No encontré '{comando}' abierto.")
                    print(f"   [Sistema]: Dime el nombre exacto o simplemente 'cierra' para la ventana activa.")
                    return
                
                # Si NO hay comando (solo "cierra"), cerrar ventana activa CON PROTECCIONES FUERTES
                palabras_a_proteger = [
                    "cmd", "powershell", "terminal", "windows terminal", "pwsh", "conhost",
                    "explorer", "file", "windows", "system", "settings", "control panel",
                    "task manager", "services", "regedit", "defender", "antivirus"
                ]
                es_critica = any(palabra in ventana_titulo for palabra in palabras_a_proteger)
                
                if es_critica:
                    print("   [Sistema]: No puedo cerrar programas críticos del sistema, Señor.")
                    print("   [Sistema]: Especifica qué aplicación quieres cerrar.")
                    return
                else:
                    print(f"   [Sistema]: Cerrando ventana activa '{ventana_activa.title if ventana_activa else 'desconocida'}'...")
                    registrar_log("CERRAR", ventana_titulo or "ventana activa")
                    if ventana_activa:
                        try:
                            ventana_activa.close()
                        except:
                            pyautogui.hotkey('alt', 'f4')
        except Exception as e:
            print(f"   [Sistema]: Error al cerrar - {e}")
        
        if modo_gaming:
            print("   [Sistema]: Desactivando Modo Gaming...")
            modo_gaming = False
    
    elif intencion == "grabar":
        print("   [Sistema]: Iniciando setup de grabación...")
        registrar_log("GRABAR", "setup grabación TikTok")
        configurar_setup_grabacion()

    elif intencion == "control_obs":
        def enviar_hotkey_obs(tecla):
            try:
                obs_window = None
                ventana_activa_original = None
                if gw:
                    try:
                        ventana_activa_original = gw.getActiveWindow()
                    except:
                        pass
                    for v in gw.getAllWindows():
                        if v.title and "OBS " in v.title:
                            obs_window = v
                            break
                if obs_window:
                    try:
                        if obs_window.isMinimized:
                            obs_window.restore()
                        obs_window.activate()
                        time.sleep(0.3)
                    except:
                        pass
                    pyautogui.hotkey('alt', tecla)
                    time.sleep(0.1)
                    if ventana_activa_original and ventana_activa_original.title != obs_window.title:
                        try:
                            ventana_activa_original.activate()
                        except:
                            pass
                else:
                    pyautogui.hotkey('alt', tecla)
            except Exception as e:
                print(f"   [Sistema]: Error invocando OBS: {e}")
                pyautogui.hotkey('alt', tecla)

        if comando == "iniciar":
            print("   [Sistema]: Iniciando grabación en OBS (ALT+B)...")
            registrar_log("OBS", "iniciar grabación")
            enviar_hotkey_obs('b')
        elif comando == "detener":
            print("   [Sistema]: Deteniendo grabación en OBS (ALT+N)...")
            registrar_log("OBS", "detener grabación")
            enviar_hotkey_obs('n')

    elif intencion == "wikipedia" and comando and comando not in ["null", "none", "", "ninguno"]:
        print(f"   [Sistema]: Buscando '{comando}' en Wikipedia...")
        registrar_log("WIKIPEDIA", comando)
        resultado = buscar_wikipedia(comando)
        print(f"   [Dayan]: {resultado}")

    elif intencion == "hora":
        print("   [Sistema]: Obteniendo hora actual...")
        registrar_log("HORA", "información de la hora")
        hora_actual = obtener_hora()
        print(f"   [Dayan]: {hora_actual}")

    elif intencion == "clima":
        print("   [Sistema]: Consultando información del clima...")
        registrar_log("CLIMA", "información del clima")
        info_clima = obtener_climate()
        print(f"   [Dayan]: {info_clima}")

    elif intencion == "noticias":
        print("   [Sistema]: Obteniendo noticias...")
        registrar_log("NOTICIAS", "últimos titulares")
        categoria = None
        if comando and comando not in ["null", "none", "", "ninguno"]:
            categoria = comando.lower().strip()
        noticias = obtener_noticias(pais="es", categoria=categoria)
        print(f"   [Dayan]: {noticias}")

    elif intencion == "info_sistema":
        print("   [Sistema]: Analizando estado del sistema...")
        registrar_log("INFO_SISTEMA", "diagnóstico del sistema")
        info = obtener_info_sistema()
        print(f"   [Dayan]: {info}")

    elif intencion == "reproducir" and comando and comando not in ["null", "none", "", "ninguno"]:
        # Limpiar comando de palabras de control (pon en youtube, busca en youtube, etc)
        comando_limpio = comando.lower()
        palabras_deshabilitar = ["pon en youtube", "busca en youtube", "reproduce en youtube", "busca youtube", "pon youtube", "reproduce youtube"]
        for palabra in palabras_deshabilitar:
            comando_limpio = comando_limpio.replace(palabra, "").strip()
        
        # Extraer solo lo que hay que buscar
        tema_busqueda = comando_limpio if comando_limpio else comando
        
        # Interceptar música pura sin artista
        if tema_busqueda.strip().lower() in ["música", "musica", "musica en youtube", "música para escuchar"]:
            print("   [Sistema]: Petición de música genérica interceptada.")
            hablar_async("¿Qué artista o track desea que ponga, Señor?")
            registrar_log("REPRODUCIR (BLOQUEADO)", "Petición genérica")
            return
            
        print(f"   [Sistema]: Reproduciendo '{tema_busqueda}' en YouTube...")
        registrar_log("REPRODUCIR", tema_busqueda)
        try:
            pywhatkit.playonyt(tema_busqueda)
            time.sleep(6) 
            # SOLO mover a segunda pantalla si hay REALMENTE un juego activo
            if mode_gaming_deberia_estar_activo() and hay_segunda_pantalla():
                print("   [Sistema]: Moviendo YouTube a segunda pantalla (Juego detectado)...")
                mover_a_segunda_pantalla()
            else:
                print("   [Sistema]: YouTube en pantalla principal")
        except Exception as e:
            print(f"[Error]: No se pudo reproducir - {e}")

    elif intencion == "control_media":
        print("   [Sistema]: Ejecutando control multimedia...")
        registrar_log("MEDIA", comando_original)
        # Usamos el comando procesado por la IA o pre-asignado por el shortcut
        comando_lower = comando.lower() + " " + comando_original.lower()
        if any(p in comando_lower for p in ["pausa", "pausar", "resume", "continúa", "reanuda", "play"]):
            pyautogui.press('playpause')
        elif any(p in comando_lower for p in ["siguiente", "próxima", "salta"]):
            pyautogui.press('nexttrack')
        elif any(p in comando_lower for p in ["anterior", "regresa"]):
            pyautogui.press('prevtrack')
        elif any(p in comando_lower for p in ["sube", "subir", "más", "aumenta"]) and "volumen" in comando_lower:
            for _ in range(5): pyautogui.press('volumeup')
        elif any(p in comando_lower for p in ["baja", "bajar", "menos", "disminuye"]) and "volumen" in comando_lower:
            for _ in range(5): pyautogui.press('volumedown')
        elif "silencia" in comando_lower or "mute" in comando_lower:
            pyautogui.press('volumemute')

    elif intencion == "buscar" and comando and comando not in ["null", "none", "", "ninguno"]:
        print(f"   [Sistema]: Buscando '{comando}' en web...")
        registrar_log("BUSCAR", comando)
        url_busqueda = f"https://duckduckgo.com/?q=!ducky+{urllib.parse.quote(comando)}"
        try:
            os.startfile(url_busqueda)
            time.sleep(8)  # Esperar a que cargue completamente
            # SOLO mover a segunda pantalla si hay REALMENTE un juego activo
            if mode_gaming_deberia_estar_activo() and hay_segunda_pantalla():
                print("   [Sistema]: Moviendo búsqueda a segunda pantalla (Juego detectado)...")
                mover_a_segunda_pantalla()
            else:
                print("   [Sistema]: Búsqueda en pantalla principal")
        except Exception as e:
            print(f"[Error]: No se pudo abrir la búsqueda - {e}")

if __name__ == "__main__":
    print("Dayan v10.0 EN LÍNEA - POTENCIADO POR GROQ (HARDWARE ACELERADOR)")
    print("=" * 60)
    print("[INFO] Motor de IA: Groq Mixtral 8x7B | Latencia: ULTRABAJA")
    print("[INFO] Hardware acelerador Groq activado - Respuestas instantáneas")
    print("=" * 60)
    
    # ⚡ DIAGNÓSTICO DE MICRÓFONO AL INICIAR
    diagnosticar_microfono()
    
    # RESETEAR ESTADO DE AUDIO AL INICIO (sin global, estamos al nivel del módulo)
    pygame_mixer_silenciado = False
    try:
        if pygame and pygame.mixer.get_init():
            pygame.mixer.music.set_volume(1.0)
    except:
        pass
    
    cargar_cache()
    # Comentado: Para que DiaNe empiece SIN historial anterior (sesión limpia)
    # cargar_historial_completo()
    # cargar_historial_sesion()
    cargar_perfil_usuario()
    registrar_log("INICIO", f"Jarvis/Dayan iniciado en Nube.")
    
    servidor_holografico.iniciar_servidor()
    
    # Auto-ejecución del Interfaz Visual Holográfico (index.html) - guardamos proceso para matarlo al salir
    _browser_proc = None
    try:
        import os, subprocess, webbrowser, tempfile
        ruta_index = os.path.abspath(os.path.join(os.path.dirname(__file__), "public", "index.html"))
        if os.path.exists(ruta_index):
            print("   [Sistema]: Proyectando interfaz visual en pantalla...")
            procesadores_web = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            browser_sel = next((p for p in procesadores_web if os.path.exists(p)), None)
            if browser_sel:
                temp_profile = os.path.join(tempfile.gettempdir(), "DayanAppLayer")
                _browser_proc = subprocess.Popen([
                    browser_sel,
                    f"--app=file:///{ruta_index.replace(chr(92), '/')}",
                    f"--window-size={UI_ANCHO},{UI_ALTO}",
                    f"--window-position={UI_POS_X},{UI_POS_Y}",
                    f"--user-data-dir={temp_profile}",
                    "--disable-extensions"
                ])
                iniciar_anclaje_ventana_ui("DiaNe OS")
            else:
                webbrowser.open(f"file:///{ruta_index.replace(chr(92), '/')}")
    except Exception as ev_ui:
        print(f"   [Advertencia]: No se pudo proyectar la UI: {ev_ui}")

    saludar_inicial()

    if AUTO_ESCUCHA_FORZADA_AL_INICIAR:
        forzar_escucha = True
        print("   [Sistema]: Escucha automática inicial activada (tipo F9)")
    
    # Iniciar monitoreo de hotkeys en background
    if PYNPUT_DISPONIBLE:
        thread_hotkeys = Thread(target=monitorear_hotkeys, daemon=True)
        thread_hotkeys.start()
        print("   [Sistema]: Hotkeys activos (F7=silenciar, F8=parar, F9=escucha forzada)")
    
    tiempo_ultima_orden = time.time() if AUTO_ESCUCHA_FORZADA_AL_INICIAR else 0
    tiempo_espera = 90  # Ventana activa: 90 segundos de silencio antes de dormir
    try:
      while True:
        
        # ─── CHEQUEO DE CIERRE ORDENADO (navegador cerrado o comando de cierre) ───
        if os.path.exists("desactivar_protocolos.txt"):
            print("   [Sistema]: Cierre ordenado detectado - Apagando Dayan...")
            guardar_historial()
            guardar_perfil_usuario()
            registrar_log("CIERRE", "Cierre ordenado por usuario (navegador cerrado).")
            try:
                os.remove("desactivar_protocolos.txt")
            except Exception:
                pass
            break
        
        # --- MODO PAUSA (activado desde la UI web) ---
        if os.path.exists("dayan_pausado.txt"):
            servidor_holografico.cambiar_estado("Inactivo")
            time.sleep(0.5)
            continue

        tiempo_actual = time.time()
        # DESPIERTO si: fue orden reciente O Dayan terminó de hablar hace menos de tiempo_espera segundos
        # tiempo_fin_hablar se actualiza en el hilo hablar() al terminar la reproducción
        tiempo_referencia = max(tiempo_ultima_orden, tiempo_fin_hablar)
        esta_despierto = ((tiempo_actual - tiempo_referencia) <= tiempo_espera or modo_dictado_vscode) and not modo_reposo_manual
        fue_offline = False 
        comando_crudo = None
        
        # --- INTERCEPCIÓN WEBSOCKET UI ---
        try:
            if os.path.exists("forzar_escucha.txt"):
                os.remove("forzar_escucha.txt")
                forzar_escucha = True
            
            if os.path.exists("comando_gui.txt"):
                with open("comando_gui.txt", "r", encoding="utf-8") as f:
                    comando_crudo = f.read().strip()
                os.remove("comando_gui.txt")
        except Exception:
            pass

        if comando_crudo:
            print(f"   [UI Web]: Comando recibido -> {comando_crudo}")
        elif forzar_escucha:
            # SI SE PRESIONÓ F9 O BOTÓN WEB: FORZAR ESCUCHA COMPLETA
            forzar_escucha = False
            print("   [IA]: ✓ Escucha forzada activada")
            comando_crudo = escuchar(forzada=True)
        elif not esta_despierto:
            # Modo dormido: esperar palabra clave (OWW o Google SR)
            comando_capturado, fue_offline = detectar_activacion_y_capturar_comando()

            # Si nada ocurrió (ni OWW ni Google SR detectaron nada), volver a dormir
            if comando_capturado is None and not fue_offline:
                time.sleep(0.5)
                continue

            # Activación confirmada! Despertar y escuchar el comando real
            if modo_reposo_manual:
                modo_reposo_manual = False
                print("   [IA]: Modo reposo desactivado por palabra clave")
            tiempo_ultima_orden = time.time()  # Iniciar ventana activa de 12s
            print("   [IA]: \u2713 Activada \u2014 Di tu orden, Se\u00f1or")

            if comando_capturado and len(comando_capturado.strip()) > 4:
                # Google SR ya capturó el comando junto con la palabra clave
                comando_crudo = comando_capturado
                print(f"   [Sistema]: Comando en activación: '{comando_crudo}'")
            else:
                # OWW activó o Google SR no tiene suficiente texto — escuchar
                comando_crudo = escuchar()
        else:
            # MODO ACTIVO: escucha sin palabra clave
            if not debe_interrumpir:
                print("   [IA]: Te escucho... (ventana activa)")
            else:
                print("\n   [IA]: Escucho tu nuevo comando...")
            comando_crudo = escuchar(forzada=debe_interrumpir)
            debe_interrumpir = False
        
        # Actualizar tiempo_última_orden solo DESPUÉS de tener el comando listo
        if comando_crudo:
            # El texto ya se emitió en escuchar(), no duplicar
            
            # INTERRUPCIÓN ACTIVA TIPO ALEXA: Si habló y capturamos algo válido, callar la voz
            if esta_hablando:
                print("\n   [Sistema]: ¡Interrumpida por nueva orden de voz!")
                debe_interrumpir = True
                
            tiempo_ultima_orden = time.time()
        
        if comando_crudo:
            comando_lower = comando_crudo.lower()
            comando_a_procesar = comando_crudo

            # Reposo manual: ignorar TODO excepto frases explícitas para reactivar
            if modo_reposo_manual:
                if any(f in comando_lower for f in FRASES_REACTIVAR):
                    modo_reposo_manual = False
                    tiempo_ultima_orden = time.time()
                    servidor_holografico.cambiar_estado("Escuchando")
                    hablar_async("Reactivada, Señor. Lo escucho.")
                else:
                    servidor_holografico.cambiar_estado("Inactivo")
                    print("   [IA]: En reposo manual. Comando ignorado hasta reactivación.")
                continue
            
            tiempo_ultima_orden = time.time()
            
            # LIMPIEZA AUTOMÁTICA DE MP3s VIEJOS
            limpiar_archivos_mp3()
            
            if "desactivar protocolos de jarvis" in comando_lower:
                print("Apagando a Dayan...")
                guardar_historial()
                guardar_perfil_usuario()
                registrar_log("CIERRE", "Asistente desconectado. Perfil guardado.")
                break

            # Modo dictado VSCode (evita llamadas a IA y consumo de tokens)
            frases_desactivar_dictado = [
                "desactiva dictado",
                "salir de dictado",
                "terminar dictado",
                "apaga dictado",
                "detener dictado"
            ]

            frases_confirmar_envio = [
                "enviar", "si enviar", "sí enviar", "conforme", "si", "sí", "ok enviar", "mandar"
            ]
            frases_cancelar_envio = [
                "no enviar", "cancelar", "descartar", "no", "corregir", "editar"
            ]

            if es_activar_dictado_vscode(comando_lower):
                modo_dictado_vscode = True
                dictado_borrador = ""
                esperando_confirmacion_envio = False
                tiempo_ultima_orden = time.time()
                print("   [Dictado]: Modo dictado VSCode ACTIVADO")
                vscode_ok = abrir_o_enfocar_vscode()
                if vscode_ok:
                    hablar_async("Modo dictado en VSCode activado, Señor. Dicte su mensaje y luego le preguntaré si lo envío.")
                else:
                    hablar_async("Modo dictado activado, Señor. No pude enfocar VSCode automáticamente, enfoque la caja de texto y dicte.")
                forzar_escucha = True
                continue

            if any(f in comando_lower for f in frases_desactivar_dictado):
                modo_dictado_vscode = False
                dictado_borrador = ""
                esperando_confirmacion_envio = False
                print("   [Dictado]: Modo dictado VSCode DESACTIVADO")
                hablar_async("Dictado desactivado, Señor.")
                continue

            if modo_dictado_vscode:
                if esperando_confirmacion_envio:
                    if any(f in comando_lower for f in frases_confirmar_envio):
                        enviado = enviar_dictado_a_vscode(dictado_borrador)
                        if enviado:
                            registrar_log("DICTADO_VSCODE", dictado_borrador)
                            print(f"   [Dictado]: Enviado -> {dictado_borrador}")
                            hablar_async("Enviado, Señor. Puede dictar el siguiente mensaje.")
                        else:
                            hablar_async("No pude enviarlo, Señor. Verifique que la caja de texto esté enfocada.")
                        dictado_borrador = ""
                        esperando_confirmacion_envio = False
                        forzar_escucha = True
                        continue

                    if any(f in comando_lower for f in frases_cancelar_envio):
                        print("   [Dictado]: Borrador descartado")
                        dictado_borrador = ""
                        esperando_confirmacion_envio = False
                        hablar_async("Perfecto, Señor. Dicteme el nuevo mensaje.")
                        forzar_escucha = True
                        continue

                    hablar_async("No entendí la confirmación, Señor. Diga enviar o cancelar.")
                    forzar_escucha = True
                    continue

                dictado_borrador = comando_a_procesar.strip()
                if dictado_borrador:
                    print(f"   [Dictado]: Borrador -> {dictado_borrador}")
                    esperando_confirmacion_envio = True
                    hablar_async("Señor, ¿está conforme con el texto? Diga enviar o cancelar.")
                    forzar_escucha = True
                continue

            shortcut_detectado = False
            # Shortcuts SOLO si:
            # 1. Comando CORTO (< 40 caracteres)
            # 2. La palabra clave está en PRIMERAS 2 posiciones
            # 3. Es una PALABRA COMPLETA (no substring como "play" en "auronplay")
            if len(comando_lower) < 40:
                palabras = comando_lower.split()
                primeras_palabras = " ".join(palabras[:2])  # Primeras 2 palabras como string
                
                for palabra_clave, accion in shortcuts.items():
                    # Si es frase de varias palabras, buscar en string; si no, como token completo
                    if (" " in palabra_clave and palabra_clave in primeras_palabras) or (" " not in palabra_clave and palabra_clave in primeras_palabras.split()):
                        registrar_log("SHORTCUT", palabra_clave)
                        if "cerrar" in accion:
                            ejecutar({"intencion": "cerrar", "comando": "ventana", "respuesta": "Cerrando."}, comando_crudo)
                        elif "playpause" in accion:
                            ejecutar({"intencion": "control_media", "comando": "pausa", "respuesta": "Modificando reproducción, Señor."}, comando_crudo)
                        elif "nexttrack" in accion:
                            ejecutar({"intencion": "control_media", "comando": "siguiente", "respuesta": "Cambiando de tema."}, comando_crudo)
                        elif "youtube música" in accion:
                            ejecutar({"intencion": "reproducir", "comando": "música para trabajar", "respuesta": "Poniendo música en YouTube."}, comando_crudo)
                        elif "dormir" in accion:
                            modo_reposo_manual = True
                            tiempo_ultima_orden = 0
                            hablar_async("Entrando en estado de reposo. Llámame si me necesitas, Señor.")
                            servidor_holografico.cambiar_estado("Inactivo")
                        shortcut_detectado = True
                        break
            if shortcut_detectado:
                continue

            if "cierra" in comando_lower and ("juego" in comando_lower or "ventana" in comando_lower or "dispatch" in comando_lower or "expedition" in comando_lower):
                ejecutar({"intencion": "cerrar", "comando": "ventana activa"}, comando_crudo)
                registrar_log("COMANDO", "cierre directo sin IA")
                continue
                
            if any(frase in comando_a_procesar.lower() for frase in ['desactiva el modo', 'modo normal', 'ya no estoy jugando']):
                modo_gaming = False
                print("\n   [Sistema]: Modo Gaming DESACTIVADO.")
                registrar_log("MODO GAMING MANUAL", "DESACTIVADO")
                continue 
                
            if any(frase in comando_a_procesar.lower() for frase in ['activa el modo', 'estoy jugando', 'modo gaming']):
                modo_gaming = True
                print("\n   [Sistema]: Modo Gaming ACTIVADO.")
                registrar_log("MODO GAMING MANUAL", "ACTIVADO")
                continue
                
            datos_ia = pensar(comando_a_procesar)
            actualizar_freq_comandos(comando_a_procesar, datos_ia.get("intencion", "conversa"))
            ejecutar(datos_ia, comando_a_procesar)
            continue  # Volver al inicio del loop sin hacer más preguntas
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        # Limpiar archivos de estado al salir
        for _f in ["dayan_pausado.txt", "forzar_escucha.txt", "comando_gui.txt"]:
            try: os.remove(_f)
            except: pass
        # Cerrar ventana del navegador si sigue abierta
        if _browser_proc:
            try: _browser_proc.terminate()
            except: pass
        print("\n   [Sistema]: Dayan apagado. Hasta luego, Señor.")
        guardar_historial()
        guardar_perfil_usuario()
