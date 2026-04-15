import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import os
import threading
import queue
from datetime import datetime
import subprocess
import sys

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis - Chat Interface v1.0")
        self.root.geometry("1000x650")
        self.root.configure(bg="#1a1a2e")
        
        # Queue para comunicación entre threads
        self.mensaje_queue = queue.Queue()
        self.proceso_jarvis = None
        self.escuchando = False
        
        # Estilos
        self.setup_estilos()
        
        # Frame superior con info
        self.crear_header()
        
        # Frame central: chat + información
        self.crear_chat_area()
        
        # Frame inferior: input panel
        self.crear_input_panel()
        
        # Sincronización con jarvis.py ejecutándose
        self.monitorear_archivos()
        
    def setup_estilos(self):
        """Configura estilos visuales"""
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure("TButton", font=("Courier", 9))
        estilo.configure("TLabel", background="#1a1a2e", foreground="#00ff88")
        
    def crear_header(self):
        """Crea barra superior con estado"""
        header = tk.Frame(self.root, bg="#0f3460", height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(header, text="🤖 JARVIS v9.0 - Chat Interface", 
                         font=("Courier", 14, "bold"), 
                         bg="#0f3460", fg="#00ff88")
        titulo.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.estado_label = tk.Label(header, text="⚫ Escuchando...", 
                                    font=("Courier", 10), 
                                    bg="#0f3460", fg="#ffaa00")
        self.estado_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.voz_toggle = tk.Button(header, text="🎙 Voz ON", 
                                   command=self.toggle_voz,
                                   bg="#16a085", fg="white", 
                                   font=("Courier", 9, "bold"),
                                   relief=tk.FLAT, padx=10, pady=5)
        self.voz_toggle.pack(side=tk.RIGHT, padx=5, pady=10)
        
    def crear_chat_area(self):
        """Crea área de chat y panel lateral"""
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat
        chat_frame = tk.Frame(main_frame, bg="#0a0a14")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        
        tk.Label(chat_frame, text="HISTORIAL:", font=("Courier", 9, "bold"),
                bg="#0a0a14", fg="#00ff88").pack(anchor=tk.W)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            bg="#0a0a14", fg="#00ff88", font=("Courier", 9),
            wrap=tk.WORD, height=20, width=60
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Panel lateral: Perfil + Acciones
        lado_frame = tk.Frame(main_frame, bg="#0f3460", width=250)
        lado_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        lado_frame.pack_propagate(False)
        
        # Perfil
        tk.Label(lado_frame, text="👤 PERFIL", font=("Courier", 10, "bold"),
                bg="#0f3460", fg="#00ff88").pack(anchor=tk.W, padx=10, pady=(10,5))
        
        self.perfil_text = scrolledtext.ScrolledText(
            lado_frame, bg="#000", fg="#00ff88", 
            font=("Courier", 7), height=8, width=30
        )
        self.perfil_text.pack(fill=tk.X, padx=10, pady=5)
        self.perfil_text.config(state=tk.DISABLED)
        
        # Comandos frecuentes
        tk.Label(lado_frame, text="⭐ FAVORITOS", font=("Courier", 10, "bold"),
                bg="#0f3460", fg="#ffaa00").pack(anchor=tk.W, padx=10, pady=(10,5))
        
        self.favoritos_frame = tk.Frame(lado_frame, bg="#0f3460")
        self.favoritos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Estado del sistema
        tk.Label(lado_frame, text="🖥️ SISTEMA", font=("Courier", 10, "bold"),
                bg="#0f3460", fg="#aa00ff").pack(anchor=tk.W, padx=10, pady=(10,5))
        
        self.sistema_text = scrolledtext.ScrolledText(
            lado_frame, bg="#000", fg="#aa00ff", 
            font=("Courier", 7), height=6, width=30
        )
        self.sistema_text.pack(fill=tk.X, padx=10, pady=5)
        self.sistema_text.config(state=tk.DISABLED)
        
    def crear_input_panel(self):
        """Crea panel inferior para escribir comandos"""
        input_frame = tk.Frame(self.root, bg="#0f3460", height=100)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        input_frame.pack_propagate(False)
        
        tk.Label(input_frame, text="📝 ESCRIBE TU COMANDO:", 
                font=("Courier", 9, "bold"),
                bg="#0f3460", fg="#00ff88").pack(anchor=tk.W, pady=(5,0))
        
        # Input field
        self.input_field = tk.Entry(input_frame, font=("Courier", 11),
                                   bg="#1a1a2e", fg="#00ff88", 
                                   insertbackground="#00ff88",
                                   relief=tk.FLAT, bd=2)
        self.input_field.pack(fill=tk.X, pady=5, ipady=8)
        self.input_field.bind("<Return>", self.enviar_comando)
        self.input_field.focus()
        
        # Botones
        botones_frame = tk.Frame(input_frame, bg="#0f3460")
        botones_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(botones_frame, text="✉️  ENVIAR", command=self.enviar_comando,
                 bg="#16a085", fg="white", font=("Courier", 10, "bold"),
                 relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(botones_frame, text="🗑️  LIMPIAR", command=self.limpiar_chat,
                 bg="#c0392b", fg="white", font=("Courier", 10, "bold"),
                 relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(botones_frame, text="💾 GUARDAR SESIÓN", command=self.guardar_sesion,
                 bg="#8e44ad", fg="white", font=("Courier", 10, "bold"),
                 relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
    def enviar_comando(self, event=None):
        """Envía comando a jarvis.py"""
        comando = self.input_field.get().strip()
        if not comando:
            return
        
        # Mostrar en chat
        self.agregar_mensaje_chat("👤 Tú", comando, "#00ff88")
        self.input_field.delete(0, tk.END)
        
        # Escribir a archivo que jarvis.py monitorea
        try:
            with open("comando_gui.txt", "w", encoding="utf-8") as f:
                f.write(comando)
            self.agregar_mensaje_chat("🤖 Jarvis", "Procesando tu comando...", "#ffaa00")
        except Exception as e:
            self.agregar_mensaje_chat("❌ Error", f"No se pudo enviar: {e}", "#ff0000")
    
    def agregar_mensaje_chat(self, sender, mensaje, color):
        """Agrega mensaje al chat"""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        linea = f"[{timestamp}] {sender}: {mensaje}\n"
        self.chat_display.insert(tk.END, linea, color)
        self.chat_display.tag_config(color, foreground=color)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def monitorear_archivos(self):
        """Monitorea cambios en archivos de Jarvis"""
        try:
            # Cargar perfil
            if os.path.exists("perfil_usuario.json"):
                with open("perfil_usuario.json", "r", encoding="utf-8") as f:
                    perfil = json.load(f)
                    self.actualizar_perfil_panel(perfil)
            
            # Cargar historial
            archivo_historial = f"historial_{datetime.now().strftime('%Y%m%d')}.json"
            if os.path.exists(archivo_historial):
                with open(archivo_historial, "r", encoding="utf-8") as f:
                    historial = json.load(f)
                    self.actualizar_chat_desde_historial(historial)
            
            # Monitorear log para actualizaciones en tiempo real
            with open("jarvis.log", "r", encoding="utf-8") as f:
                lineas = f.readlines()
                for linea in lineas[-5:]:
                    if "CONVERSA" in linea:
                        self.agregar_mensaje_chat("🤖 Jarvis", "...", "#00ff88")
        except Exception as e:
            pass
        
        # Reintentar cada 2 segundos
        self.root.after(2000, self.monitorear_archivos)
    
    def actualizar_perfil_panel(self, perfil):
        """Actualiza panel de perfil"""
        self.perfil_text.config(state=tk.NORMAL)
        self.perfil_text.delete(1.0, tk.END)
        
        info = f"""Última sesión: {perfil.get('última_sesión', 'N/A')[:10]}
Modelo: {perfil.get('preferencias', {}).get('modelo', 'mistral')}
Voz: {perfil.get('preferencias', {}).get('voz', 'es-MX-JorgeNeural').split('-')[-1]}

Comandos totales: {len(perfil.get('comandos_favoritos', []))}
"""
        self.perfil_text.insert(1.0, info)
        self.perfil_text.config(state=tk.DISABLED)
        
        # Actualizar favoritos
        self.favoritos_frame.destroy()
        self.favoritos_frame = tk.Frame(self.root.winfo_children()[1].winfo_children()[1], bg="#0f3460")
        self.favoritos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for cmd in perfil.get("comandos_favoritos", [])[:3]:
            btn = tk.Button(self.favoritos_frame, text=f"► {cmd[:20]}...",
                           font=("Courier", 7), bg="#16a085", fg="white",
                           relief=tk.FLAT, pady=2)
            btn.pack(fill=tk.X, pady=2)
    
    def actualizar_chat_desde_historial(self, historial):
        """Carga historial en el chat"""
        self.chat_display.config(state=tk.NORMAL)
        for msg in historial[-10:]:
            rol = msg.get("rol", "")
            texto = msg.get("texto", "")
            color = "#00ff88" if rol == "Usuario" else "#ffaa00"
            emoji = "👤" if rol == "Usuario" else "🤖"
            self.agregar_mensaje_chat(emoji + " " + rol, texto, color)
    
    def toggle_voz(self):
        """Activa/desactiva micrófono"""
        self.escuchando = not self.escuchando
        estado = "ON" if self.escuchando else "OFF"
        color = "#16a085" if self.escuchando else "#c0392b"
        self.voz_toggle.config(text=f"🎙 Voz {estado}", bg=color)
        
        # Escribir estado para que jarvis.py lo detecte
        with open("voz_estado.txt", "w") as f:
            f.write(str(self.escuchando))
    
    def limpiar_chat(self):
        """Limpia el historial visual"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def guardar_sesion(self):
        """Guarda la sesión actual"""
        try:
            archivo_sesion = f"sesion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            contenido = self.chat_display.get(1.0, tk.END)
            with open(archivo_sesion, "w", encoding="utf-8") as f:
                f.write(contenido)
            self.agregar_mensaje_chat("💾 Sistema", f"Sesión guardada: {archivo_sesion}", "#8e44ad")
        except Exception as e:
            self.agregar_mensaje_chat("❌ Error", f"No se pudo guardar: {e}", "#ff0000")

if __name__ == "__main__":
    root = tk.Tk()
    gui = JarvisGUI(root)
    root.mainloop()
