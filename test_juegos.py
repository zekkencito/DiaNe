#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificar que solo se detectan juegos INSTALADOS"""

import os

def obtener_juegos_instalados():
    """Clasifica juegos entre Steam y locales INSTALADOS."""
    instalados_steam = []
    instalados_locales = []
    
    rutas_steam = [
        r"C:\Program Files (x86)\Steam\steamapps\common",
        r"D:\SteamLibrary\steamapps\common"
    ]
    rutas_locales = [r"C:\Games", r"D:\Games"]
    carpetas_ignore = ["steamworks shared", "directx", "steam controller configs"]
    
    print("📁 Buscando juegos de Steam instalados...")
    for ruta in rutas_steam:
        if os.path.exists(ruta):
            print(f"   ✓ Encontrada: {ruta}")
            for carpeta in os.listdir(ruta):
                carpeta_path = os.path.join(ruta, carpeta)
                if os.path.isdir(carpeta_path) and carpeta.lower() not in carpetas_ignore:
                    instalados_steam.append(carpeta)
                    print(f"     - {carpeta}")
        else:
            print(f"   ✗ No encontrada: {ruta}")
    
    print("\n🎮 Buscando juegos locales instalados...")
    for ruta in rutas_locales:
        if os.path.exists(ruta):
            print(f"   ✓ Encontrada: {ruta}")
            for carpeta in os.listdir(ruta):
                carpeta_path = os.path.join(ruta, carpeta)
                if os.path.isdir(carpeta_path):
                    instalados_locales.append(carpeta)
                    print(f"     - {carpeta}")
        else:
            print(f"   ✗ No encontrada: {ruta}")
    
    resultado = {
        "steam": ", ".join(instalados_steam) if instalados_steam else "Ninguno",
        "locales": ", ".join(instalados_locales) if instalados_locales else "Ninguno"
    }
    
    print("\n" + "="*60)
    print("📊 RESUMEN:")
    print(f"   Steam instalados: {len(instalados_steam)}")
    print(f"   Locales instalados: {len(instalados_locales)}")
    print(f"   Total: {len(instalados_steam) + len(instalados_locales)}")
    print("="*60)
    
    return resultado

if __name__ == "__main__":
    print("🔍 Verificando juegos INSTALADOS en tu computadora:\n")
    juegos = obtener_juegos_instalados()
    print("\n✅ Resultados finales:")
    print(f"Steam: {juegos['steam']}")
    print(f"Locales: {juegos['locales']}")
