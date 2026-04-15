"""
Script rápido para listar TODOS los juegos en C:\Games y D:\Games
Ignora las capas de cachés de aplicaciones y muestra exactamente qué .exe hay
"""

import os
import sys

def mostrar_juegos():
    rutas_juegos = [r"C:\Games", r"D:\Games"]
    
    total_juegos = 0
    
    for ruta_juego in rutas_juegos:
        if not os.path.exists(ruta_juego):
            print(f"❌ {ruta_juego} no existe\n")
            continue
        
        print(f"\n{'='*70}")
        print(f"📂 JUEGOS EN: {ruta_juego}")
        print(f"{'='*70}\n")
        
        juegos_encontrados = {}
        
        try:
            for raiz, carpetas, archivos in os.walk(ruta_juego):
                # Calcular nivel de profundidad
                nivel = raiz.replace(ruta_juego, '').count(os.sep)
                indent = '  ' * nivel
                carpeta_nombre = os.path.basename(raiz)
                
                # Mostrar carpeta (solo si hay .exe adentro)
                exes_en_carpeta = [a for a in archivos if a.lower().endswith(".exe")]
                if exes_en_carpeta and nivel > 0:
                    print(f"{indent}📁 {carpeta_nombre}/")
                
                # Mostrar ejecutables
                for archivo in sorted(archivos):
                    if archivo.lower().endswith(".exe"):
                        # Ignorar utilidades innecesarias
                        if any(x in archivo.lower() for x in ["unins", "crash", "redist", "setup", "unity", "vcredist", "dotnet", "prereq"]):
                            continue
                        
                        nombre_limpio = archivo.rsplit(".", 1)[0]
                        ruta_completa = os.path.join(raiz, archivo)
                        
                        # Evitar duplicados
                        if nombre_limpio not in juegos_encontrados:
                            juegos_encontrados[nombre_limpio] = ruta_completa
                            print(f"{indent}  ⚙️  {nombre_limpio}")
        
        except Exception as e:
            print(f"❌ Error accediendo a {ruta_juego}: {e}\n")
            continue
        
        # Resumen
        total_juegos += len(juegos_encontrados)
        print(f"\n📊 Total en {ruta_juego}: {len(juegos_encontrados)} juegos\n")
        
        if juegos_encontrados:
            print(f"👉 Nombres EXACTOS para Jarvis (copia-pega):")
            print("-" * 70)
            for nombre in sorted(juegos_encontrados.keys()):
                print(f"     Abre {nombre}")
            print()
    
    print(f"\n{'='*70}")
    print(f"✓ TOTAL ENCONTRADO: {total_juegos} juegos en todas las carpetas")
    print(f"{'='*70}\n")
    
    if total_juegos == 0:
        print("⚠️  No se encontraron juegos. Verifica que C:\\Games contenga las carpetas de tus juegos.\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎮 LISTADO COMPLETO DE JUEGOS LOCALES - JARVIS v9.0")
    print("="*70)
    
    mostrar_juegos()
    
    print("💡 TIP: Usa exactamente estos nombres con Jarvis")
    print("   Ejemplo: 'Abre Cyberpunk2077' o 'Abre P5R'\n")
