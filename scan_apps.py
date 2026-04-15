"""
Herramienta de Diagnóstico: Escanea todos los programas instalados en el sistema
Útil para verificar si Jarvis puede encontrar tus aplicaciones
"""

import os
import re
import json
import winreg
from pathlib import Path

def limpiar_nombre(nombre):
    """Normaliza el nombre para comparación"""
    return re.sub(r'[^a-z0-9\s]', '', str(nombre).lower())

def buscar_en_program_files():
    """Busca ejecutables en Program Files"""
    aplicaciones = {}
    program_files = [
        os.path.expandvars(r"%ProgramFiles%"),
        os.path.expandvars(r"%ProgramFiles(x86)%")
    ]
    
    print("[*] Escaneando Program Files...")
    
    for pf in program_files:
        if not os.path.exists(pf):
            continue
        
        for raiz, carpetas, archivos in os.walk(pf):
            # Limitar profundidad
            if raiz.count(os.sep) - pf.count(os.sep) > 3:
                del carpetas[:]
                continue
            
            for archivo in archivos:
                if archivo.lower().endswith(".exe"):
                    if any(x in archivo.lower() for x in ["unins", "crash", "redist", "setup", "msi", "vcredist"]):
                        continue
                    
                    nombre_limpio = archivo.rsplit(".", 1)[0]
                    ruta_completa = os.path.join(raiz, archivo)
                    aplicaciones[nombre_limpio] = ruta_completa
    
    return aplicaciones

def buscar_en_registro():
    """Busca programas instalados en el registro de Windows"""
    aplicaciones = {}
    
    print("[*] Escaneando registro de Windows...")
    
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        
        for i in range(winreg.QueryInfoKey(reg_key)[0]):
            try:
                subkey_name = winreg.EnumKey(reg_key, i)
                subkey = winreg.OpenKey(reg_key, subkey_name)
                
                try:
                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    try:
                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                    except:
                        install_location = ""
                    
                    if install_location and os.path.exists(install_location):
                        # Buscar .exe en la carpeta
                        for archivo in os.listdir(install_location):
                            if archivo.lower().endswith(".exe"):
                                ruta = os.path.join(install_location, archivo)
                                aplicaciones[display_name] = ruta
                                break
                except:
                    pass
                
                winreg.CloseKey(subkey)
            except:
                pass
        
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"[!] Error al leer registro: {e}")
    
    return aplicaciones

def buscar_en_accesos():
    """Busca atajos en Start Menu y Desktop"""
    aplicaciones = {}
    
    print("[*] Escaneando accesos directos...")
    
    rutas = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%USERPROFILE%\Desktop"),
        os.path.expandvars(r"%PUBLIC%\Desktop")
    ]
    
    for ruta in rutas:
        if not os.path.exists(ruta):
            continue
        
        for raiz, _, archivos in os.walk(ruta):
            for archivo in archivos:
                if archivo.lower().endswith((".lnk", ".url")):
                    nombre = archivo.rsplit(".", 1)[0]
                    ruta_completa = os.path.join(raiz, archivo)
                    aplicaciones[nombre] = ruta_completa
    
    return aplicaciones

def buscar_en_juegos_locales():
    """Busca juegos en carpetas locales"""
    aplicaciones = {}
    
    print("[*] Escaneando juegos locales en C:\\Games y D:\\Games...")
    
    rutas_juegos = [r"C:\Games", r"D:\Games"]
    
    for ruta_juego in rutas_juegos:
        if not os.path.exists(ruta_juego):
            continue
        
        for raiz, _, archivos in os.walk(ruta_juego):
            for archivo in archivos:
                if archivo.lower().endswith(".exe"):
                    # Ignorar instaladores y utilidades
                    if any(x in archivo.lower() for x in ["unins", "crash", "redist", "setup", "unity"]):
                        continue
                    
                    nombre_limpio = archivo.rsplit(".", 1)[0]
                    ruta_completa = os.path.join(raiz, archivo)
                    aplicaciones[nombre_limpio] = ruta_completa
    
    return aplicaciones

def main():
    print("=" * 70)
    print("🔍 JARVIS - HERRAMIENTA DE DIAGNÓSTICO DE APLICACIONES")
    print("=" * 70)
    print()
    
    todas_las_apps = {}
    
    # Ejecutar búsquedas
    apps_pf = buscar_en_program_files()
    todas_las_apps.update(apps_pf)
    print(f"   ✓ Encontradas {len(apps_pf)} aplicaciones en Program Files")
    
    apps_reg = buscar_en_registro()
    todas_las_apps.update(apps_reg)
    print(f"   ✓ Encontradas {len(apps_reg)} aplicaciones registradas")
    
    apps_acc = buscar_en_accesos()
    todas_las_apps.update(apps_acc)
    print(f"   ✓ Encontrados {len(apps_acc)} accesos directos")
    
    apps_juegos = buscar_en_juegos_locales()
    todas_las_apps.update(apps_juegos)
    print(f"   ✓ Encontrados {len(apps_juegos)} juegos locales")
    
    print()
    print(f"TOTAL: {len(todas_las_apps)} aplicaciones encontradas")
    print()
    
    # Mostrar aplicaciones populares
    print("📌 APLICACIONES POPULARES ENCONTRADAS:")
    print("-" * 70)
    
    popular = ["Visual Studio", "discord", "steam", "spotify", "chrome", "firefox", "notepad", 
               "code", "python", "git", "vlc", "7zip", "audacity", "blender"]
    
    encontradas = []
    for app_nombre, app_ruta in todas_las_apps.items():
        for pop in popular:
            if pop.lower() in app_nombre.lower():
                encontradas.append((app_nombre, app_ruta))
                break
    
    for nombre, ruta in sorted(encontradas):
        print(f"  ✓ {nombre}")
        print(f"    └─ {ruta[:60]}...")
    
    print()
    
    # NUEVO: Mostrar TODOS los juegos locales encontrados
    print("🎮 JUEGOS LOCALES ENCONTRADOS (C:\\Games, D:\\Games):")
    print("-" * 70)
    
    juegos_locales = []
    for app_nombre, app_ruta in todas_las_apps.items():
        if "\\games\\" in app_ruta.lower() or "\\games/" in app_ruta.lower():
            juegos_locales.append((app_nombre, app_ruta))
    
    if juegos_locales:
        for nombre, ruta in sorted(juegos_locales):
            print(f"  ✓ {nombre}")
            print(f"    └─ {ruta}")
    else:
        print("  (No se encontraron juegos locales)")
    
    print()
    
    # Buscar aplicación específica
    while True:
        print("\n🔎 BUSCAR APLICACIÓN ESPECÍFICA:")
        buscar = input("  Escribe parte del nombre (o 'salir'): ").strip()
        
        if buscar.lower() == "salir":
            break
        
        if not buscar:
            continue
        
        buscar_limpio = limpiar_nombre(buscar)
        resultados = []
        
        for app_nombre, app_ruta in todas_las_apps.items():
            if buscar_limpio in limpiar_nombre(app_nombre):
                resultados.append((app_nombre, app_ruta))
        
        if resultados:
            print(f"\n  Encontradas {len(resultados)} coincidencias:")
            for nombre, ruta in sorted(resultados)[:10]:
                print(f"    • {nombre}")
                print(f"      {ruta}")
        else:
            print(f"\n  ✗ No se encontraron coincidencias para '{buscar}'")
    
    # Guardar en JSON
    print("\n💾 Guardando resultados en 'apps_log.json'...")
    with open("apps_log.json", "w", encoding="utf-8") as f:
        json.dump(todas_las_apps, f, ensure_ascii=False, indent=2)
    
    print("✓ Hecho. Usa 'apps_log.json' como referencia de nombres exactos.")
    print("=" * 70)

if __name__ == "__main__":
    main()
