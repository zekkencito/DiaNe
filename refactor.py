import sys

with open('jarvis.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if line.startswith('def detectar_activacion_y_capturar_comando'):
        start_idx = i
    elif line.startswith('def diagnosticar_microfono'):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_func = """def detectar_activacion_y_capturar_comando(ruta_modelo="hey_jarvis_v0.1.onnx"):
    import speech_recognition as sr
    import servidor_holografico
    servidor_holografico.cambiar_estado("Escuchando")
    print("\\n   [Escucha]: Esperando palabra de activación 'Dayan'...")

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

"""
    
    new_lines = lines[:start_idx] + [new_func] + lines[end_idx:]
    
    with open('jarvis.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print('Replaced successfully')
else:
    print('Could not find start/end indices: ', start_idx, end_idx)
