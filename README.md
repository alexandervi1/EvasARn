# 🐳 Moby AR AI Assistant - Experiencia Conversacional WebXR de Docker

¡Bienvenido a **Moby AR AI Assistant**! Esta es una plataforma educativa de vanguardia en **Realidad Aumentada (RA) WebXR** que te permite interactuar en tiempo real con **Moby**, la ballena mascota de Docker. 

La aplicación combina modelado procedimental 3D generado por Blender, Inteligencia Artificial local a través de **Ollama (Qwen 3B)**, reconocimiento/síntesis de voz en español nativo, transiciones animadas automáticas (metáforas visuales) y un sistema interactivo de gamificación en tiempo real inspirado en **Pokémon Go**.

---

## ✨ Características Principales

### 📸 1. Realidad Aumentada Real (Video Pass-Through)
- Integra la cámara trasera de tu dispositivo móvil (`facingMode: environment`) directamente en el fondo de la escena 3D a través de la transparencia de lienzo alfa en A-Frame.
- Los hologramas 3D flotan y se integran de manera fluida y responsiva sobre tu espacio físico real.

### 🧭 2. Radar Brújula de Orientación (Estilo Pokémon Go)
- Si giras tu celular y Moby sale del ángulo de visión directo de tu cámara, un **radar brújula inteligente 360°** detecta el cambio de giroscopio.
- Te muestra indicadores neón parpadeantes en los bordes de la pantalla (`🐳 Moby a tu izquierda` / `Moby a tu derecha 🐳`) guiándote de manera intuitiva para centrar el modelo en tu pantalla nuevamente.

### 📦 3. Despliegue de Contenedores (Pokéball Throw Interactive)
- Cuenta con un panel de **Acciones Rápidas** táctiles en el HUD.
- **Lanzar Contenedor**: Dispara un contenedor industrial 3D neón animado desde tu pantalla hacia Moby. Al impactar, estalla en un **anillo expansivo neón** y hace que Moby realice una **pirueta acrobática (giro delfín de 360°)** en el aire. Al caer, Moby comparte un tip o concepto técnico práctico sobre el microservicio desplegado (Nginx, PostgreSQL, Redis, Node.js, Flask o Alpine) por audio y texto.
- **Hacer Truco**: Moby realiza saltos y wiggles laterales alegres interactuando contigo.

### 👆 4. Reacciones Físicas al Toque (Raycasting 3D)
Puedes tocar o dar un toque directamente en la pantalla sobre los hologramas 3D para activarlos:
- **Moby (Ballena)**: Salta alegremente y emite saludos alegres de voz.
- **Laptop de Caos**: Tiembla rápidamente con fallas de glitches (`jitter`) alertándote de las inconsistencias del desarrollo local clásico.
- **Servidor Rack**: Sufre una pulsación de escala y Moby celebra que la infraestructura en producción está escalada.
- **Buque de Carga**: Se balancea de babor a estribor sobre olas virtuales representando la portabilidad marítima de los contenedores Docker.

### 🎙️ 5. Chat Conversacional por Voz (STT y TTS)
- **Reconocimiento de Voz Nativo (Speech-to-Text)**: Presiona el micrófono en el panel, háblale en voz alta sobre Docker y tu consulta se transcribirá en tiempo real para ser evaluada directamente por la IA.
- **Voz Cute de Mascota (Text-to-Speech)**: Moby habla contigo con una tierna voz alta de mascota (Pitch: 1.3, Rate: 1.12) en español nativo, modulada dinámicamente.

---

## 🛠️ Estructura del Proyecto

```text
mcpBlender/
├── moby_studio/              # Código principal del servicio AR
│   ├── output/               # Modelos procedimentales 3D (.glb)
│   │   ├── ballena_docker.glb  # Moby (con una pirámide de contenedores apilada en su lomo)
│   │   ├── buque_carga.glb     # Barco carguero industrial
│   │   ├── laptop_caos.glb     # Laptop con dependencias glitching
│   │   └── servidor_rack.glb   # Rack de servidores de producción
│   ├── scripts/              # Scripts de modelado automatizado en Blender
│   │   ├── gen_ballena.py
│   │   └── gen_buque.py
│   ├── index.html            # Frontend WebXR, HUD Glassmorphism, CSS y lógica interactiva
│   ├── lanzador_ar.py        # Servidor local de desarrollo automatizado con forzado UTF-8
│   └── server.py             # Servidor API secundario
├── medios/                   # Contiene imágenes auxiliares y recursos multimedia
├── .gitignore                # Reglas de exclusión para control de versiones (Git)
└── README.md                 # El documento que estás leyendo
```

---

## 🚀 Guía de Instalación y Uso Local

### 1. Requisitos Previos
- **Blender** (versión 4.2+ recomendada para exportación de modelos `.glb`).
- **Python 3.10+**.
- **Ollama** con el modelo `qwen` descargado y ejecutándose:
  ```bash
  ollama run qwen
  ```

### 2. Generación Automatizada de Modelos 3D (Blender headless)
Si deseas regenerar los archivos 3D `.glb` procedimentales a partir de los scripts matemáticos:
```bash
# Generar la Ballena Docker
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python moby_studio/scripts/gen_ballena.py

# Generar el Buque de Carga
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python moby_studio/scripts/gen_buque.py
```
*(Nota: Asegúrate de ajustar la ruta del ejecutable de Blender según tu instalación).*

### 3. Iniciar el Servidor de Desarrollo
El lanzador de desarrollo detecta tu dirección IP local automáticamente para que puedas escanear el código QR directamente desde tu teléfono móvil:
```bash
cd moby_studio
python lanzador_ar.py
```

### 4. Habilitar Acceso en Dispositivos Móviles (HTTPS)
Dado que las APIs de cámara y reconocimiento de voz (`webkitSpeechRecognition` y `getUserMedia`) son **características seguras**, los navegadores móviles requieren obligatoriamente conectarse mediante una conexión segura **HTTPS**.
- Se recomienda exponer el puerto `8000` local usando una herramienta segura de túnel como **Cloudflare Tunnel** o **Ngrok**:
  ```bash
  ngrok http 8000
  ```
- Abre el enlace HTTPS generado en el navegador de tu dispositivo móvil y ¡comienza la aventura interactiva de Moby!

---

## 🌐 Hoja de Ruta: Despliegue en Equipo (Cloud Serverless)

Si deseas compartir este proyecto con un equipo de trabajo sin necesidad de que tu PC esté encendida ni de ejecutar Ollama localmente, sigue el plan de arquitectura detallado en [plan_despliegue_equipo.md](file:///C:/Users/ALEXANDER%20VILLALVA/.gemini/antigravity-cli/brain/f30c4d6f-7aaf-4a88-a5a6-32566be40f28/plan_despliegue_equipo.md):

1. **Hospedaje Web**: Despliega `index.html` y la carpeta `output` en **Vercel** o **Netlify** para un rendimiento global ultra rápido vía CDN.
2. **Backend Proxy Seguro**: Configura una función serverless en `/api/chat` en Node.js que mantenga segura tu clave de API sin exponerla en el navegador cliente.
3. **IA en la Nube**: Configura e inyecta la API Key de **Google Gemini API (modelo gemini-1.5-flash)** o **Groq Cloud API** para procesar miles de preguntas concurrentes del equipo al mismo tiempo de manera 100% independiente.

---

## 🐳 Créditos e Inspiración
Proyecto desarrollado con amor por el ecosistema DevOps y la educación interactiva 3D. ¡Dockerizar el mundo nunca fue tan divertido! 🚀⚓
