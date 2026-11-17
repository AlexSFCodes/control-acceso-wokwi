"""Detecta rostros en fotos y envia el resultado al Arduino por serial."""

import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
import serial
from PIL import Image, ImageDraw, ImageOps, ImageTk
from serial.tools import list_ports

PUERTO_WOKWI = "rfc2217://localhost:4000"
BAUDIOS = 115200
CARPETA_PROYECTO = Path(__file__).resolve().parent


def enviar_resultado(puerto, hay_rostro):
    if not puerto:
        raise ValueError("Selecciona un puerto COM o el puerto del simulador.")
    esperado = "acceso correcto" if hay_rostro else "acceso denegado"
    opciones = {"baudrate": BAUDIOS, "timeout": 0.4}
    if "://" not in puerto:
        opciones["write_timeout"] = 3
    with serial.serial_for_url(puerto, **opciones) as conexion:
        if "://" not in puerto:
            time.sleep(2)  # El UNO fisico puede reiniciarse al abrir su puerto.
        conexion.reset_input_buffer()
        conexion.write(b"1" if hay_rostro else b"0")
        conexion.flush()
        limite = time.monotonic() + 5
        while time.monotonic() < limite:
            respuesta = conexion.readline().decode("ascii", errors="replace").strip()
            if respuesta == esperado:
                return respuesta
    raise OSError("Arduino no confirmó el resultado. Comprueba el simulador y el puerto.")


class DetectorRostros:
    def __init__(self):
        ruta = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        self.haar = cv2.CascadeClassifier(str(ruta))
        if self.haar.empty():
            raise RuntimeError("No se pudo cargar el clasificador Haar Cascade.")
        modelo = CARPETA_PROYECTO / "modelos" / "face_detection_yunet_2023mar.onnx"
        if not modelo.is_file():
            raise RuntimeError("Falta el modelo de rostros en modelos/. Extrae el proyecto completo.")
        self.yunet = cv2.FaceDetectorYN.create(str(modelo), "", (320, 320), 0.85, 0.3, 5000)

    def detectar(self, foto):
        rgb = np.asarray(foto)
        gris = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        rostros = self.haar.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(rostros):
            return [tuple(map(int, rostro)) for rostro in rostros]

        # YuNet recupera caras grandes o recortadas que Haar puede pasar por alto.
        ancho, alto = foto.size
        for lado in (320, 640):
            escala = lado / max(ancho, alto)
            imagen = cv2.resize(rgb, (max(1, round(ancho * escala)), max(1, round(alto * escala))))
            bgr = cv2.cvtColor(imagen, cv2.COLOR_RGB2BGR)
            self.yunet.setInputSize((bgr.shape[1], bgr.shape[0]))
            _, detecciones = self.yunet.detect(bgr)
            if detecciones is None:
                continue
            cajas = []
            for cara in detecciones:
                x, y, w, h = cara[:4] / escala
                izquierda, arriba = max(0, round(float(x))), max(0, round(float(y)))
                derecha = min(ancho, round(float(x + w)))
                abajo = min(alto, round(float(y + h)))
                if derecha > izquierda and abajo > arriba:
                    cajas.append((izquierda, arriba, derecha - izquierda, abajo - arriba))
            if cajas:
                return cajas
        return []


def cargar_detector():
    return DetectorRostros()


def analizar_imagen(ruta, detector):
    with Image.open(ruta) as archivo:
        foto = ImageOps.exif_transpose(archivo).convert("RGB")
    foto.thumbnail((1280, 1280))
    rostros = detector.detectar(foto)
    return foto, rostros


def main():
    detector = cargar_detector()
    ventana = tk.Tk()
    ventana.title("Control de acceso | Arduino y Wokwi | v2")
    ventana.minsize(700, 620)
    panel = ttk.Frame(ventana, padding=20)
    panel.pack(fill="both", expand=True)
    ttk.Label(panel, text="Control de acceso", font=("Segoe UI", 20, "bold")).pack(anchor="w")
    ttk.Label(panel, text="Carga una foto para detectar si contiene un rostro.").pack(anchor="w", pady=(4, 10))
    ttk.Label(panel, text="Puerto serial: Arduino físico o Wokwi en VS Code").pack(anchor="w")
    puertos = [p.device for p in list_ports.comports()]
    puerto = tk.StringVar(value=PUERTO_WOKWI)
    ttk.Combobox(panel, textvariable=puerto, values=[PUERTO_WOKWI, *puertos], width=48).pack(anchor="w", pady=(4, 4))
    ttk.Label(panel, text="Para encender los LED desde la foto: abre control_acceso.code-workspace y ejecuta Wokwi: Start Simulator.", wraplength=650).pack(anchor="w")
    solo_analizar = tk.BooleanVar(value=False)
    ttk.Checkbutton(panel, text="Solo analizar la foto (sin enviar por serial)", variable=solo_analizar).pack(anchor="w", pady=(8, 0))
    resultado = ttk.Label(panel, font=("Segoe UI", 15, "bold"))
    estado = tk.StringVar(value="Selecciona una foto para comenzar.")
    vista = ttk.Label(panel)
    eventos = queue.Queue()

    def analizar_foto():
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if not ruta:
            return
        try:
            foto, rostros = analizar_imagen(ruta, detector)
        except (OSError, ValueError, cv2.error) as error:
            messagebox.showerror("Error de imagen", str(error))
            return
        hay_rostro = len(rostros) > 0
        dibujo = ImageDraw.Draw(foto)
        for x, y, ancho, alto in rostros:
            dibujo.rectangle((x, y, x + ancho, y + alto), outline="#23a55a", width=4)
        foto.thumbnail((650, 340))
        vista.image = ImageTk.PhotoImage(foto)
        vista.configure(image=vista.image)
        resultado.configure(text="Acceso correcto" if hay_rostro else "Acceso denegado", foreground="#167849" if hay_rostro else "#b52b36")
        if solo_analizar.get():
            estado.set(f"Rostros detectados: {len(rostros)}. No se envió por serial.")
            return
        estado.set(f"Rostros detectados: {len(rostros)}. Esperando confirmación del Arduino...")
        boton.configure(state="disabled")
        # Captura el texto en el hilo de Tk antes de iniciar la comunicación.
        puerto_actual = puerto.get().strip()

        def enviar():
            try:
                eventos.put((True, enviar_resultado(puerto_actual, hay_rostro)))
            except (OSError, ValueError, serial.SerialException) as error:
                eventos.put((False, str(error)))

        threading.Thread(target=enviar, daemon=True).start()

    def revisar_eventos():
        try:
            correcto, mensaje = eventos.get_nowait()
        except queue.Empty:
            pass
        else:
            boton.configure(state="normal")
            if correcto:
                estado.set(f"Arduino confirmó: {mensaje}.")
                print(mensaje, flush=True)
            else:
                if puerto.get().strip().startswith("rfc2217://"):
                    estado.set("Foto analizada. Sin conexión con el Arduino simulado: inicia Wokwi en VS Code.")
                    mensaje += "\n\nAbre control_acceso.code-workspace, pulsa F1 y ejecuta Wokwi: Start Simulator. Mantén el simulador visible. Wokwi en el navegador no habilita este puerto."
                else:
                    estado.set("Foto analizada. El Arduino no confirmó el resultado: comprueba el puerto COM.")
                messagebox.showwarning("Sin confirmación del Arduino", mensaje)
        ventana.after(100, revisar_eventos)

    boton = ttk.Button(panel, text="Cargar y analizar foto", command=analizar_foto)
    boton.pack(anchor="w", pady=(12, 8))
    resultado.pack(anchor="w")
    ttk.Label(panel, textvariable=estado, wraplength=650).pack(anchor="w", pady=(4, 10))
    vista.pack(anchor="w")
    ttk.Label(panel, text="Demostración: detecta presencia de rostros; no identifica personas autorizadas.", wraplength=650).pack(anchor="w", side="bottom", pady=(10, 0))
    revisar_eventos()
    ventana.mainloop()


if __name__ == "__main__":
    main()
