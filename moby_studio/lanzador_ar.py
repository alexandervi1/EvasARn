# -*- coding: utf-8 -*-
import os
import sys
import io
import socket
import http.server
import socketserver
import json
import urllib.request
import urllib.parse

import base64
import subprocess
import shutil
import glob
import time
import zipfile
import hashlib

USERS_FILE = os.path.join("projects", "users.json")

def load_users():
    os.makedirs("projects", exist_ok=True)
    if not os.path.exists(USERS_FILE):
        admin_hash = hashlib.sha256("admin123".encode("utf-8")).hexdigest()
        viewer_hash = hashlib.sha256("viewer123".encode("utf-8")).hexdigest()
        default_users = {
            "admin": {
                "username": "admin",
                "password_hash": admin_hash,
                "role": "owner",
                "color": "#22d3ee",
                "userId": "user-admin"
            },
            "viewer": {
                "username": "viewer",
                "password_hash": viewer_hash,
                "role": "cliente",
                "color": "#a78bfa",
                "userId": "user-viewer"
            }
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=4, ensure_ascii=False)
        return default_users
        
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

try:
    import qrcode
except ImportError:
    qrcode = None

# Forzar codificación UTF-8 en flujos estándar de consola para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PORT = 8000

ASSET_EXTENSIONS = {
    ".glb": "model",
    ".gltf": "model",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".gif": "image",
    ".mp4": "video",
    ".webm": "video",
    ".mov": "video",
    ".mind": "target",
    ".json": "data"
}

PROTECTED_OUTPUT_FILES = {"layout.json"}
PROJECTS_DIR = "projects"
ARCHIVE_DIR = "_archive"
COLLAB_TTL_SECONDS = 18
COLLAB_STATE = {}

def send_json(handler, status, payload):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

def safe_project_name(name):
    raw = (name or "default").strip().lower()
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in raw).strip("-_")
    return safe or "default"

def project_layout_path(project):
    safe = safe_project_name(project)
    return os.path.join(PROJECTS_DIR, safe, "layout.json")

def read_layout_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_default_project():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    default_path = project_layout_path("default")
    if not os.path.exists(default_path):
        legacy_path = os.path.join("output", "layout.json")
        os.makedirs(os.path.dirname(default_path), exist_ok=True)
        if os.path.exists(legacy_path):
            shutil.copyfile(legacy_path, default_path)
        else:
            with open(default_path, "w", encoding="utf-8") as f:
                json.dump({"stage": {"width": 3, "height": 3, "gridVisible": True}, "entities": [], "version": 0}, f, indent=4, ensure_ascii=False)

def list_projects():
    ensure_default_project()
    projects = []
    for name in os.listdir(PROJECTS_DIR):
        path = project_layout_path(name)
        if not os.path.isfile(path):
            continue
        try:
            data = read_layout_file(path)
        except Exception:
            data = {}
        stat_info = os.stat(path)
        projects.append({
            "name": name,
            "version": int(data.get("version", 0)) if isinstance(data, dict) else 0,
            "updatedAt": data.get("updatedAt") if isinstance(data, dict) else None,
            "entities": len(data.get("entities", [])) if isinstance(data, dict) and isinstance(data.get("entities"), list) else 0,
            "date": stat_info.st_mtime
        })
    projects.sort(key=lambda item: item["date"], reverse=True)
    return projects

def list_archived_projects():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    projects = []
    for name in os.listdir(ARCHIVE_DIR):
        path = os.path.join(ARCHIVE_DIR, name, "layout.json")
        if not os.path.isfile(path):
            continue
        try:
            data = read_layout_file(path)
        except Exception:
            data = {}
        stat_info = os.stat(path)
        projects.append({
            "name": name,
            "version": int(data.get("version", 0)) if isinstance(data, dict) else 0,
            "updatedAt": data.get("updatedAt") if isinstance(data, dict) else None,
            "entities": len(data.get("entities", [])) if isinstance(data, dict) and isinstance(data.get("entities"), list) else 0,
            "date": stat_info.st_mtime
        })
    projects.sort(key=lambda item: item["date"], reverse=True)
    return projects

def collab_project_state(project):
    safe = safe_project_name(project)
    if safe not in COLLAB_STATE:
        COLLAB_STATE[safe] = {"users": {}, "locks": {}}
    cleanup_collab_state(safe)
    return COLLAB_STATE[safe]

def cleanup_collab_state(project):
    state = COLLAB_STATE.get(project)
    if not state:
        return
    now = time.time()
    expired_users = [
        user_id for user_id, user in state["users"].items()
        if now - float(user.get("lastSeen", 0)) > COLLAB_TTL_SECONDS
    ]
    for user_id in expired_users:
        state["users"].pop(user_id, None)
    expired_locks = [
        object_id for object_id, lock in state["locks"].items()
        if lock.get("userId") in expired_users or now - float(lock.get("lastSeen", 0)) > COLLAB_TTL_SECONDS
    ]
    for object_id in expired_locks:
        state["locks"].pop(object_id, None)

def collab_payload(project):
    safe = safe_project_name(project)
    state = collab_project_state(project)
    layout_version = 0
    updated_at = None
    path = project_layout_path(safe)
    if os.path.exists(path):
        try:
            data = read_layout_file(path)
            if isinstance(data, dict):
                layout_version = int(data.get("version", 0))
                updated_at = data.get("updatedAt")
        except Exception:
            pass
    return {
        "project": safe,
        "version": layout_version,
        "updatedAt": updated_at,
        "users": list(state["users"].values()),
        "locks": state["locks"]
    }

def format_size(size_bytes):
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"

def asset_kind(file_name):
    return ASSET_EXTENSIONS.get(os.path.splitext(file_name.lower())[1], "other")

def friendly_asset_name(file_name):
    name = os.path.splitext(file_name)[0].replace("_", " ").replace("-", " ").title()
    known = {
        "blue whale 3d model.glb": "Ballena Azul (Original)",
        "ballena_docker.glb": "Ballena Docker (Procedural)",
        "contenedor_docker.glb": "Contenedor Estandar (Procedural)",
        "laptop_caos.glb": "Laptop de Caos (Procedural)",
        "servidor_rack.glb": "Servidor Rack (Procedural)",
        "buque_carga.glb": "Buque de Carga (Procedural)",
        "qr_presentacion.png": "QR de Presentacion"
    }
    return known.get(file_name, name)

def collect_layout_asset_usage():
    usage = {}
    model_id_to_file = {
        "modelo-ballena": "blue whale 3d model.glb",
        "modelo-laptop": "laptop_caos.glb",
        "modelo-rack": "servidor_rack.glb",
        "modelo-buque": "buque_carga.glb"
    }
    layout_path = os.path.join("output", "layout.json")
    if not os.path.exists(layout_path):
        return usage
    try:
        with open(layout_path, "r", encoding="utf-8") as f:
            layout = json.load(f)
        entities = layout.get("entities", []) if isinstance(layout, dict) else layout
        for obj in entities if isinstance(entities, list) else []:
            label = obj.get("nombre") or obj.get("uuid") or "Objeto"
            model_id = obj.get("modelId")
            if isinstance(model_id, str):
                if model_id in model_id_to_file:
                    usage.setdefault(model_id_to_file[model_id], []).append({"field": "modelId", "object": label})
                elif model_id.startswith("modelo-"):
                    guessed = model_id.replace("modelo-", "").replace("_", " ")
                    for ext in (".glb", ".gltf"):
                        file_name = f"{guessed}{ext}"
                        if os.path.exists(os.path.join("output", file_name)):
                            usage.setdefault(file_name, []).append({"field": "modelId", "object": label})
                            break
            for field in ("mediaUrl", "markerImage", "mindTargetUrl", "glbUrl"):
                value = obj.get(field)
                if isinstance(value, str) and value.startswith("output/"):
                    name = os.path.basename(value)
                    usage.setdefault(name, []).append({"field": field, "object": label})
    except Exception as err:
        print(f"[ASSETS WARNING] No se pudo leer uso de layout: {err}")
    return usage

def export_experience_package(package_name="moby_experience"):
    output_dir = "output"
    exports_dir = os.path.join(output_dir, "exports")
    layout_path = os.path.join(output_dir, "layout.json")

    if not os.path.exists(layout_path):
        raise FileNotFoundError("No existe output/layout.json. Guarda la escena antes de exportar.")

    os.makedirs(exports_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in package_name).strip("_") or "moby_experience"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    zip_name = f"{safe_name}_{timestamp}.zip"
    zip_path = os.path.join(exports_dir, zip_name)

    usage = collect_layout_asset_usage()
    used_files = sorted(usage.keys())
    missing_assets = []
    included_assets = []

    with open(layout_path, "r", encoding="utf-8") as f:
        layout_data = json.load(f)

    manifest = {
        "name": safe_name,
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "entrypoint": "index.html",
        "layout": "output/layout.json",
        "assets": [],
        "missingAssets": []
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        if os.path.exists("index.html"):
            package.write("index.html", "index.html")
        package.write(layout_path, "output/layout.json")

        for file_name in used_files:
            asset_path = os.path.join(output_dir, file_name)
            fallback_path = file_name if os.path.exists(file_name) and os.path.isfile(file_name) else None
            source_path = asset_path if os.path.exists(asset_path) and os.path.isfile(asset_path) else fallback_path
            if source_path:
                package.write(source_path, f"output/{file_name}")
                included_assets.append(file_name)
                manifest["assets"].append({
                    "name": file_name,
                    "path": f"output/{file_name}",
                    "kind": asset_kind(file_name),
                    "usedBy": usage.get(file_name, [])
                })
            else:
                missing_assets.append(file_name)
                manifest["missingAssets"].append(file_name)

        package.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        package.writestr(
            "README_EXPORT.txt",
            "Moby Studio export\n\n"
            "Abre esta experiencia sirviendo la carpeta descomprimida con un servidor HTTP local.\n"
            "Entrada: index.html\n"
            "Layout: output/layout.json\n"
        )

    return {
        "zipName": zip_name,
        "zipPath": f"output/exports/{zip_name}",
        "assetCount": len(included_assets),
        "missingAssets": missing_assets,
        "size": format_size(os.path.getsize(zip_path)),
        "layoutEntities": len(layout_data.get("entities", [])) if isinstance(layout_data, dict) else 0
    }

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

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE DE VISIÓN: Gemma4:e2b Multimodal (ve la imagen directamente)
# ─────────────────────────────────────────────────────────────────────────────
# Gemma4:e2b reemplaza completamente a YOLO porque:
#  - YOLO solo detecta objetos físicos con bounding boxes (no lee texto ni UI)
#  - YOLO nunca puede entender Docker Desktop, terminales ni código en pantalla
#  - Gemma4:e2b ve la imagen completa y la explica con contexto Docker educativo

SYSTEM_PROMPT_DOCKER = """Eres Moby, la mascota oficial de Docker — una ballena simpática, didáctica y entusiasta.
Tu misión es analizar imágenes del entorno real o de pantallas de computadora y explicar Docker de forma pedagógica.

Reglas:
- Responde SIEMPRE en español.
- Máximo 3 oraciones cortas y claras.
- Si ves objetos físicos (laptop, teclado, ratón, taza, cables, pantalla, teléfono): haz una analogía Docker creativa con cada objeto.
- Si ves interfaces de software (Docker Desktop, terminal, dashboard, código, navegador, contenedores corriendo): explica lo que ves de forma educativa y menciona conceptos Docker relevantes (imagen, contenedor, volumen, red, compose, registry, Dockerfile).
- Si ves una terminal con comandos docker: lee los comandos visibles y explica qué hacen.
- Si ves Docker Desktop: describe el estado de los contenedores visibles y explica qué significa cada sección.
- Si la imagen está borrosa o vacía: invita al usuario a enfocar la cámara hacia algo relacionado con Docker o computación.
- Nunca menciones que eres una IA o un modelo de lenguaje. Eres Moby, la ballena.
- Usa 1 emoji por respuesta máximo. Preferir 🐳."""

def query_gemma_vision(base64_image_data: str) -> str:
    """
    Pipeline de visión: envía la imagen directamente a Gemma4:e2b
    (modelo multimodal local via Ollama) para análisis visual completo.
    Funciona con objetos físicos E interfaces de computadora (Docker Desktop,
    terminales, código, dashboards).
    """
    # Limpiar prefijo data URI si existe
    if "," in base64_image_data:
        base64_image_data = base64_image_data.split(",")[1]

    # Asegurar padding correcto
    missing_padding = len(base64_image_data) % 4
    if missing_padding:
        base64_image_data += '=' * (4 - missing_padding)

    print("[GEMMA VISION] Enviando imagen a gemma4:e2b para análisis multimodal...")

    try:
        url_ollama = "http://localhost:11434/api/chat"
        payload = {
            "model": "gemma4:e2b",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": SYSTEM_PROMPT_DOCKER + "\n\nAnaliza esta imagen y responde como Moby:",
                    "images": [base64_image_data]
                }
            ],
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 200
            }
        }

        req = urllib.request.Request(
            url_ollama,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            message = res_data.get("message", {})
            content = message.get("content", "").strip()
            if content:
                print(f"[GEMMA VISION] Análisis completado: {len(content)} caracteres.")
                return content
            return None

    except Exception as e:
        print(f"[GEMMA VISION] Error: {str(e)}")
        return None


def analizar_vision(base64_image_data: str) -> str:
    """
    Pipeline de visión usando Gemma4:e2b (multimodal).
    Si Ollama no está disponible, devuelve un mensaje de ayuda claro.
    YOLO fue eliminado: no puede leer interfaces ni explicar Docker.
    """
    resultado = query_gemma_vision(base64_image_data)
    if resultado:
        return resultado

    print("[VISION] Gemma4:e2b no disponible. Ollama no está corriendo o el modelo no está descargado.")
    return (
        "¡Ups! Mi cerebro de visión no está activo. "
        "Asegúrate de que Ollama esté corriendo y de haber descargado el modelo "
        "con: ollama pull gemma4:e2b 🐳"
    )


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

                # 2. Ejecutar pipeline de visión: Gemma3 multimodal → fallback YOLO+Ollama
                print("[VISION] Iniciando pipeline de visión inteligente...")
                analisis = analizar_vision(image_base64)
                print("[VISION] Análisis completado.")

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
        elif self.path.startswith('/api/save-layout'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                layout_data = json.loads(post_data.decode('utf-8'))
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                requested_project = layout_data.get("project", "default") if isinstance(layout_data, dict) else "default"
                requested_version = layout_data.get("expectedVersion", None) if isinstance(layout_data, dict) else None
                project = safe_project_name(params.get('project', [requested_project])[0])
                expected_version_raw = params.get('version', [requested_version])[0]
                
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                ensure_default_project()
                ruta_proyecto = project_layout_path(project)
                os.makedirs(os.path.dirname(ruta_proyecto), exist_ok=True)

                current_version = 0
                if os.path.exists(ruta_proyecto):
                    try:
                        current_data = read_layout_file(ruta_proyecto)
                        current_version = int(current_data.get("version", 0)) if isinstance(current_data, dict) else 0
                    except Exception:
                        current_version = 0

                if expected_version_raw not in (None, ""):
                    try:
                        expected_version = int(expected_version_raw)
                    except Exception:
                        expected_version = current_version
                    if expected_version != current_version:
                        send_json(self, 409, {
                            "error": "conflict",
                            "message": "El proyecto fue guardado por otra persona. Recarga antes de sobrescribir.",
                            "project": project,
                            "serverVersion": current_version,
                            "clientVersion": expected_version
                        })
                        return

                next_version = current_version + 1
                if isinstance(layout_data, dict):
                    layout_data["project"] = project
                    layout_data["version"] = next_version
                    layout_data["updatedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")

                with open(ruta_proyecto, "w", encoding="utf-8") as f:
                    json.dump(layout_data, f, indent=4, ensure_ascii=False)

                # Mantener compatibilidad: la vista final sigue leyendo output/layout.json.
                ruta_layout = os.path.join(output_dir, "layout.json")
                with open(ruta_layout, "w", encoding="utf-8") as f:
                    json.dump(layout_data, f, indent=4, ensure_ascii=False)
                
                print(f"[LAYOUT] Proyecto '{project}' guardado v{next_version}: {os.path.abspath(ruta_proyecto)}")
                send_json(self, 200, {
                    "status": "success",
                    "message": "Diseño guardado exitosamente.",
                    "project": project,
                    "version": next_version,
                    "layoutPath": ruta_proyecto
                })
                
            except Exception as e:
                print(f"[LAYOUT ERROR] Error al guardar el diseño: {str(e)}")
                send_json(self, 500, {"error": f"Falla al guardar el diseño: {str(e)}"})
        elif self.path.startswith('/api/collab-heartbeat'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'

            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                project = safe_project_name(data.get("project", "default"))
                user_id = str(data.get("userId") or "").strip()
                if not user_id:
                    send_json(self, 400, {"error": "Falta userId."})
                    return

                now = time.time()
                state = collab_project_state(project)
                user = {
                    "userId": user_id,
                    "name": str(data.get("name") or "Usuario").strip()[:40],
                    "color": str(data.get("color") or "#22d3ee")[:24],
                    "selectedObject": data.get("selectedObject") or None,
                    "lastSeen": now
                }
                state["users"][user_id] = user

                for object_id, lock in list(state["locks"].items()):
                    if lock.get("userId") == user_id:
                        state["locks"].pop(object_id, None)

                selected = data.get("selectedObject")
                if selected:
                    existing = state["locks"].get(selected)
                    if not existing or existing.get("userId") == user_id or now - float(existing.get("lastSeen", 0)) > COLLAB_TTL_SECONDS:
                        state["locks"][selected] = {
                            "userId": user_id,
                            "name": user["name"],
                            "color": user["color"],
                            "lastSeen": now
                        }

                send_json(self, 200, collab_payload(project))
            except Exception as e:
                print(f"[COLLAB ERROR] Heartbeat falló: {str(e)}")
                send_json(self, 500, {"error": str(e)})
        elif self.path.startswith('/api/collab-release'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                project = safe_project_name(data.get("project", "default"))
                user_id = str(data.get("userId") or "").strip()
                state = collab_project_state(project)
                for object_id, lock in list(state["locks"].items()):
                    if lock.get("userId") == user_id:
                        state["locks"].pop(object_id, None)
                send_json(self, 200, collab_payload(project))
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
        elif self.path.startswith('/api/generate-qr'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            qr_text = params.get('text', [''])[0].strip()
            file_name = params.get('name', [''])[0].strip()

            if not qr_text:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Texto QR no especificado."}).encode('utf-8'))
                return

            if qrcode is None:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "La librería qrcode no está instalada en este Python. Usa moby_studio\\venv\\Scripts\\python.exe lanzador_ar.py."}).encode('utf-8'))
                return

            safe_name = os.path.basename(file_name or f"qr_{abs(hash(qr_text))}.png")
            if not safe_name.lower().endswith(".png"):
                safe_name += ".png"

            try:
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                ruta_qr = os.path.join(output_dir, safe_name)
                img.save(ruta_qr)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({
                    "status": "success",
                    "message": "QR generado exitosamente.",
                    "src": f"output/{safe_name}",
                    "text": qr_text
                })
                self.wfile.write(response_body.encode('utf-8'))
            except Exception as e:
                print(f"[QR ERROR] Error al generar QR: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Falla al generar QR: {str(e)}"}).encode('utf-8'))
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
        elif self.path.startswith('/api/upload-media'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            file_name = params.get('name', ['uploaded_file.bin'])[0]
            
            # Sanitizar nombre del archivo
            file_name = os.path.basename(file_name)
                
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
                    
                print(f"[UPLOAD-MEDIA] Archivo multimedia guardado en: {os.path.abspath(ruta_archivo)}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({
                    "status": "success", 
                    "message": "Archivo multimedia subido exitosamente.", 
                    "src": f"output/{file_name}"
                })
                self.wfile.write(response_body.encode('utf-8'))
                
            except Exception as e:
                print(f"[UPLOAD-MEDIA ERROR] Error al subir archivo: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response_body = json.dumps({"error": f"Falla al subir archivo: {str(e)}"})
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
        elif self.path.startswith('/api/delete-asset'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            file_name = os.path.basename(params.get('name', [''])[0])

            if not file_name:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Nombre de archivo no especificado."}).encode('utf-8'))
                return

            if file_name in PROTECTED_OUTPUT_FILES:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Este archivo esta protegido y no se puede eliminar desde la mediateca."}).encode('utf-8'))
                return

            try:
                ruta_archivo = os.path.join("output", file_name)
                if not os.path.exists(ruta_archivo):
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "warning", "message": "El archivo no existe en el disco."}).encode('utf-8'))
                    return

                os.remove(ruta_archivo)
                print(f"[DELETE-ASSET] Asset eliminado: {os.path.abspath(ruta_archivo)}")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Asset eliminado correctamente."}).encode('utf-8'))
            except Exception as e:
                print(f"[DELETE-ASSET ERROR] Error al eliminar asset: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Falla al eliminar asset: {str(e)}"}).encode('utf-8'))
        elif self.path.startswith('/api/export-experience'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            package_name = params.get('name', ['moby_experience'])[0]

            try:
                export_data = export_experience_package(package_name)
                print(f"[EXPORT] Experiencia exportada: {export_data['zipPath']}")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "message": "Experiencia exportada correctamente.",
                    **export_data
                }).encode('utf-8'))
            except Exception as e:
                print(f"[EXPORT ERROR] Error al exportar experiencia: {str(e)}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Falla al exportar experiencia: {str(e)}"}).encode('utf-8'))
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
                # Obtener el nombre del archivo del parámetro 'name'
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                model_name = params.get('name', ['blue whale 3d model.glb'])[0]
                model_name = os.path.basename(model_name) # Sanitizar

                # Buscar blender
                blender_path = find_blender()
                print(f"[COMPRESSION ENGINE] Ejecutando compresión Draco con Blender para: {model_name}...")
                
                script_path = os.path.join("scripts", "compress_model.py")
                cmd = [blender_path, "--background", "--python", script_path, "--", model_name]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"[COMPRESSION ENGINE] Compresión Draco de {model_name} completada con éxito.")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Obtener el nuevo tamaño de archivo
                ruta_modelo = os.path.join("output", model_name)
                size_bytes = os.path.getsize(ruta_modelo)
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB" if size_bytes >= 1024 * 1024 else f"{size_bytes / 1024:.1f} KB"
                
                response_body = json.dumps({
                    "status": "success",
                    "message": f"Modelo {model_name} comprimido exitosamente por Blender con Draco.",
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
        elif self.path.startswith('/api/duplicate-project'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                project = safe_project_name(data.get("project"))
                new_project = safe_project_name(data.get("newProject"))
                
                src_dir = os.path.join(PROJECTS_DIR, project)
                dst_dir = os.path.join(PROJECTS_DIR, new_project)
                
                if not os.path.exists(src_dir):
                    send_json(self, 404, {"error": f"El proyecto origen '{project}' no existe."})
                    return
                if os.path.exists(dst_dir):
                    send_json(self, 400, {"error": f"El proyecto destino '{new_project}' ya existe."})
                    return
                
                shutil.copytree(src_dir, dst_dir)
                
                # Modificar el layout.json en el destino
                dst_layout = os.path.join(dst_dir, "layout.json")
                if os.path.exists(dst_layout):
                    layout_data = read_layout_file(dst_layout)
                    if isinstance(layout_data, dict):
                        layout_data["project"] = new_project
                        layout_data["version"] = 1
                        layout_data["updatedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        with open(dst_layout, "w", encoding="utf-8") as f:
                            json.dump(layout_data, f, indent=4, ensure_ascii=False)
                
                send_json(self, 200, {"status": "success", "message": f"Proyecto duplicado como '{new_project}'."})
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
        elif self.path.startswith('/api/rename-project'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                project = safe_project_name(data.get("project"))
                new_project = safe_project_name(data.get("newProject"))
                
                src_dir = os.path.join(PROJECTS_DIR, project)
                dst_dir = os.path.join(PROJECTS_DIR, new_project)
                
                if not os.path.exists(src_dir):
                    send_json(self, 404, {"error": f"El proyecto '{project}' no existe."})
                    return
                if os.path.exists(dst_dir):
                    send_json(self, 400, {"error": f"El proyecto '{new_project}' ya existe."})
                    return
                
                os.rename(src_dir, dst_dir)
                
                # Modificar el layout.json en el destino
                dst_layout = os.path.join(dst_dir, "layout.json")
                if os.path.exists(dst_layout):
                    layout_data = read_layout_file(dst_layout)
                    if isinstance(layout_data, dict):
                        layout_data["project"] = new_project
                        layout_data["updatedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        with open(dst_layout, "w", encoding="utf-8") as f:
                            json.dump(layout_data, f, indent=4, ensure_ascii=False)
                
                send_json(self, 200, {"status": "success", "message": f"Proyecto renombrado a '{new_project}'."})
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
        elif self.path.startswith('/api/archive-project'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                project = safe_project_name(data.get("project"))
                
                src_dir = os.path.join(PROJECTS_DIR, project)
                archive_project_dir = os.path.join(ARCHIVE_DIR, project)
                
                if not os.path.exists(src_dir):
                    send_json(self, 404, {"error": f"El proyecto '{project}' no existe."})
                    return
                
                os.makedirs(ARCHIVE_DIR, exist_ok=True)
                if os.path.exists(archive_project_dir):
                    shutil.rmtree(archive_project_dir)
                
                shutil.move(src_dir, archive_project_dir)
                send_json(self, 200, {"status": "success", "message": f"Proyecto '{project}' archivado con éxito."})
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
        elif self.path.startswith('/api/restore-project'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                project = safe_project_name(data.get("project"))
                
                src_dir = os.path.join(ARCHIVE_DIR, project)
                dst_dir = os.path.join(PROJECTS_DIR, project)
                
                if not os.path.exists(src_dir):
                    send_json(self, 404, {"error": f"El proyecto '{project}' no se encuentra en el archivo."})
                    return
                
                if os.path.exists(dst_dir):
                    send_json(self, 400, {"error": f"El proyecto activo '{project}' ya existe. Renómbralo o elíminalo antes de restaurar."})
                    return
                
                shutil.move(src_dir, dst_dir)
                send_json(self, 200, {"status": "success", "message": f"Proyecto '{project}' restaurado con éxito."})
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
        elif self.path.startswith('/api/login'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                username = str(data.get("username") or "").strip().lower()
                password = str(data.get("password") or "")
                
                if not username or not password:
                    send_json(self, 400, {"error": "Usuario y contraseña requeridos."})
                    return
                
                users = load_users()
                if username not in users:
                    send_json(self, 404, {"error": "Usuario no encontrado."})
                    return
                
                user = users[username]
                password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
                
                if user["password_hash"] != password_hash:
                    send_json(self, 401, {"error": "Contraseña incorrecta."})
                    return
                
                send_json(self, 200, {
                    "status": "success",
                    "message": "Inicio de sesión exitoso.",
                    "user": {
                        "username": user["username"],
                        "role": user["role"],
                        "color": user["color"],
                        "userId": user["userId"]
                    }
                })
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
        elif self.path.startswith('/api/register'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8') or '{}')
                username = str(data.get("username") or "").strip().lower()
                password = str(data.get("password") or "")
                role = str(data.get("role") or "editor")
                color = str(data.get("color") or "#22d3ee")
                
                if not username or not password:
                    send_json(self, 400, {"error": "Usuario y contraseña requeridos."})
                    return
                
                if len(username) < 3 or len(password) < 4:
                    send_json(self, 400, {"error": "El usuario debe tener al menos 3 caracteres y la contraseña al menos 4."})
                    return
                
                users = load_users()
                if username in users:
                    send_json(self, 400, {"error": "El nombre de usuario ya está registrado."})
                    return
                
                user_id = f"user-{int(time.time())}-{username}"
                password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
                
                users[username] = {
                    "username": username,
                    "password_hash": password_hash,
                    "role": role,
                    "color": color,
                    "userId": user_id
                }
                save_users(users)
                
                send_json(self, 200, {
                    "status": "success",
                    "message": "Registro completado con éxito.",
                    "user": {
                        "username": username,
                        "role": role,
                        "color": color,
                        "userId": user_id
                    }
                })
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/list-projects'):
            try:
                send_json(self, 200, {"projects": list_projects()})
            except Exception as e:
                print(f"[PROJECTS ERROR] Error al enlistar proyectos: {str(e)}")
                send_json(self, 500, {"error": str(e)})
            return

        if self.path.startswith('/api/list-archived-projects'):
            try:
                send_json(self, 200, {"projects": list_archived_projects()})
            except Exception as e:
                print(f"[PROJECTS ERROR] Error al enlistar proyectos archivados: {str(e)}")
                send_json(self, 500, {"error": str(e)})
            return

        if self.path.startswith('/api/connection-info'):
            client_ip = self.client_address[0]
            is_local = client_ip in ('127.0.0.1', '::1', 'localhost')
            send_json(self, 200, {
                "clientIp": client_ip,
                "isLocal": is_local
            })
            return

        if self.path.startswith('/api/load-layout'):
            try:
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                project = safe_project_name(params.get('project', ['default'])[0])
                ensure_default_project()
                path = project_layout_path(project)
                if not os.path.exists(path):
                    send_json(self, 404, {"error": "Proyecto no encontrado.", "project": project})
                    return
                data = read_layout_file(path)
                if isinstance(data, dict):
                    data.setdefault("project", project)
                    data.setdefault("version", 0)
                send_json(self, 200, data)
            except Exception as e:
                print(f"[LAYOUT ERROR] Error al cargar proyecto: {str(e)}")
                send_json(self, 500, {"error": str(e)})
            return

        if self.path.startswith('/api/collab-state'):
            try:
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                project = safe_project_name(params.get('project', ['default'])[0])
                send_json(self, 200, collab_payload(project))
            except Exception as e:
                send_json(self, 500, {"error": str(e)})
            return

        if self.path == '/api/list-assets':
            try:
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                usage = collect_layout_asset_usage()
                assets = []
                for file_name in os.listdir(output_dir):
                    ruta = os.path.join(output_dir, file_name)
                    if not os.path.isfile(ruta):
                        continue
                    ext = os.path.splitext(file_name.lower())[1]
                    kind = asset_kind(file_name)
                    stat_info = os.stat(ruta)
                    src = f"output/{file_name}"
                    usage_items = usage.get(file_name, [])
                    assets.append({
                        "name": file_name,
                        "friendlyName": friendly_asset_name(file_name),
                        "kind": kind,
                        "extension": ext,
                        "size": format_size(stat_info.st_size),
                        "sizeBytes": stat_info.st_size,
                        "src": src,
                        "modelId": f"modelo-{file_name.replace('.glb', '').replace('.gltf', '').replace(' ', '_')}" if kind == "model" else None,
                        "date": os.path.getmtime(ruta),
                        "protected": file_name in PROTECTED_OUTPUT_FILES,
                        "usedBy": usage_items,
                        "usedCount": len(usage_items)
                    })

                assets.sort(key=lambda x: x["date"], reverse=True)
                send_json(self, 200, assets)
            except Exception as e:
                print(f"[ASSETS ERROR] Error al enlistar assets: {str(e)}")
                send_json(self, 500, {"error": str(e)})
            return

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
