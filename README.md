# Moby Studio

Moby Studio es un editor local para crear, guardar y probar experiencias WebAR con tracking por imagen usando MindAR. El proyecto incluye un editor 3D para PC, un visor final para telefono, gestion de assets, proyectos versionados, exportacion de experiencias y un backend Python que sirve la aplicacion desde `moby_studio/`.

El objetivo actual es trabajar como un flujo tipo Vuforia, pero ejecutado en navegador:

```text
Crear target -> subir imagen fisica -> subir .mind -> agregar contenido -> anclar -> validar -> probar en telefono
```

## Estado Actual

Implementado:

- Editor 3D en `moby_studio/editor.html`.
- Visor WebAR/MindAR en `moby_studio/index.html`.
- Backend local en `moby_studio/lanzador_ar.py`.
- Servidor HTTP threaded en el puerto `8000`.
- Proyectos versionados en `moby_studio/projects/<proyecto>/layout.json`.
- Runtime activo en `moby_studio/output/layout.json`.
- Mediateca para modelos, imagenes, videos y targets `.mind`.
- Targets MindAR con `markerImage`, `mindTargetUrl` y `mindTargetIndex`.
- Contenido AR anclado a targets mediante `arAnchor`.
- Validador de publicacion orientado a MindAR.
- Exportacion ZIP de experiencia.
- Autosave local, Undo/Redo y bloqueo temporal por objeto.
- Manual de ayuda integrado en el editor y en el visor.
- Paneles laterales del editor pulidos para guiar el flujo `Target -> Assets -> Anclar -> Probar`.
- Plantilla principal `Marcador + Modelo 3D` para crear una experiencia AR funcional sin pasos de demo.
- Gestion de proyectos con crear, duplicar, renombrar, archivar, restaurar y eliminar.
- Visor simplificado: solo muestra controles necesarios para AR; chatbot y acciones extra se habilitan desde el editor.
- Compresion Draco de modelos GLB usando Blender mediante `scripts/compress_model.py`.

Retirado o no principal:

- Los generadores procedurales antiguos de modelos 3D fueron eliminados.
- Las plantillas `OIRA 1`, `OIRA 2` y `OIRA 3` fueron retiradas del flujo principal.
- El `Banco 3D` ya no aparece como paso principal; queda como busqueda externa opcional desde `Importar GLB`.
- La carpeta legacy de `dataset/` y vision local anterior ya no forma parte del flujo.
- `/api/generate-model` queda retirado y responde como endpoint obsoleto.
- `/api/vision`, Ollama y Gemma fueron retirados del runtime porque generaban errores y no aportaban al tracking AR.
- QR, BarcodeDetector y simulaciones fueron retirados del flujo AR principal.
- La compilacion local de `.mind` todavia esta pendiente; por ahora se suben archivos `.mind` ya generados.

## Estructura

```text
mcpBlender/
├── README.md
├── medios/
└── moby_studio/
    ├── ARCHITECTURE.md
    ├── MEJORAS_PENDIENTES.md
    ├── editor.html
    ├── index.html
    ├── lanzador_ar.py
    ├── output/
    │   ├── layout.json
    │   ├── *.glb / *.gltf
    │   ├── *.png / *.jpg / *.webp / *.gif
    │   ├── *.mp4 / *.webm / *.mov
    │   └── *.mind
    ├── projects/
    │   └── <proyecto>/
    │       └── layout.json
    ├── scripts/
    │   └── compress_model.py
    └── venv/
```

## Ejecucion Local

Primera instalacion despues de clonar:

```powershell
cd C:\Users\ALEXANDER VILLALVA\Desktop\mcpBlender
python -m venv moby_studio\venv
.\moby_studio\venv\Scripts\python.exe -m pip install --upgrade pip
.\moby_studio\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Desde PowerShell:

```powershell
cd C:\Users\ALEXANDER VILLALVA\Desktop\mcpBlender\moby_studio
.\venv\Scripts\python.exe lanzador_ar.py
```

Abrir:

- Editor: `http://localhost:8000/editor.html`
- Visor final: `http://localhost:8000/index.html`
- Assets: `http://localhost:8000/api/list-assets`

Para probar en telefono se necesita una URL HTTPS. Puedes usar Cloudflare Tunnel, ngrok u otra herramienta equivalente apuntando al puerto `8000`. La camara movil suele fallar si se abre por HTTP normal.

Dependencias externas opcionales:

- Blender: necesario solo para comprimir GLB con Draco desde `/api/compress-model`.

## Flujo Recomendado

1. Abre `editor.html`.
2. Crea o selecciona un proyecto.
3. En `Crear > Flujo AR`, crea un `Marcador AR`.
4. Configura el target:
   - sube la imagen fisica que se va a imprimir o mostrar;
   - sube el archivo `.mind`;
   - define `mindTargetIndex` si el `.mind` contiene varios targets.
5. Sube o selecciona contenido:
   - modelo `.glb` / `.gltf`;
   - imagen;
   - video.
6. Ancla el contenido al target desde el inspector derecho.
7. Ajusta posicion, escala y rotacion en el lienzo.
8. Abre `Publicar` y ejecuta la validacion.
9. Guarda.
10. Abre `index.html` en PC o telefono y prueba la deteccion real.

## Editor

El editor es la herramienta de autoria para PC. Sus zonas principales son:

- Panel izquierdo:
  - `Escena`: outliner de targets, contenido anclado y objetos de mesa base.
  - `Crear`: flujo AR, plantilla `Marcador + Modelo 3D`, target MindAR, importar GLB, modelos externos opcionales y mediateca.
  - `Publicar`: validacion, exportacion y QA movil.
- Lienzo central:
  - taller de composicion AR;
  - superficie de referencia del target;
  - guias MindAR;
  - transform toolbar para orbitar, mover, rotar, escalar y borrar.
- Inspector derecho:
  - estado del objeto seleccionado;
  - tipo, estado AR, target y archivo;
  - nombre, transformacion, anclaje y configuracion AR;
  - dimensiones de paneles de imagen/video;
  - comentarios y notas;
  - acciones rapidas como duplicar y resetear transformacion.

El icono `?` de la barra superior abre el manual interno del editor.

## Visor Final

`index.html` carga `output/layout.json` y reconstruye la experiencia final.

Funciones principales:

- Activar camara RA.
- Cargar MindAR cuando hay targets con `.mind`.
- Mostrar contenido al detectar `targetFound`.
- Ocultar contenido con `targetLost`.
- Reproducir contenido de video con audio cuando el navegador lo permite tras interaccion del usuario.
- Ajustar escala y distancia del contenido desde controles flotantes.
- Entrar en modo presentacion.
- Mostrar chatbot, voz/texto y analisis de camara solo si `stage.viewer.chatEnabled` esta habilitado desde el editor.

El visor tambien tiene un icono de ayuda con instrucciones de uso y problemas comunes.

## MindAR

Reglas importantes:

- El reconocimiento ocurre en el navegador con `mind-ar`.
- El archivo `.mind` debe estar servido por HTTP/HTTPS.
- Una escena MindAR usa un `imageTargetSrc`.
- Si hay varios targets, deben estar compilados dentro del mismo `.mind`.
- Cada target usa `mindTargetIndex` para decidir que imagen del `.mind` lo activa.
- El contenido se vincula al target con `arAnchor`.

Estado de un target:

- Falta imagen fisica.
- Falta archivo `.mind`.
- Target listo.
- Contenido sin target.
- Contenido anclado listo.

## Mediateca

La mediateca lista recursos desde `moby_studio/output/` mediante `/api/list-assets`.

Tipos soportados:

| Extension | Tipo |
|---|---|
| `.glb`, `.gltf` | Modelo 3D |
| `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` | Imagen |
| `.mp4`, `.webm`, `.mov` | Video |
| `.mind` | Target MindAR |
| `.json` | Datos |

Funciones:

- Subir assets.
- Buscar y filtrar por tipo.
- Ver si un asset esta en uso.
- Agregar modelos, imagenes o videos a la escena.
- Asignar `.mind` al target seleccionado.
- Comprimir GLB con Draco.
- Copiar rutas.
- Eliminar assets no protegidos.

`layout.json` esta protegido.

## Proyectos Y Colaboracion

Cada proyecto se guarda en:

```text
moby_studio/projects/<proyecto>/layout.json
```

Al guardar, tambien se actualiza:

```text
moby_studio/output/layout.json
```

Caracteristicas:

- Selector de proyecto.
- Crear, duplicar, renombrar, archivar, restaurar y eliminar proyectos.
- El proyecto `default` queda protegido para tener siempre una base limpia de trabajo.
- Version incremental por proyecto.
- Conflicto `409` si se intenta guardar sobre una version antigua.
- Usuario local por navegador.
- Presencia colaborativa.
- Lock temporal del objeto seleccionado.
- Aviso de version remota disponible.
- Sincronizacion al guardar, no edicion granular en tiempo real.

## API Principal

| Endpoint | Metodo | Uso |
|---|---:|---|
| `/api/save-layout?project=...&version=...` | POST | Guarda proyecto versionado y actualiza `output/layout.json`. |
| `/api/load-layout?project=...` | GET | Carga un proyecto. |
| `/api/list-projects` | GET | Lista proyectos activos. |
| `/api/list-archived-projects` | GET | Lista proyectos archivados. |
| `/api/duplicate-project` | POST | Duplica proyecto. |
| `/api/rename-project` | POST | Renombra proyecto. |
| `/api/archive-project` | POST | Archiva proyecto. |
| `/api/restore-project` | POST | Restaura proyecto archivado. |
| `/api/delete-project` | POST | Elimina permanentemente un proyecto activo o archivado, excepto `default`. |
| `/api/collab-heartbeat` | POST | Registra presencia y lock temporal. |
| `/api/collab-release` | POST | Libera locks del usuario. |
| `/api/collab-state?project=...` | GET | Devuelve usuarios, locks y version remota. |
| `/api/list-assets` | GET | Lista assets de `output/`. |
| `/api/upload-media?name=...` | POST | Sube imagen, video, `.mind` u otro recurso permitido. |
| `/api/upload-model?name=...` | POST | Sube GLB/GLTF. |
| `/api/delete-asset?name=...` | POST | Elimina asset no protegido. |
| `/api/delete-model?name=...` | POST | Elimina modelo. |
| `/api/list-models` | GET | Lista modelos para compatibilidad. |
| `/api/export-experience?name=...` | POST | Genera ZIP de experiencia. |
| `/api/compress-model` | POST | Comprime GLB con Blender/Draco. |
| `/api/generate-model?script=...` | POST | Retirado; generacion procedural eliminada. |
| `/api/connection-info` | GET | Devuelve informacion de conexion local. |

## Layout

Ejemplo minimo:

```json
{
  "project": "default",
  "version": 3,
  "stage": {
    "width": 3,
    "height": 3,
    "gridVisible": true
  },
  "entities": [
    {
      "uuid": "target-1",
      "nombre": "Target Producto",
      "isMarker": true,
      "posicion": { "x": 0, "y": 0.02, "z": -2.5 },
      "rotacion": { "y": 0 },
      "escala": 1,
      "markerImage": "output/target-producto.png",
      "recognitionKey": "target-1",
      "trackingMode": "image",
      "mindTargetUrl": "output/target-producto.mind",
      "mindTargetIndex": 0,
      "arAnchor": "base"
    },
    {
      "uuid": "contenido-1",
      "nombre": "Panel Producto",
      "mediaType": "image",
      "mediaUrl": "output/panel-producto.png",
      "posicion": { "x": 0, "y": 0.55, "z": 0.05 },
      "rotacion": { "y": 0 },
      "escala": 1,
      "relativeToAnchor": true,
      "arAnchor": "target-1"
    }
  ],
  "updatedAt": "2026-05-30 16:10:00"
}
```

## Comandos Utiles

Validar backend:

```powershell
python -m py_compile moby_studio/lanzador_ar.py
```

Validar servidor local:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/editor.html
Invoke-WebRequest -UseBasicParsing http://localhost:8000/index.html
```

Revisar cambios:

```powershell
git status --short
git diff --check
```

## Pendientes Principales

La lista completa esta en `moby_studio/MEJORAS_PENDIENTES.md`.

Prioridad actual:

1. Probar ciclo completo con target real.
2. Implementar asistente/compilador local de targets `.mind`.
3. Refinar publicacion profesional para cliente.
4. Validar experiencia en telefono por HTTPS.
5. Limpiar compatibilidad OIRA interna restante.

## Documentacion Relacionada

- `moby_studio/ARCHITECTURE.md`: arquitectura interna.
- `moby_studio/MEJORAS_PENDIENTES.md`: contexto para continuar el desarrollo.
- Manual interno del editor: boton `?` en `editor.html`.
- Manual interno del visor: boton `Ayuda` o `?` en `index.html`.
