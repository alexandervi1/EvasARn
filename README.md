# Moby Studio

Moby Studio es una aplicacion local para crear, editar y probar experiencias AR desde el navegador. Incluye un editor 3D, un cliente movil AR, gestion de assets, disparadores por QR o imagen entrenada, y un backend Python que guarda el layout y sirve los recursos desde `moby_studio/output/`.

## Estado Actual

La aplicacion ya incluye:

- **Estilo Inmersivo Vision Pro**: Interfaz de usuario con estética visionOS oscura, glassmorphic y moderna, incluyendo combo boxes personalizados con flechas chevron de alto contraste y animaciones de resplandor.
- **Iconografía Vectorial SVG (Editor PC)**: Reemplazo completo de emojis y caracteres unicode en outliner, listas de escena, validaciones e inspectores por SVGs lineales integrados (`stroke="currentColor"`) consistentes y dinámicos para una visualización ultra-nítida.
- **Tarjetas Stacked en Mediateca ("Mis Medios")**: Rediseño de tarjetas de assets a un diseño estructurado de dos filas (superior para miniatura e info; inferior para badges y botones de acción) que previene el amontonamiento horizontal. Utilidad `.no-scrollbar` para ocultar barras de scroll grises.
- **Optimización Draco al Click**: Compresión de mallas Draco para modelos 3D integrada en el editor y accesible con un botón vectorial rápido en la mediateca.
- **Iconografía Móvil SVG (Cliente Teléfono)**: Visor móvil (`index.html`) con botones de acciones rápidas, dock inferior y controles AR actualizados a SVGs nativos para un tacto premium.
- Editor 3D en `moby_studio/editor.html`.
- Cliente AR/movil en `moby_studio/index.html`.
- Backend local en `moby_studio/lanzador_ar.py`.
- Persistencia de escena en `moby_studio/output/layout.json`.
- Proyectos guardados por nombre en `moby_studio/projects/<proyecto>/layout.json`.
- Versionado basico por proyecto para evitar sobrescrituras.
- Presencia colaborativa, nombre de usuario y bloqueo temporal por objeto.
- Sincronizacion remota por version: recarga automatica si no hay cambios locales.
- Mediateca profesional para modelos, imagenes, videos y targets `.mind`.
- Autosave local y recuperacion de borradores.
- Undo/Redo real por snapshots de escena.
- Validador de publicacion.
- Soporte para QR y MindAR.
- Flujo AR target fisico + contenido proyectado desde el mismo modal.
- Contenido por archivo local o URL directa para imagen, video y GLB/GLTF.
- Nodos OIRA generados sin depender de modelos base heredados.
- Cliente movil con controles compactos para telefono.
- Integracion opcional de vision local con YOLOv8 y Ollama.

## Estructura Del Proyecto

```text
mcpBlender/
├── README.md
├── medios/
│   └── image.png
└── moby_studio/
    ├── ARCHITECTURE.md
    ├── MEJORAS_PENDIENTES.md
    ├── editor.html
    ├── index.html
    ├── lanzador_ar.py
    ├── output/
    │   ├── layout.json
    │   ├── *.glb
    │   ├── *.png / *.jpg / *.webp
    │   ├── *.mp4 / *.webm
    │   └── *.mind
    ├── projects/
    │   └── <proyecto>/
    │       └── layout.json
    ├── scripts/
    ├── vision/
    └── venv/
```

## Como Ejecutar

Desde la raiz del proyecto:

```powershell
cd moby_studio
.\venv\Scripts\python.exe lanzador_ar.py
```

Luego abre:

- Editor: `http://localhost:8000/editor.html`
- Cliente AR: `http://localhost:8000/index.html`
- API assets: `http://localhost:8000/api/list-assets`

Para probar desde telefono, usa la URL LAN que imprime el servidor. Si el navegador movil bloquea la camara, expone el puerto con HTTPS usando una herramienta como ngrok o Cloudflare Tunnel.

## Editor 3D

El editor permite:

- Crear modelos 3D, imagenes, videos y marcadores AR.
- Crear experiencias AR rapidas: marcador + imagen, marcador + video y plantillas OIRA.
- Configurar en un mismo modal el target fisico que se imprime o muestra en la vida real y el contenido que se proyecta encima.
- Asociar contenido a un marcador mediante `arAnchor`.
- Pegar una URL directa o subir un archivo local para imagenes, videos y modelos.
- Editar posicion, rotacion y escala con sliders, inputs numericos y gizmo 3D.
- Bloquear, ocultar, duplicar y seleccionar objetos desde el outliner.
- Validar si una escena esta lista para probar en telefono.
- Guardar por proyecto con versionado.
- Ver usuarios activos y objetos que otra persona esta editando.

## Proyectos Y Colaboracion

El editor trabaja sobre un proyecto activo. Cada proyecto se guarda en:

```text
moby_studio/projects/<proyecto>/layout.json
```

Al guardar, el servidor tambien actualiza `moby_studio/output/layout.json` para mantener compatibilidad con el cliente final y la exportacion.

Funciones actuales:

- Selector de proyecto en la barra superior.
- Creacion rapida de nuevos proyectos.
- Version incremental por proyecto.
- Conflicto `409` si alguien intenta guardar una version vieja.
- Nombre de usuario local por navegador.
- Presencia de usuarios activos.
- Bloqueo temporal del objeto seleccionado por otro usuario.
- Aviso de version remota disponible.
- Recarga automatica cuando otra persona guarda y el editor local no tiene cambios sin guardar.

## Disparadores AR

Los marcadores AR son entidades normales con `isMarker: true`. Pueden configurarse con:

- `trackingMode: "qr"` y `recognitionKey` para QR / BarcodeDetector.
- `trackingMode: "image"` y `mindTargetUrl` para targets MindAR `.mind`.
- `markerImage` para la textura visual del target dentro del editor.

El contenido asociado guarda `arAnchor` con el UUID del marcador.

Flujo recomendado:

1. Presiona `Marcador + Imagen` o `Marcador + Video`.
2. En `Target fisico`, sube la imagen/QR/icono que se va a imprimir o mostrar en una tarjeta.
3. En `Reconocimiento`, usa QR o MindAR.
4. En `Contenido flotante`, sube un archivo local o pega una URL directa.
5. Guarda. En telefono, al detectar el target, el contenido aparece encima.

Para video, el link debe apuntar directo al archivo (`.mp4` o `.webm`). Un enlace normal de YouTube/Vimeo no funciona como textura AR directa.

## Cliente Movil

`index.html` carga `output/layout.json` y reconstruye la experiencia AR. En telefono prioriza:

- Interfaz compacta.
- Dock de acciones.
- Escaneo de QR si `BarcodeDetector` esta disponible.
- Soporte para MindAR cuando el marcador tiene `.mind`.
- Paneles espaciales flotantes para imagenes y videos.
- Nodos OIRA flotantes generados desde datos del layout.
- Contenido oculto hasta detectar el target asociado.
- Ocultar paneles de simulacion de marcadores en telefono, salvo `?debugMarkers=1`.

## Mediateca

La mediateca del editor usa `/api/list-assets` para listar recursos de `output/`:

- Modelos `.glb` / `.gltf`.
- Imagenes `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`.
- Videos `.mp4`, `.webm`, `.mov`.
- Targets `.mind`.
- Datos `.json`.

Funciones disponibles:

- Buscar assets.
- Filtrar por tipo.
- Filtrar assets sin uso.
- Ver previews de imagen y video.
- Ver si un asset esta usado por el layout.
- Subir nuevos assets.
- Agregar assets a la escena.
- Asignar assets al objeto seleccionado.
- Copiar rutas.
- Eliminar assets no protegidos.

`layout.json` esta protegido y no se puede eliminar desde la mediateca.

## Autosave Y Undo/Redo

El editor guarda borradores locales en `localStorage` mientras hay cambios sin guardar. Al abrir el editor, si existe un borrador local no publicado, muestra un banner para restaurarlo o descartarlo.

Undo/Redo usa snapshots completos de escena y cubre:

- Crear, borrar y duplicar objetos.
- Configurar AR.
- Asignar assets.
- Cambiar transformaciones.
- Cambiar anclajes.
- Ocultar, mostrar, bloquear y desbloquear.
- Cambiar escenario y rejilla.
- Restaurar borradores.

Atajos:

- `Ctrl+Z`: deshacer.
- `Ctrl+Y`: rehacer.
- `Ctrl+Shift+Z`: rehacer.

## API Principal

| Endpoint | Metodo | Descripcion |
|---|---:|---|
| `/api/save-layout?project=...&version=...` | POST | Guarda el proyecto versionado y actualiza `output/layout.json`. |
| `/api/list-projects` | GET | Lista proyectos guardados, version y cantidad de entidades. |
| `/api/load-layout?project=...` | GET | Carga el layout de un proyecto. |
| `/api/collab-heartbeat` | POST | Registra usuario activo, seleccion y lock temporal. |
| `/api/collab-release` | POST | Libera locks del usuario. |
| `/api/collab-state?project=...` | GET | Devuelve usuarios, locks y version remota. |
| `/api/list-assets` | GET | Lista todos los assets de `output/` con tipo, tamano, uso y proteccion. |
| `/api/delete-asset?name=...` | POST | Elimina un asset no protegido de `output/`. |
| `/api/export-experience?name=...` | POST | Genera un ZIP con `index.html`, `layout.json`, assets usados, manifiesto y README. |
| `/api/list-models` | GET | Lista modelos GLB/GLTF para compatibilidad. |
| `/api/upload-media?name=...` | POST | Sube cualquier recurso multimedia permitido. |
| `/api/upload-model?name=...` | POST | Sube modelos GLB/GLTF. |
| `/api/delete-model?name=...` | POST | Elimina modelos GLB/GLTF. |
| `/api/generate-qr?text=...&name=...` | POST | Genera un QR PNG en `output/`. |
| `/api/generate-model?script=...` | POST | Ejecuta Blender headless con un script procedural. |
| `/api/compress-model` | POST | Ejecuta compresion de modelo con Blender. |
| `/api/vision` | POST | Analiza un frame base64 con YOLOv8 y Ollama local. |

## Datos De Layout

Formato actual:

```json
{
  "project": "default",
  "version": 2,
  "updatedAt": "2026-05-29 15:03:57",
  "stage": {
    "width": 3,
    "height": 3,
    "gridVisible": true
  },
  "entities": [
    {
      "uuid": "objeto-marcador-1",
      "nombre": "Target Producto",
      "isMarker": true,
      "posicion": { "x": 0, "y": 0.02, "z": -3.5 },
      "rotacion": { "y": 0 },
      "escala": 1,
      "markerImage": "output/qr_presentacion.png",
      "recognitionKey": "objeto-marcador-1",
      "trackingMode": "qr",
      "mindTargetUrl": null,
      "mindTargetIndex": 0,
      "arAnchor": "base"
    },
    {
      "uuid": "objeto-panel-2",
      "nombre": "Panel explicativo",
      "mediaType": "image",
      "mediaUrl": "output/panel.png",
      "posicion": { "x": 0, "y": 0.55, "z": 0.05 },
      "rotacion": { "y": 0 },
      "escala": 1,
      "relativeToAnchor": true,
      "arAnchor": "objeto-marcador-1"
    }
  ]
}
```

## Backlog

Las mejoras pendientes estan documentadas en:

`moby_studio/MEJORAS_PENDIENTES.md`

Ese archivo contiene el orden sugerido para continuar: editor guiado de targets MindAR, inspector avanzado de contenido, optimizacion de assets, QA movil, roles/comentarios y sincronizacion mas granular.
