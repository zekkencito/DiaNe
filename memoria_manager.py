import json
import os

MEMORIA_FILE = "memoria_largo_plazo.json"

def init_memoria():
    if not os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, 'w', encoding='utf-8') as f:
                json.dump({"hechos": []}, f, indent=4)
        except Exception as e:
            print(f"[Error] No se pudo inicializar memoria LP: {e}")

def obtener_recuerdos():
    init_memoria()
    try:
        with open(MEMORIA_FILE, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            hechos = datos.get("hechos", [])
            if hechos:
                return "Recuerdos LP:\n- " + "\n- ".join(hechos)
            return ""
    except Exception:
        return ""

def agregar_recuerdo(hecho):
    init_memoria()
    try:
        with open(MEMORIA_FILE, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Evitar duplicados (case-insensitive)
        if any(h.lower() == hecho.lower() for h in datos.get("hechos", [])):
            return False

        datos["hechos"].append(hecho)
        
        with open(MEMORIA_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Error] Fallo al guardar recuerdo LP: {e}")
        return False
