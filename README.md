# 🤖 JARVIS v9.0 - Asistente de Voz + GUI Chat

## Características Nuevas

### 1️⃣ Memoria Expandida
- **Historial Completo**: Carga todos los mensajes de la sesión (no solo últimos 4)
- **Perfil Persistente** (`perfil_usuario.json`):
  - Comandos favoritos tracking
  - Aplicaciones frecuentes
  - Búsquedas recientes
  - Preferencias de voz/modelo
  - Archivos abiertos recientemente

### 2️⃣ Interfaz Gráfica (GUI)
- **Chat en Tiempo Real**: Visualiza historial de conversación
- **Input de Texto**: Escribe comandos mientras el micrófono escucha
- **Panel de Perfil**: Ver información de usuario y comandos favoritos
- **Control de Voz**: Botón ON/OFF para micrófono
- **Guardado de Sesiones**: Exporta logs de conversación

### 3️⃣ Dual Input
- **Voz**: Continúa funcionando normalmente vía micrófono
- **Texto**: Comandos desde la GUI tienen prioridad
- **Paralelo**: Ambos funcionan simultáneamente sin conflicto

### 4️⃣ Búsqueda Mejorada de Programas (NEW!)
- **Caché**: Búsqueda instantánea de programas conocidos
- **Program Files**: Escanea C:\Program Files y C:\Program Files (x86)
- **Registro de Windows**: Lee aplicaciones instaladas desde el registro
- **Accesos Directos**: Start Menu + Desktop
- **Juegos Locales**: C:\Games + D:\Games
- **Diagnóstico**: Nueva herramienta `scan_apps.py` para verificar qué programas encuentra Jarvis

---

## Instalación

### Dependencias Adicionales
```bash
pip install tkinter  # Generalmente incluido con Python
```

### Ya instaladas:
- `requests`, `speech_recognition`, `edge_tts`, `pygame`, `pyautogui`

---

## Uso

### Opción 1: Launcher Automático (Recomendado)
```bash
python launcher.py
```
- Abre automáticamente GUI + inicia Jarvis en background

### Opción 2: Solo CLI (Modo Original)
```bash
python jarvis.py
```
- Funciona con voz como antes, sin GUI

### Opción 3: Solo GUI (Sin Voz)
```bash
python jarvis_gui.py
```
- Interface gráfica solamente (para debugging)

### Opción 4: Diagnosticar Programas Instalados
```bash
python scan_apps.py
```
- Escanea TODO tu sistema y muestra qué aplicaciones puede encontrar Jarvis
- Permite buscar manualmente
- Genera `apps_log.json` con el mapa completo

### Opción 5: Listar TODOS los Juegos Locales (C:\Games, D:\Games)
```bash
python list_games.py
```
- Muestra una lista completa con la estructura de carpetas
- Muestra exactamente qué nombres usar para "Abre [juego]"
- Útil para verificar si un juego está disponible

---

## Estructura de Archivos

```
┌─ jarvis.py                 # Motor principal (voz + IA)
├─ jarvis_gui.py            # Interfaz gráfica
├─ launcher.py              # Script coordinador
├─ scan_apps.py             # Herramienta de diagnóstico ⭐ NUEVO
│
├─ cache_programas.json     # Cache de búsquedas
├─ perfil_usuario.json      # Perfil persistente ⭐ NUEVO
├─ historial_YYYYMMDD.json  # Conversaciones diarias (completo)
├─ apps_log.json            # Aplicaciones encontradas (por scan_apps.py)
├─ jarvis.log               # Log de eventos
│
└─ Archivos temporales:
   ├─ comando_gui.txt       # Comandos desde GUI
   ├─ voz_estado.txt        # Estado micrófono
   └─ respuesta.mp3         # Audio temporal
```

---

## Flujo de Datos

```
┌─────────────────────────────────────────────────────┐
│              JARVIS v9.0 ARQUITECTURA               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  GUI (jarvis_gui.py)                               │
│  ├── Chat Display                                   │
│  ├── Text Input ──→[comando_gui.txt]               │
│  ├── Perfil Panel ←──[perfil_usuario.json]        │
│  └── Voice Toggle                                  │
│         │                                           │
│         ↓                                           │
│  JARVIS CORE (jarvis.py)                          │
│  ├── leer_comando_gui() ◄─── (prioridad alta)     │
│  ├── escuchar() ◄─────────── (spellcheck vía mic) │
│  ├── pensar() ──→ Ollama/Mistral                   │
│  │   └─ Context: historial completo + perfil     │
│  ├── ejecutar()                                    │
│  │   └─ buscar_programa() (5 fuentes)             │
│  └── hablar_async() ──→ Edge TTS                   │
│         │                                           │
│         ↓                                           │
│  BÚSQUEDA MEJORADA (NEW!)                         │
│  1. Caché (instantáneo)                            │
│  2. Program Files (ejecutables reales)             │
│  3. Registro Windows (aplicaciones instaladas)     │
│  4. Accesos directos (Start Menu + Desktop)        │
│  5. Juegos locales (C:\Games, D:\Games)            │
│         │                                           │
│         ↓                                           │
│  MEMORIA PERSISTENTE                              │
│  ├── historial_YYYYMMDD.json (completo)           │
│  ├── perfil_usuario.json (usuario tracking)       │
│  └── cache_programas.json (búsquedas)             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Comandos Especiales

### Control de Voz
- **"desactiva el modo"** → Desactiva Gaming Mode
- **"activa el modo"** → Activa Gaming Mode
- **"desactivar protocolos de jarvis"** → Apaga Jarvis

### Desde GUI
- **Botón 🎙 Voz**: ON/OFF micrófono
- **Botón ✉️ ENVIAR**: Ejecuta comando escrito
- **Botón 🗑️ LIMPIAR**: Limpia historial visual
- **Botón 💾 GUARDAR**: Exporta sesión actual

### Shortcuts (Directos, sin IA)
- `"apaga"` → Cierra ventana
- `"música"` → Reproduce música aleatoria
- `"música [canción]"` → Abre YouTube
- `"play"` → Reproduce en YouTube

---

## Búsqueda de Programas - Cómo Funciona

Cuando dices "Abre Visual Studio Code", Jarvis busca en este orden:

1. **Caché** (~1ms): ¿Ya lo busqué antes?
2. **Program Files** (~1s): Busca .exe en C:\Program Files
3. **Registro Windows** (~2s): Lee "Software\Microsoft\Windows\CurrentVersion\Uninstall"
4. **Accesos** (~500ms): Busca .lnk en Start Menu y Desktop
5. **Juegos** (~500ms): Busca en C:\Games y D:\Games

Si **NO lo encuentra**, Jarvis te dirá y sugerirá verificar la instalación.

---

## Herramienta de Diagnóstico

Si Jarvis no encuentra un programa que sabes que está instalado, usa:

```bash
python scan_apps.py
```

**Ejemplo:**
```
🔍 JARVIS - HERRAMIENTA DE DIAGNÓSTICO DE APLICACIONES

[*] Escaneando Program Files...
   ✓ Encontradas 156 aplicaciones en Program Files
[*] Escaneando registro de Windows...
   ✓ Encontradas 89 aplicaciones registradas
[*] Escaneando accesos directos...
   ✓ Encontrados 42 accesos directos

TOTAL: 287 aplicaciones encontradas

📌 APLICACIONES POPULARES ENCONTRADAS:
  ✓ Visual Studio Code
    └─ C:\Program Files\Microsoft VS Code\Code.exe
  ✓ Discord
    └─ C:\Users\...\AppData\Local\Discord\Update.exe
  ✓ Steam
    └─ C:\Program Files (x86)\Steam\Steam.exe

🔎 BUSCAR APLICACIÓN ESPECÍFICA:
  Escribe parte del nombre (o 'salir'): antigravity
  
  Encontradas 1 coincidencias:
    • AntiGravity Game
      C:\Games\AntiGravity\AntiGravity.exe
```

---

## Información de Perfil Usuario

El archivo `perfil_usuario.json` contiene:

```json
{
  "creado": "2026-03-31T10:30:00",
  "última_sesión": "2026-03-31T14:45:00",
  "comandos_favoritos": [
    "abrir:visual studio code",
    "reproducir:lofi beats",
    "buscar:python tutorial"
  ],
  "aplicaciones_frecuentes": {
    "Code": 25,
    "Discord": 18
  },
  "búsquedas_frecuentes": ["python", "javascript"],
  "horarios_de_uso": {
    "14": 12,
    "15": 8
  },
  "preferencias": {
    "voz": "es-MX-JorgeNeural",
    "modelo": "mistral",
    "gamificación": true
  },
  "archivos_recientes": ["proyecto.py", "readme.md"]
}
```

---

## Historial Expandido

Ahora Jarvis accede al historial **COMPLETO** del día (no solo últimos 4 mensajes):

```python
# ANTES (v8.0):
memoria_texto = "\n".join([f"{msg['rol']}: {msg['texto']}" for msg in historial[-4:]])

# AHORA (v9.0):
memoria_texto = "\n".join([f"{msg['rol']}: {msg['texto']}" for msg in historial[-30:]])
# + contexto del perfil usuario
# + archivos recientes del sistema
```

Esto permite:
✅ Mejor contexto conversacional
✅ Recordar preferencias anteriores
✅ Detectar patrones de uso
✅ Respuestas más personalizadas

---

## Troubleshooting

### "No encontré 'X' programa"

**Paso 1**: Verifica que esté instalado
```bash
# Escanear todos los programas del sistema
python scan_apps.py
```

**Paso 2**: Busca en los resultados

**Paso 3**: Si lo ves en `scan_apps.py` pero Jarvis no lo encuentra:
- El nombre podría ser diferente (ej: "Code" vs "Visual Studio Code")
- Podría no tener acceso de búsqueda ese archivo
- Podría estar en una ruta no estándar

**Paso 4**: Abre manualmente una vez (se cachea automáticamente después)

### GUI no aparece
```bash
# Verificar Tkinter
python -c "import tkinter; print('OK')"

# En Ubuntu/Debian:
sudo apt-get install python3-tk
```

### Micrófono no funciona en GUI+Voz paralelo
- Algunos drivers no permiten acceso simultáneo
- Solución: Usar solo texto mientras se recopila audio

### Comando del GUI no se procesa
- Verificar que `comando_gui.txt` se crea
- Revisar permisos de lectura/escritura

### Perfil no se guarda
```bash
# Limpiar archivo corrupto
rm perfil_usuario.json
# Reiniciar Jarvis (lo recreará)
```

---

## Performance Tips

| Acción | Efecto |
|--------|--------|
| **Usar Mistral** | 2-3x más rápido que Qwen2.5 |
| **Activar Gaming Mode** | Libera VRAM, respuestas ultra-rápidas |
| **Chat en GUI** | No bloquea micrófono |
| **Historial completo** | +500ms en respuesta (pero mejor contexto) |
| **Scan_apps primera vez** | ~5s (después se cachea) |

---

## Próximas Mejoras

- [ ] Sincronización de sesiones entre dispositivos
- [ ] Voice commands desde el panel de favoritos
- [ ] Análisis de patrones de uso diario
- [ ] Integración con calendario/recordatorios
- [ ] Modo colaborativo (múltiples usuarios)
- [ ] Exportación de datos de sesión
- [ ] Pre-cacheo de aplicaciones comunes
- [ ] Fuzzy matching para nombres aproximados

---

**Versión**: 9.0
**Última actualización**: 31-03-2026
**Modo**: Dual Input (Voz + Texto)
**Búsqueda de Programas**: 5 Fuentes + Diagnóstico
