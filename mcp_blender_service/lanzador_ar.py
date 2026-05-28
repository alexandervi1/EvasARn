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

def query_gemini_vision(api_key, base64_image_data):
    """
    Realiza una consulta a la API de Google Gemini 1.5 Flash utilizando el feed
    base64 de la cámara, sin requerir la librería externa google-generativeai.
    """
    if "," in base64_image_data:
        base64_image_data = base64_image_data.split(",")[1]
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {
                    "text": (
                        "Actúa como Moby, la ballena mascota oficial de Docker. Responde de manera alegre, "
                        "didáctica y en máximo 3 oraciones en español nativo. "
                        "Analiza la siguiente imagen de la cámara del usuario. Si ves la interfaz de Docker Desktop "
                        "o alguna terminal con comandos de Docker, identifica los contenedores, imágenes, "
                        "volúmenes o procesos, explicando brevemente qué son y cuál es su estado (verde/activo, gris/inactivo). "
                        "Si ves objetos del mundo real (como una computadora, laptop, teclado, ratón, taza, etc.), "
                        "identifícalos e invéntate una analogía divertida sobre cómo se relacionan con Docker (por ejemplo, "
                        "que la taza de café es un volumen persistente que mantiene activo el cerebro del desarrollador)."
                    )
                },
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": base64_image_data
                    }
                }
            ]
        }]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return text
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        print(f"[ERROR DE VISION] HTTP Error: {error_msg}")
        raise Exception(f"Falla de API de Gemini: {e.code} - {e.reason}")
    except Exception as e:
        print(f"[ERROR DE VISION] Falla general: {str(e)}")
        raise e

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
                # 1. Buscar API Key de Gemini (entorno o archivos locales)
                api_key = os.environ.get("GEMINI_API_KEY")
                
                # Buscar en carpeta raíz del proyecto (un nivel arriba del servicio)
                if not api_key:
                    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gemini_key.txt")
                    if os.path.exists(key_path):
                        with open(key_path, "r", encoding="utf-8") as f:
                            api_key = f.read().strip()
                
                # Buscar en carpeta actual del servicio
                if not api_key:
                    key_path_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_key.txt")
                    if os.path.exists(key_path_local):
                        with open(key_path_local, "r", encoding="utf-8") as f:
                            api_key = f.read().strip()
                
                if not api_key:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response_body = json.dumps({
                        "error": "Clave API de Gemini no configurada. Por favor, crea un archivo llamado 'gemini_key.txt' en la carpeta raíz del proyecto e ingresa tu API Key gratuita para activar mi Ojo de Sonar. 🐳🔒"
                    })
                    self.wfile.write(response_body.encode('utf-8'))
                    return

                # 2. Leer JSON del cliente
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

                # 3. Ejecutar Inferencia de Gemini
                print("[VISION] Procesando fotograma y consultando a Gemini 1.5 Flash...")
                analisis = query_gemini_vision(api_key, image_base64)
                print("[VISION] Análisis completado con éxito.")

                # 4. Enviar Respuesta
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
