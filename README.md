# 🐳 Moby Studio — Plataforma AR 3D & AI WebXR de Docker

<p align="center">
  <img src="medios/image.png" alt="Moby Studio Preview" width="700px" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Blender-F5792A?style=for-the-badge&logo=blender&logoColor=white" alt="Blender"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/YOLOv8-00FFA6?style=for-the-badge&logo=ultralytics&logoColor=black" alt="YOLOv8"/>
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama"/>
  <img src="https://img.shields.io/badge/A--Frame-EF2D5E?style=for-the-badge&logo=aframe&logoColor=white" alt="A-Frame"/>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"/>
</p>

¡Bienvenido a **Moby Studio**! Una suite de desarrollo y simulación en **Realidad Aumentada (AR) interactiva y visión local por Inteligencia Artificial**. Diseñada originalmente sobre tecnologías WebXR, esta plataforma permite a desarrolladores y entusiastas DevOps experimentar un ecosistema de modelado 3D procedural controlado por Blender, análisis de radar asistido por YOLOv8, integración didáctica con Ollama (Qwen) y un lienzo 3D interactivo premium de alto rendimiento.

---

## ✨ Características de Calidad Premium

### 🖥️ 1. Lienzo 3D y Gizmos de Transformación (Estilo Unity)
*   **Controles de Transformación:** Edición directa en tiempo real de posición, escala y rotación de objetos en la escena 3D a través de controles interactivos fluidos.
*   **HUD de Inspector Inteligente:** Visualización y edición numérica precisa de coordenadas.
*   **Barra de Herramientas Flotante:** Acceso rápido a herramientas de navegación, imán de snapping (pasos de 0.5 unidades / 15°), borrado rápido de entidades y un robusto historial de transformaciones con **Deshacer (Undo - `Ctrl+Z`) y Rehacer (Redo - `Ctrl+Y`)**.

### 🗂️ 2. Mediateca Dinámica y Auto-Sincronización
*   **Gestor de Medios en Tiempo Real:** Muestra el peso de almacenamiento real en disco de cada modelo `.glb` alojado en el servidor.
*   **Sincronización Reactiva Inteligente (Modelos Base):** Si eliminas un modelo base (como el buque de carga o la ballena) desde la mediateca para liberar espacio en disco, la tarjeta de acceso directo en el panel de **"Modelos Base"** se ocultará dinámicamente en tiempo real en la UI, previniendo errores de carga y 404s.
*   **Compresión Draco Integrada:** Invoca en segundo plano a Blender para comprimir tus modelos mediante el algoritmo de Google Draco, reduciendo drásticamente el tamaño del archivo para cargas WebXR ultra rápidas en celulares.

### 🍕 3. Integración Directa con Poly Pizza (API Key Devs)
*   Busca y descarga al instante miles de modelos low-poly gratuitos directamente desde la interfaz del editor.
*   **Llave de Desarrollador Personalizada:** Cualquier desarrollador puede ingresar su propia API Key de Poly Pizza directamente desde la UI. Se guarda de forma 100% segura y privada en el navegador (`localStorage`) con validación visual instantánea de estado.

### 📸 4. Radar Brújula y Visión AR por IA Local (YOLOv8 + Ollama)
*   **Radar Brújula 360°:** Si el celular se desvía y los hologramas salen de pantalla, un giroscopio inteligente te muestra indicadores visuales neón en los bordes de la pantalla guiándote hacia el objeto.
*   **Visión Local Inteligente:** Envía fotogramas de la cámara trasera al backend para ejecutar inferencias locales rápidas con **YOLOv8**. Los objetos detectados se envían a **Ollama (Qwen)** para formular una analogía didáctica de cómo esos objetos físicos se relacionan con Docker (ej. la laptop representa portabilidad, una taza es persistencia de datos).

---

## 📂 Arquitectura Organizada del Repositorio

El proyecto ha sido saneado y organizado en carpetas estructuradas de acuerdo a sus responsabilidades:

```text
mcpBlender/ (Raíz del Repositorio)
├── medios/                 # Recursos multimedia e imágenes de documentación del proyecto
│   ├── image.png           # Captura principal de pantalla
│   └── WhatsApp Image...   # Captura complementaria
├── moby_studio/            # Carpeta Core de la Aplicación
│   ├── _archive/           # Backups históricos de código (server.py anterior y JS redundantes)
│   ├── output/             # Directorio activo de guardado (layout.json y modelos GLB)
│   ├── scripts/            # Scripts generadores procedurales de Blender
│   │   ├── gen_ballena.py
│   │   ├── gen_buque.py
│   │   ├── gen_laptop.py
│   │   ├── gen_server.py
│   │   ├── generar_contenedor.py
│   │   └── compress_model.py
│   ├── vision/             # Modelos y pesos de Inteligencia Artificial (YOLO)
│   │   ├── yolov8_docker_custom.pt
│   │   └── yolov8n.pt
│   ├── venv/               # Entorno Virtual Python con dependencias locales
│   ├── editor.html         # Lienzo e interfaz premium de edición 3D
│   ├── index.html          # Vista de presentación y Realidad Aumentada (Play AR)
│   └── lanzador_ar.py      # Servidor HTTP unificado y Backend API REST
├── .gitignore              # Reglas de exclusión para no subir venv/ ni pesos pesados .pt
└── README.md               # El documento que estás leyendo
```

---

## 🛠️ Guía de Inicio Rápido (Desarrollo Local)

### 1. Requisitos Previos
*   **Python 3.10+** (Instalado y en el PATH).
*   **Blender 4.2+** (Detectado automáticamente en Windows en archivos de programa o a través del PATH).
*   **Ollama** con el modelo `qwen` activo:
    ```bash
    ollama run qwen
    ```

### 2. Levantar el Servidor de Moby Studio
Navega a la carpeta del servicio central e inicia el backend en tu terminal:

```bash
cd moby_studio
python lanzador_ar.py
```

El servidor detectará dinámicamente tu dirección IP de red local (Wi-Fi) y realizará las siguientes tareas automáticamente:
1.  Generará un **Código QR único** (`qr_presentacion.png`) apuntando a tu servidor local.
2.  Iniciará el servidor HTTP con soporte para tipos MIME 3D en el puerto `8000`.
3.  Imprimirá en la consola las direcciones locales y móviles de acceso.

> **💡 Consejo Pro (Acceso Móvil HTTPS):** Para habilitar la cámara en tu celular, los navegadores exigen el protocolo HTTPS. Te recomendamos mapear el puerto local exponiéndolo mediante una herramienta segura como **Ngrok** o **Cloudflare Tunnel**:
> ```bash
> ngrok http 8000
> ```

---

## 🔌 Documentación de la API REST del Servidor

El backend de `lanzador_ar.py` expone los siguientes endpoints REST listos para interactuar con cualquier cliente:

| Endpoint | Método | Entrada | Salida | Descripción |
|---|---|---|---|---|
| `/api/list-models` | `GET` | Ninguna | `JSON Array` | Lista todos los modelos `.glb` en `output/` con tamaño real en disco y fecha de edición. |
| `/api/save-layout` | `POST` | `JSON Object` | `JSON Status` | Guarda la escena 3D actual (nombres, posiciones, rotaciones y escalas) en `output/layout.json`. |
| `/api/upload-model` | `POST` | `Binary glb` | `JSON Object` | Sube un archivo `.glb`/`.gltf` externo y lo registra en la mediateca. |
| `/api/delete-model` | `POST` | Query `?name=file.glb` | `JSON Status` | Elimina permanentemente el modelo físico de la carpeta `output/` del servidor. |
| `/api/generate-model`| `POST` | Query `?script=name.py`| `JSON Object` | Ejecuta a Blender en modo silencioso (`headless`) para compilar un modelo procedural. |
| `/api/compress-model`| `POST` | Ninguna | `JSON Status` | Comprime el modelo base actual mediante Blender usando el compresor Draco. |
| `/api/vision` | `POST` | `JSON {image: base64}` | `JSON {response: str}` | Realiza inferencia local YOLOv8 del frame de la cámara y genera analogía Docker vía Ollama. |

---

## 📝 Guía para Colaboradores (Crear Nuevos Generadores Blender)

Agregar tus propios scripts de generación 3D procedural en Blender es muy sencillo:

1.  Crea un archivo Python (ejemplo: `gen_cohete.py`) que use el módulo `bpy` de Blender para modelar, asignar materiales y exportar a la carpeta `output/`.
2.  Guárdalo dentro de la carpeta `moby_studio/scripts/`.
3.  En `moby_studio/editor.html`, añade el botón en la interfaz llamando a la API:
    ```javascript
    // Ejemplo de llamada desde el frontend
    fetch('/api/generate-model?script=gen_cohete.py', { method: 'POST' });
    ```
4.  ¡Listo! Blender compilará tu objeto procedural y la mediateca dinámica se refrescará con el nuevo archivo de inmediato.

---

## 🐳 Créditos y Comunidad
Plataforma desarrollada con amor para fusionar la diversión de los videojuegos interactivos 3D con el aprendizaje práctico del ecosistema de contenedores. ¡Dockerizar el mundo nunca fue tan visual y sorprendente! 🚀⚓
