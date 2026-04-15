#!/usr/bin/env python3
"""
Script para testear el micrófono y la captura de audio
"""
import speech_recognition as sr
import pyaudio
import numpy as np

print("\n" + "="*60)
print("🔧 TEST DE MICRÓFONO")
print("="*60)

# Test 1: PyAudio
print("\n[1] Verificando PyAudio...")
try:
    p = pyaudio.PyAudio()
    print(f"✓ PyAudio disponible")
    print(f"  Dispositivos totales: {p.get_device_count()}")
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  [{i}] 🎤 {info['name'][:50]}")
    
    default_idx = p.get_default_input_device_index()
    default_info = p.get_device_info_by_index(default_idx)
    print(f"\n  Por defecto: [{default_idx}] {default_info['name']}")
    p.terminate()
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: speech_recognition
print("\n[2] Verificando speech_recognition...")
try:
    r = sr.Recognizer()
    print(f"✓ speech_recognition disponible")
    print(f"  Energy threshold: {r.energy_threshold}")
    print(f"  Dynamic energy: {r.dynamic_energy_threshold}")
    print(f"  Pause threshold: {r.pause_threshold}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Captura de audio
print("\n[3] Probando captura de audio (30 segundos)...")
print("   Habla ahora...\n")

try:
    r = sr.Recognizer()
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print("   Calibrando ruido ambiente (2s)...")
        r.adjust_for_ambient_noise(source, duration=2)
        print(f"   Energy threshold ajustado a: {r.energy_threshold}")
        
        print("   ESCUCHANDO... (máx 30s)")
        try:
            audio = r.listen(source, timeout=30, phrase_time_limit=25)
            print(f"   ✓ Audio capturado ({len(audio.frame_data)} bytes)")
            
            print("   Procesando con Google SR...")
            texto = r.recognize_google(audio, language="es-ES")
            print(f"\n   ✅ ÉXITO: '{texto}'")
            
        except sr.UnknownValueError:
            print("   ❌ Audio capturado pero no se entiende")
        except sr.RequestError as e:
            print(f"   ⚠️  Error API Google: {e}")
        except sr.WaitTimeoutError:
            print("   ⏱️  Timeout - no se detectó sonido")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60 + "\n")
