# -*- coding: utf-8 -*-
import os
import sys
import io
import socket
import http.server
import socketserver
import qrcode
import json
import urllib.request
import urllib.error
import base64

# Forzar codificación UTF-8 en flujos estándar de consola para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PORT = 8000

def get_local_ip():
    """
    Detecta la dirección IP local de la computadora conectada a la red Wi-Fi
    de forma dinámica, descartando la dirección loopback 127.0.0.1.
    """
    try:
        # Crea un socket UDP temporal para verificar la interfaz de red activa
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Nos conectamos a un host externo (no envía tráfico de datos real)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        if not local_ip.startswith("127."):
            return local_ip
    except Exception:
        pass

    # Fallback si no hay conexión a internet / externa
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                return ip
    except Exception:
        pass

    return "127.0.0.1"

yolo_model = None

def query_yolo_and_ollama(base64_image_data):
    """
    Procesa un fotograma en Base64 de forma 100% local ejecutando YOLOv8
    en la computadora del usuario y alimentando las etiquetas detectadas
    a Ollama local (qwen) para armar una respuesta didáctica divertida.
    """
    global yolo_model
    
    # Lazy loading para evitar que falle el servidor si ultralytics sigue instalándose
    try:
        from ultralytics import YOLO
    except ImportError:
        return "¡Procesador de visión instalándose! La librería 'ultralytics' (YOLOv8) se está configurando en segundo plano en tu PC. Por favor, espera un minuto e inténtalo de nuevo. 🐳⏳"

    if yolo_model is None:
        if os.path.exists("yolov8_docker_custom.pt"):
            print("[YOLO LOCAL] Inicializando Modelo Personalizado (yolov8_docker_custom.pt) en memoria...")
            yolo_model = YOLO("yolov8_docker_custom.pt")
        else:
            print("[YOLO LOCAL] Inicializando YOLOv8 Nano por defecto en memoria...")
            yolo_model = YOLO("yolov8n.pt")
        print("[YOLO LOCAL] Modelo YOLOv8 inicializado con éxito.")

    # 1. Decodificar la imagen Base64 y guardarla temporalmente
    if "," in base64_image_data:
        base64_image_data = base64_image_data.split(",")[1]
    
    # Asegurar que tenga el relleno (padding) correcto para evitar binascii.Error
    missing_padding = len(base64_image_data) % 4
    if missing_padding:
        base64_image_data += '=' * (4 - missing_padding)
    
    img_data = base64.b64decode(base64_image_data)
    temp_path = "temp_capture.jpg"
    with open(temp_path, "wb") as f:
        f.write(img_data)
        
    detecciones = []
    try:
        # 2. Correr inferencia local con YOLOv8
        results = yolo_model(temp_path, verbose=False)
        
        # 3. Filtrar detecciones con confianza > 50%
        for box in results[0].boxes:
            conf = float(box.conf[0])
            if conf >= 0.50:
                cls_id = int(box.cls[0])
                label = results[0].names[cls_id]
                detecciones.append(f"{label} ({int(conf * 100)}% de confianza)")
    except Exception as e:
        print(f"[YOLO LOCAL] Falla en la inferencia de la imagen: {str(e)}")
    finally:
        # Garantizar limpieza del archivo temporal
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        
    # 4. Crear el Prompt dinámico para Ollama
    if not detecciones:
        prompt_ollama = (
            "Eres Moby, la ballena mascota oficial de Docker. El sensor de mi cámara no detectó ningún objeto "
            "claro en el entorno inmediato. Genera una respuesta alegre de 2 oraciones en español saludando al usuario "
            "e invitándolo a colocar una laptop, teclado, ratón o taza de café frente a la cámara para analizarlos "
            "y explicar su relación con contenedores."
        )
    else:
        objetos_detectados = ", ".join(detecciones)
        print(f"[YOLO LOCAL] Radar detectó en el entorno real: {objetos_detectados}")
        
        prompt_ollama = (
            f"Eres Moby, la ballena mascota oficial de Docker. Responde de manera alegre, didáctica y en máximo "
            f"2 oraciones en español. El sensor de mi cámara acaba de escanear mi entorno real y detectó "
            f"los siguientes objetos físicos: {objetos_detectados}. "
            f"Describe brevemente qué objetos viste y haz una analogía didáctica y divertida de cómo se relacionan "
            f"con Docker (por ejemplo, que la laptop representa portabilidad, que la taza de café es un volumen persistente, "
            f"que el teclado es para escribir Dockerfiles o que el mouse ayuda a orquestar contenedores)."
        )
        
    # 5. Consultar a tu Ollama local (qwen)
    try:
        url_ollama = "http://localhost:11434/api/generate"
        payload = {
            "model": "qwen",
            "prompt": prompt_ollama,
            "stream": False
        }
        
        req = urllib.request.Request(
            url_ollama,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("response", "¡Ups! No pude procesar los datos de mi radar.")
            
    except Exception as e:
        print(f"[OLLAMA ERROR] Error al conectar al servicio local Ollama: {str(e)}")
        # Fallback elegante si Ollama está caído
        if detecciones:
            return (
                f"¡Hola! Mi sonar local detectó: {', '.join(detecciones)}. "
                "Lamentablemente no pude conectar con mi cerebro de Ollama en el puerto 11434, "
                "¡pero sé que esos objetos son claves para tu estación de trabajo Docker! 🐳🔌"
            )
        else:
            return "¡Sonar activo! No detecté objetos claros, pero asegúrate de tener Ollama activo en el puerto 11434 para que pueda hablar contigo sobre tu entorno. 🐳📡"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/vision':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # 1. Leer JSON del cliente
                data = json.loads(post_data.decode('utf-8'))
                image_base64 = data.get("image")
                
                if not image_base64:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response_body = json.dumps({"error": "Falta la imagen para analizar."})
                    self.wfile.write(response_body.encode('utf-8'))
                    return

                # 2. Ejecutar Inferencia de YOLOv8 local + Ollama local
                print("[VISION LOCAL] Procesando fotograma mediante YOLOv8 + Ollama...")
                analisis = query_yolo_and_ollama(image_base64)
                print("[VISION LOCAL] Análisis de radar completado con éxito.")

                # 3. Enviar Respuesta
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"response": analisis})
                self.wfile.write(response_body.encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla en el procesamiento de visión: {str(e)}"})
                self.wfile.write(response_body.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def end_headers(self):
        # Deshabilitar caché y habilitar CORS para pruebas AR/WebXR en celulares
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    # Asegurar que el directorio de trabajo es la raíz del servicio
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    # 1. Detectar IP Local o usar URL personalizada pasada por argumento
    ip_detectada = get_local_ip()
    if len(sys.argv) > 1:
        url_servicio = sys.argv[1]
        print("=" * 80)
        print("[DESPLIEGUE] INICIANDO LANZADOR WEBXR AR DOCKER")
        print(f"URL de destino personalizada (Cloudflare/Pública): {url_servicio}")
    else:
        url_servicio = f"http://{ip_detectada}:{PORT}"
        print("=" * 80)
        print("[DESPLIEGUE] INICIANDO LANZADOR WEBXR AR DOCKER")
        print(f"Dirección IP local detectada: {ip_detectada}")
        print(f"URL de destino por defecto: {url_servicio}")
    print("-" * 80)

    # 2. Generar Código QR
    try:
        print("Generando código QR de presentación...")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url_servicio)
        qr.make(fit=True)

        # Crear y guardar la imagen
        img = qr.make_image(fill_color="black", back_color="white")
        ruta_qr = os.path.abspath("qr_presentacion.png")
        img.save(ruta_qr)
        
        print("[OK] Código QR generado y guardado exitosamente.")
        print(f"Ruta física del QR: {ruta_qr}")
        print("-" * 80)
    except Exception as e:
        print(f"[ERROR] No se pudo generar el código QR: {str(e)}", file=sys.stderr)
        # Continuar con el servidor de todos modos
        pass

    # 3. Lanzar Servidor HTTP
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        print(f"Iniciando servidor HTTP en puerto {PORT}...")
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("=" * 80)
            print("[OK] SERVIDOR WEBXR AR CORRIENDO CORRECTAMENTE")
            print("Acceso Local (PC):")
            print(f"   -> http://localhost:{PORT}")
            print("-" * 80)
            print("Acceso Móvil (Celular):")
            print(f"   -> {url_servicio}")
            print("-" * 80)
            print("ESCANEE EL ARCHIVO 'qr_presentacion.png' CON SU CELULAR PARA INGRESAR")
            print("=" * 80)
            print("Presione Ctrl+C para detener el servidor de despliegue.")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR CRÍTICO] No se pudo iniciar el servidor web: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
