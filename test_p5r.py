#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validar que P5R existe y puede ejecutarse"""

import os
import subprocess
import json

# Cargar caché
cache_file = "cache_programas.json"
if os.path.exists(cache_file):
    with open(cache_file, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

print("🔍 Buscando P5R en caché y sistema...\n")

# Buscar en caché
p5r_path = None
for nombre, ruta in cache.items():
    if "p5r" in nombre.lower() or "persona 5" in nombre.lower():
        print(f"✓ Encontrado en caché: {nombre}")
        print(f"  Ruta: {ruta}")
        p5r_path = ruta
        break

if not p5r_path:
    print("✗ No encontrado en caché")
    print("  Searching in C:\\Games...")
    
    for root, dirs, files in os.walk(r"C:\Games"):
        for file in files:
            if file.lower() == "p5r.exe":
                p5r_path = os.path.join(root, file)
                print(f"✓ Encontrado en: {p5r_path}")
                break

if p5r_path:
    print("\n📋 Validación del ejecutable:")
    print(f"  Existe: {os.path.exists(p5r_path)} ✓")
    print(f"  Es ejecutable: {os.path.isfile(p5r_path)} ✓")
    print(f"  Tamaño: {os.path.getsize(p5r_path) / (1024*1024):.2f} MB")
    print(f"  Ruta completa: {os.path.abspath(p5r_path)}")
    
    print("\n🚀 Intentando lanzar...")
    try:
        # Usar Popen sin esperar (como Jarvis lo hace)
        proceso = subprocess.Popen(p5r_path)
        print(f"✓ Proceso lanzado con PID: {proceso.pid}")
        print("  Esperando 3 segundos para ver si se mantiene abierto...")
        
        import time
        time.sleep(3)
        
        if proceso.poll() is None:
            print("✓ P5R sigue ejecutándose ✅")
        else:
            exit_code = proceso.returncode
            print(f"✗ P5R se cerró inmediatamente (código: {exit_code}) ❌")
            print("\n  Posibles razones:")
            print("  • Falta de archivos o dependencias")
            print("  • Requiere antivirus desactivado")
            print("  • Necesita estar en carpeta específica")
            print("  • Falta de permisos de administered")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("\n✗ P5R no encontrado en el sistema")
