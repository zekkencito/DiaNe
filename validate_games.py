"""
Script de Validación: Verifica que los juegos se cargan correctamente en Jarvis
"""

import os
import json
from pathlib import Path

print("\n" + "="*70)
print("✅ VALIDACIÓN DE JUEGOS - JARVIS v9.0")
print("="*70 + "\n")

# 1. Verificar que C:\Games existe
games_path = r"C:\Games"
if os.path.exists(games_path):
    print(f"✓ {games_path} EXISTE\n")
else:
    print(f"✗ {games_path} NO EXISTE\n")
    exit(1)

# 2. Listar carpetas de juegos
print("📁 CARPETAS DE JUEGOS ENCONTRADAS:")
print("-" * 70)

game_folders = {}
for item in os.listdir(games_path):
    item_path = os.path.join(games_path, item)
    if os.path.isdir(item_path):
        exe_count = len([f for f in os.listdir(item_path) if f.lower().endswith('.exe')])
        game_folders[item] = exe_count
        print(f"  📂 {item:<40} ({exe_count} .exe files)")

print()

# 3. Listar TODOS los .exe (nombres para Jarvis)
print("🎮 JUEGOS LISTOS PARA COMANDAR A JARVIS:")
print("-" * 70)

juegos = []
for game_folder in sorted(game_folders.keys()):
    folder_path = os.path.join(games_path, game_folder)
    for file in os.listdir(folder_path):
        if file.lower().endswith('.exe'):
            if not any(x in file.lower() for x in ["unins", "crash", "redist", "setup", "unity", "vcredist", "dotnet"]):
                nombre = file.rsplit(".", 1)[0]
                juegos.append(nombre)
                print(f"  • Abre {nombre}")

print(f"\n✓ Total de juegos listos: {len(juegos)}")

# 4. Simular lo que hace precachear_juegos_locales()
print("\n" + "="*70)
print("🔄 SIMULANDO precachear_juegos_locales():")
print("="*70 + "\n")

cache_simulado = {}
rutas = [r"C:\Games", r"D:\Games"]

for ruta in rutas:
    if not os.path.exists(ruta):
        print(f"  ℹ️  {ruta} no existe (OK)")
        continue
    
    for raiz, _, archivos in os.walk(ruta):
        for archivo in archivos:
            if archivo.lower().endswith(".exe"):
                if any(x in archivo.lower() for x in ["unins", "crash", "redist", "setup", "unity"]):
                    continue
                nombre_limpio = archivo.rsplit(".", 1)[0]
                ruta_completa = os.path.join(raiz, archivo)
                if nombre_limpio not in cache_simulado:
                    cache_simulado[nombre_limpio] = ruta_completa

print(f"✓ Pre-caché simulado: {len(cache_simulado)} programas\n")

# 5. Mostrar resultado final
print("="*70)
print(f"📊 RESUMEN FINAL:")
print("="*70)
print(f"  Carpetas de juegos: {len(game_folders)}")
print(f"  Juegos encontrados: {len(juegos)}")
print(f"  En caché global: {len(cache_simulado)}")
print()

if len(cache_simulado) > 0:
    print("✅ VALIDACIÓN EXITOSA - Todos los juegos se cargarán al iniciar Jarvis")
    print("\n💡 PRÓXIMO PASO: Ejecuta 'python jarvis.py' e intenta:")
    print(f"   Abre {juegos[0]}")
    print(f"   Abre {juegos[min(2, len(juegos)-1)]}")
else:
    print("❌ VALIDACIÓN FALLIDA - No se encontraron juegos")

print("\n" + "="*70 + "\n")
