import asyncio
import threading
import json
import os

try:
    import websockets
except ImportError:
    websockets = None

# Almacenará los clientes WS conectados
CLIENTES_CONECTADOS = set()
_estado_actual = "Inactivo"

async def manejador_ws(websocket, *args, **kwargs):
    """Maneja cada conexión entrante de WebSockets."""
    CLIENTES_CONECTADOS.add(websocket)
    # Enviar estado actual inmediatamente tras conectar
    try:
        # Mantener conexión viva y procesar mensajes entrantes (Input UI)
        async for msg in websocket:
            try:
                data = json.loads(msg)
                accion = data.get("accion")
                if accion == "teclado":
                    with open("comando_gui.txt", "w", encoding="utf-8") as f:
                        f.write(data["texto"])
                elif accion == "parar_y_escuchar":
                    import pygame
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.music.stop()
                    except Exception:
                        pass
                    with open("forzar_escucha.txt", "w") as f:
                        f.write("1")
                elif accion == "pausar":
                    import pygame
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.music.stop()
                    except Exception:
                        pass
                    with open("dayan_pausado.txt", "w") as f:
                        f.write("1")
                elif accion == "reanudar":
                    try:
                        os.remove("dayan_pausado.txt")
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception:
        pass
    finally:
        CLIENTES_CONECTADOS.remove(websocket)
        # CUANDO SE DESCONECTA EL CLIENTE (cerró navegador) → CIERRA JARVIS
        if not CLIENTES_CONECTADOS:
            print("   [WebSocket] Cliente desconectado - Cerrando Dayan...")
            try:
                with open("desactivar_protocolos.txt", "w") as f:
                    f.write("1")
            except Exception:
                pass

def emitir_estado(nuevo_estado, _loop):
    """Ejecuta el envío a todos los clientes de forma no bloqueante desde el hilo principal."""
    global _estado_actual
    
    if _estado_actual == nuevo_estado:
        return
        
    _estado_actual = nuevo_estado
    
    if not CLIENTES_CONECTADOS:
        return

    async def _emitir_async():
        """Bucle rápido para notificar a clientes."""
        msg = json.dumps({"estado": nuevo_estado})
        tareas = []
        for ws in list(CLIENTES_CONECTADOS):
            tareas.append(asyncio.create_task(ws.send(msg)))
        if tareas:
            await asyncio.gather(*tareas, return_exceptions=True)

    # Inyectar corutina al hilo del WSL
    try:
        asyncio.run_coroutine_threadsafe(_emitir_async(), _loop)
    except Exception as e:
        print(f"   [Error WS Event] {e}")


async def _main():
    print("\n   [Sistema]: Módulo Holográfico activo en ws://0.0.0.0:8765")
    async with websockets.serve(manejador_ws, "0.0.0.0", 8765):
        await asyncio.Future()  # Corre infinitamente

def _iniciar_loop_servidor():
    """Crea un Event Loop específico para el hilo del WebSocket."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Asignamos loop globalmente a una property del módulo para inyecciones
    global async_loop
    async_loop = loop
    
    try:
        loop.run_until_complete(_main())
    except Exception as e:
        print(f"   [Sistema]: Error Servidor WebSockets: {e}")
    finally:
        loop.close()

# Variable global que expondrá el loop creado
async_loop = None

def iniciar_servidor():
    """Inicia el servidor en un Thread paralelo (daemon)."""
    if not websockets:
        print("   [Sistema]: Advertencia - Librería 'websockets' no instalada. El holograma local está deshabilitado.")
        return
    thread = threading.Thread(target=_iniciar_loop_servidor, daemon=True)
    thread.start()

def cambiar_estado(estado):
    """Facade pública para cambiar el estado visual."""
    if websockets and async_loop:
        emitir_estado(estado, async_loop)

def emitir_texto(texto_usuario=None, texto_ia=None):
    """Facade pública para enviar textos renderizados al UI."""
    if not websockets or not async_loop or not CLIENTES_CONECTADOS:
        return
        
    payload = {}
    if texto_usuario: payload["texto_usuario"] = texto_usuario
    if texto_ia: payload["texto_ia"] = texto_ia
    
    if not payload: return
    
    async def _emitir_txt():
        msg = json.dumps(payload)
        tareas = [asyncio.create_task(ws.send(msg)) for ws in list(CLIENTES_CONECTADOS)]
        if tareas:
            await asyncio.gather(*tareas, return_exceptions=True)
            
    try:
        asyncio.run_coroutine_threadsafe(_emitir_txt(), async_loop)
    except Exception:
        pass
