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
import urllib.parse

import base64
import subprocess
import shutil
import glob

# Forzar codificación UTF-8 en flujos estándar de consola para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PORT = 8000

def find_blender():
    """
    Busca de manera robusta el ejecutable de Blender en el sistema.
    """
    path_blender = shutil.which("blender")
    if path_blender:
        return path_blender
    
    if os.name == 'nt':
        search_patterns = [
            r"C:\Program Files\Blender Foundation\Blender *\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender *\blender.exe",
            r"C:\Program Files\Blender Foundation\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\blender.exe"
        ]
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            if matches:
                return sorted(matches)[-1]
                
    return "blender"

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
        elif self.path == '/api/save-layout':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                layout_data = json.loads(post_data.decode('utf-8'))
                
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                ruta_layout = os.path.join(output_dir, "layout.json")
                with open(ruta_layout, "w", encoding="utf-8") as f:
                    json.dump(layout_data, f, indent=4, ensure_ascii=False)
                
                print(f"[LAYOUT] Diseño de escenario guardado en: {os.path.abspath(ruta_layout)}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"status": "success", "message": "Diseño guardado exitosamente."})
                self.wfile.write(response_body.encode('utf-8'))
                
            except Exception as e:
                print(f"[LAYOUT ERROR] Error al guardar el diseño: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla al guardar el diseño: {str(e)}"})
                self.wfile.write(response_body.encode('utf-8'))
        elif self.path.startswith('/api/upload-model'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            file_name = params.get('name', ['uploaded_model.glb'])[0]
            
            # Sanitizar nombre del archivo
            file_name = os.path.basename(file_name)
            if not file_name.endswith('.glb') and not file_name.endswith('.gltf'):
                file_name += '.glb'
                
            content_length = int(self.headers['Content-Length'])
            
            try:
                # Leer bytes binarios de la petición POST
                file_data = self.rfile.read(content_length)
                
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                ruta_archivo = os.path.join(output_dir, file_name)
                with open(ruta_archivo, "wb") as f:
                    f.write(file_data)
                    
                print(f"[UPLOAD] Nuevo modelo 3D guardado en: {os.path.abspath(ruta_archivo)}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({
                    "status": "success", 
                    "message": "Modelo importado exitosamente.", 
                    "modelId": f"modelo-{file_name.replace('.glb', '').replace('.gltf', '')}",
                    "src": f"output/{file_name}"
                })
                self.wfile.write(response_body.encode('utf-8'))
                
            except Exception as e:
                print(f"[UPLOAD ERROR] Error al subir modelo: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla al subir modelo: {str(e)}"})
                self.wfile.write(response_body.encode('utf-8'))
        elif self.path.startswith('/api/delete-model'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            file_name = params.get('name', [''])[0]
            
            # Sanitizar nombre del archivo
            file_name = os.path.basename(file_name)
            if not file_name:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": "Nombre de archivo no especificado."})
                self.wfile.write(response_body.encode('utf-8'))
                return
                
            try:
                ruta_archivo = os.path.join("output", file_name)
                
                # Verificar si el archivo realmente existe antes de borrarlo
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
                    print(f"[DELETE] Modelo 3D eliminado del disco: {os.path.abspath(ruta_archivo)}")
                    status_msg = "Modelo eliminado exitosamente."
                    status_code = 200
                else:
                    print(f"[DELETE WARNING] Intento de eliminar modelo inexistente: {os.path.abspath(ruta_archivo)}")
                    status_msg = "El archivo no existe en el disco."
                    status_code = 404
                    
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({
                    "status": "success" if status_code == 200 else "warning", 
                    "message": status_msg
                })
                self.wfile.write(response_body.encode('utf-8'))
                
            except Exception as e:
                print(f"[DELETE ERROR] Error al eliminar modelo: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla al eliminar modelo: {str(e)}"})
                self.wfile.write(response_body.encode('utf-8'))
        elif self.path.startswith('/api/generate-model'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            script_name = params.get('script', ['generar_contenedor.py'])[0]
            
            # Sanitizar y validar
            script_name = os.path.basename(script_name)
            script_path = os.path.join("scripts", script_name)
            
            if not os.path.exists(script_path):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"El script {script_name} no existe."})
                self.wfile.write(response_body.encode('utf-8'))
                return
                
            try:
                # Buscar blender
                blender_path = find_blender()
                print(f"[BLENDER ENGINE] Ejecutando {script_name} con Blender en {blender_path}...")
                
                # Ejecutar Blender en modo headless
                cmd = [blender_path, "--background", "--python", script_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print("[BLENDER ENGINE] Compilación procedural exitosa.")
                
                # Mapear el script de salida al archivo .glb generado
                mapa_modelos = {
                    "gen_ballena.py": {"file": "ballena_docker.glb", "id": "modelo-ballena_docker"},
                    "gen_buque.py": {"file": "buque_carga.glb", "id": "modelo-buque_carga"},
                    "gen_laptop.py": {"file": "laptop_caos.glb", "id": "modelo-laptop_caos"},
                    "gen_server.py": {"file": "servidor_rack.glb", "id": "modelo-servidor_rack"},
                    "generar_contenedor.py": {"file": "contenedor_docker.glb", "id": "modelo-contenedor_docker"}
                }
                
                info_modelo = mapa_modelos.get(script_name, {"file": "contenedor_docker.glb", "id": "modelo-contenedor_docker"})
                file_glb = info_modelo["file"]
                model_id = info_modelo["id"]
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({
                    "status": "success",
                    "message": f"Modelo compilado exitosamente por Blender a partir de {script_name}.",
                    "modelId": model_id,
                    "src": f"output/{file_glb}"
                })
                self.wfile.write(response_body.encode('utf-8'))
                
            except subprocess.CalledProcessError as err:
                print(f"[BLENDER ENGINE ERROR] Error en subprocess: {err.stderr}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla al ejecutar Blender: {err.stderr or err.stdout or str(err)}"})
                self.wfile.write(response_body.encode('utf-8'))
            except Exception as e:
                print(f"[BLENDER ENGINE ERROR] Error: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla en el motor de generación: {str(e)}"})
                self.wfile.write(response_body.encode('utf-8'))
        elif self.path.startswith('/api/compress-model'):
            try:
                # Buscar blender
                blender_path = find_blender()
                print("[COMPRESSION ENGINE] Ejecutando compresión Draco con Blender...")
                
                script_path = os.path.join("scripts", "compress_model.py")
                cmd = [blender_path, "--background", "--python", script_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print("[COMPRESSION ENGINE] Compresión Draco completada con éxito.")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Obtener el nuevo tamaño de archivo
                ruta_ballena = os.path.join("output", "blue whale 3d model.glb")
                size_bytes = os.path.getsize(ruta_ballena)
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB" if size_bytes >= 1024 * 1024 else f"{size_bytes / 1024:.1f} KB"
                
                response_body = json.dumps({
                    "status": "success",
                    "message": "Modelo comprimido exitosamente por Blender con Draco.",
                    "newSize": size_str
                })
                self.wfile.write(response_body.encode('utf-8'))
                
            except subprocess.CalledProcessError as err:
                print(f"[COMPRESSION ENGINE ERROR] Error en subprocess: {err.stderr}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla al comprimir con Blender: {err.stderr or err.stdout or str(err)}"})
                self.wfile.write(response_body.encode('utf-8'))
            except Exception as e:
                print(f"[COMPRESSION ENGINE ERROR] Error: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla en el motor de compresión: {str(e)}"})
                self.wfile.write(response_body.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/api/list-models':
            try:
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                modelos = []
                # Escribir una lista de archivos en el directorio output
                for file_name in os.listdir(output_dir):
                    if file_name.endswith('.glb') or file_name.endswith('.gltf'):
                        ruta = os.path.join(output_dir, file_name)
                        stat_info = os.stat(ruta)
                        size_bytes = stat_info.st_size
                        
                        # Formatear tamaño de archivo amigable
                        if size_bytes < 1024 * 1024:
                            size_str = f"{size_bytes / 1024:.1f} KB"
                        else:
                            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                            
                        # Determinar etiqueta amigable del modelo
                        nombre_amigable = file_name.replace('.glb', '').replace('.gltf', '').replace('_', ' ').replace('-', ' ').title()
                        if file_name == "blue whale 3d model.glb":
                            nombre_amigable = "🐳 Ballena Azul (Original)"
                        elif file_name == "ballena_docker.glb":
                            nombre_amigable = "🐳 Ballena Docker (Procedural)"
                        elif file_name == "contenedor_docker.glb":
                            nombre_amigable = "📦 Contenedor Estándar (Procedural)"
                        elif file_name == "laptop_caos.glb":
                            nombre_amigable = "💻 Laptop de Caos (Procedural)"
                        elif file_name == "servidor_rack.glb":
                            nombre_amigable = "🖥️ Servidor Rack (Procedural)"
                        elif file_name == "buque_carga.glb":
                            nombre_amigable = "🚢 Buque de Carga (Procedural)"
                            
                        modelos.append({
                            "name": file_name,
                            "friendlyName": nombre_amigable,
                            "size": size_str,
                            "sizeBytes": size_bytes,
                            "modelId": f"modelo-{file_name.replace('.glb', '').replace('.gltf', '').replace(' ', '_')}",
                            "src": f"output/{file_name}",
                            "date": os.path.getmtime(ruta)
                        })
                
                # Ordenar por fecha de modificación (más reciente primero)
                modelos.sort(key=lambda x: x["date"], reverse=True)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps(modelos)
                self.wfile.write(response_body.encode('utf-8'))
                
            except Exception as e:
                print(f"[LIST ERROR] Error al enlistar modelos: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": str(e)})
                self.wfile.write(response_body.encode('utf-8'))
            return
            
        # Delegar el resto de los GETs estáticos al handler base
        super().do_GET()

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
    
    # Asegurar tipos MIME correctos para modelos 3D y WASM
    CustomHTTPRequestHandler.extensions_map.update({
        '.glb': 'model/gltf-binary',
        '.gltf': 'model/gltf+json',
        '.wasm': 'application/wasm',
    })
    
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
