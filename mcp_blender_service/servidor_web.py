import http.server
import socketserver
import socket
import os
import sys

PORT = 8000

def get_local_ips():
    """
    Obtiene las direcciones IP locales de la computadora para
    facilitar la conexión desde el navegador del celular en la misma red Wi-Fi.
    """
    ips = []
    # Intento 1: Obtener dirección IP de red principal
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        main_ip = s.getsockname()[0]
        if not main_ip.startswith("127."):
            ips.append(main_ip)
        s.close()
    except Exception:
        pass

    # Intento 2: Buscar en la lista de hostnames
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass

    return ips if ips else ["127.0.0.1"]

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Habilitar CORS y cabeceras de caché útiles para pruebas WebXR
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run_server():
    # Cambiar el directorio de trabajo al directorio donde está el index.html
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    Handler = CustomHTTPRequestHandler
    
    # Permitir la reutilización del puerto inmediatamente después de cerrarlo
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            local_ips = get_local_ips()
            
            print("=" * 70)
            print("[OK] SERVIDOR WEBXR AR LEVANTADO CON EXITO")
            print(f"Directorio servido: {current_dir}")
            print(f"Puerto local: {PORT}")
            print("-" * 70)
            print("Para probar en esta computadora, abre:")
            print(f"   -> http://localhost:{PORT}")
            print("-" * 70)
            print("Para entrar desde el navegador de tu CELULAR (misma red Wi-Fi):")
            for ip in local_ips:
                print(f"   -> http://{ip}:{PORT}")
            print("=" * 70)
            print("Presiona Ctrl+C para detener el servidor web.")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\nServidor web detenido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"Error crítico al iniciar el servidor web: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_server()
