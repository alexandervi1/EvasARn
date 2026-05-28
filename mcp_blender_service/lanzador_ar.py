# -*- coding: utf-8 -*-
import os
import sys
import io
import socket
import http.server
import socketserver
import qrcode

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

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
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
