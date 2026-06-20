# Moby Studio

Moby Studio es una aplicacion local para crear, organizar y probar experiencias WebAR con tracking de imagen. Incluye un editor visual para escritorio, un visor movil basado en A-Frame y MindAR, gestion de proyectos y assets, y un servidor HTTP escrito con la biblioteca estandar de Python.

El flujo principal es:

```text
Crear proyecto -> configurar target -> subir .mind -> agregar contenido -> anclar -> validar -> guardar -> probar
```

## Nivel de preparacion y uso recomendado

Moby Studio esta listo para desarrollo, demostraciones y trabajo local por personas con conocimientos tecnicos basicos. **Todavia no es un producto de escritorio de instalacion inmediata ni un servicio preparado para exponerse directamente a Internet.**

| Escenario | Estado | Que necesita |
|---|---|---|
| Desarrollo en la misma PC | Listo | Python, navegador moderno y ejecutar el lanzador. |
| Trabajo en una red local confiable | Utilizable con precauciones | Ejecutar el servidor, registrar usuarios y limitar el acceso a la red confiable. |
| Prueba desde telefono | Requiere configuracion | URL HTTPS mediante tunel o servidor web seguro. |
| Usuario final sin conocimientos tecnicos | No listo | Falta instalador, lanzador de un clic y compilacion integrada de `.mind`. |
| Despliegue publico en Internet | No listo | Falta endurecimiento de autenticacion, autorizacion, sesiones, TLS y almacenamiento de produccion. |
| Uso completamente offline | No listo | A-Frame, MindAR y fuentes se cargan actualmente desde CDN. |

### Pasos obligatorios despues de descargar

1. Instalar Python 3 o usar un entorno virtual existente.
2. Ejecutar `python moby_studio\lanzador_ar.py`; abrir los HTML directamente desde el disco no es un flujo soportado.
3. Mantener conexion a Internet para que el navegador cargue A-Frame, MindAR y las fuentes externas.
4. Abrir el editor, crear o seleccionar un proyecto y **guardarlo al menos una vez**. Esto genera `moby_studio/output/layout.json`, requerido por el visor.
5. Generar externamente el archivo `.mind` de cada conjunto de targets y subirlo al proyecto.
6. Para usar la camara desde un telefono, publicar el puerto `8000` mediante HTTPS.
7. Validar la experiencia y probarla en los dispositivos reales antes de entregarla.

### Aviso sobre cuentas y seguridad

El repositorio incluye cuentas de desarrollo predeterminadas:

| Usuario | Contrasena | Rol |
|---|---|---|
| `admin` | `admin123` | Propietario |
| `viewer` | `viewer123` | Cliente |

En acceso desde la misma PC, el editor inicia automaticamente como administrador. Estas cuentas y el almacenamiento actual de usuarios en `projects/users.json` existen para desarrollo local y LAN confiable. **No deben considerarse credenciales seguras ni utilizarse para publicar el servidor directamente en Internet.** Antes de un despliegue real se debe reemplazar este sistema por autenticacion, sesiones, autorizacion por endpoint y almacenamiento de credenciales adecuados.

### Verificacion antes de entregar a otra persona

- No existe todavia una suite automatizada completa; realiza una prueba manual del flujo principal.
- Confirma que editor y visor respondan desde el servidor.
- Prueba el target fisico y su `.mind` en el navegador movil objetivo.
- Comprueba modelos, video y audio en el dispositivo real.
- Verifica el ZIP exportado y las instrucciones de acceso HTTPS.

## Funciones actuales

- Editor visual en `moby_studio/editor.html` con barra lateral compacta, lienzo A-Frame e inspector.
- Visor WebAR en `moby_studio/index.html` para escritorio y telefono.
- Tracking de imagen real con MindAR y archivos `.mind`.
- Plantillas `Marcador + Imagen`, `Marcador + Video`, `Marcador + Audio`, `Marcador + Modelo 3D` y `Boton interactivo`.
- Contenido 3D, imagen, video, audio espacial con ondas visuales y nodos informativos heredados.
- Botones interactivos con acciones configurables `next`, `previous`, `show`, `hide`, `toggle`, `play`, `pause` y `stop`, incluyendo botones 2D o modelos GLB personalizados.
- Seleccion directa en el lienzo con modo puntero y atajos de transformacion (`V`, `Q`, `W`, `E`, `R`).
- Mediateca con carga, filtros, asignacion, deteccion de uso y eliminacion protegida.
- Proyectos versionados con crear, duplicar, renombrar, archivar, restaurar y eliminar.
- Exportacion e importacion de proyectos editables entre PCs mediante ZIP.
- Exportacion de una experiencia autocontenida para entrega.
- Autosave local, Undo/Redo, presencia y bloqueo temporal de objetos.
- Registro e inicio de sesion para acceso remoto; en acceso local se usa el perfil administrador automatico.
- Validacion previa a publicacion y herramientas de QA movil.
- Compresion opcional de modelos GLB con Blender y Draco.

## Limitaciones actuales

- Moby Studio no compila imagenes a `.mind`; el archivo debe generarse externamente.
- Todos los targets de una escena deben pertenecer al mismo `.mind` y usar indices diferentes.
- La colaboracion sincroniza versiones guardadas y locks en memoria; no es edicion granular en tiempo real.
- El servidor es local. El acceso movil con camara normalmente requiere publicar el puerto `8000` mediante HTTPS.
- A-Frame, MindAR y las fuentes se cargan desde CDN, por lo que el primer uso requiere conexion a Internet.
- El audio depende de las restricciones del navegador; la experiencia esta pensada para controlarse con botones externos o por interaccion dentro de la escena.

## Requisitos

- Python 3 reciente.
- Navegador moderno con WebGL y acceso a camara.
- Git, si se instala desde el repositorio.
- Blender, solamente para la compresion Draco opcional.

El runtime base no necesita paquetes externos de Python. `requirements.txt` documenta esta condicion.

## Instalacion y ejecucion

```powershell
git clone https://github.com/alexandervi1/EvasARn.git
cd EvasARn
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe moby_studio\lanzador_ar.py
```

Tambien puede ejecutarse con un Python ya disponible:

```powershell
python moby_studio\lanzador_ar.py
```

El lanzador cambia internamente su directorio de trabajo a `moby_studio/`.

Abrir en el navegador:

- Editor: `http://localhost:8000/editor.html`
- Visor: `http://localhost:8000/index.html`
- Estado de assets: `http://localhost:8000/api/list-assets`

Para un telefono, expone `http://localhost:8000` mediante Cloudflare Tunnel, ngrok u otro proxy HTTPS. No guardes en la documentacion una URL temporal porque cambia al reiniciar el tunel.

## Flujo rapido

1. Abre el editor y selecciona o crea un proyecto.
2. En la barra izquierda, abre `Agregar contenido`.
3. Elige una plantilla AR.
4. Configura la imagen fisica del target y su archivo `.mind`.
5. Sube o selecciona el contenido desde la mediateca.
6. Si necesitas interaccion, crea un boton y asignale acciones a otro contenido de la escena.
7. Comprueba que el contenido este anclado al target correcto.
8. Ajusta posicion, rotacion y escala en el lienzo o inspector.
9. Abre `Validar`, corrige los errores y guarda.
10. Abre `Probar y publicar` o carga `index.html` directamente.
11. Inicia AR, concede permiso de camara y apunta al target fisico.

Consulta [TUTORIAL_PRIMEROS_PASOS.md](moby_studio/TUTORIAL_PRIMEROS_PASOS.md) para el recorrido detallado.

## Interfaz del editor

La barra de actividad izquierda separa las tareas principales y es la fuente unica de navegacion del editor:

| Seccion | Uso |
|---|---|
| Escena | Ver targets, contenido anclado y objetos de mesa base. |
| Agregar contenido | Crear plantillas, targets y recursos para la escena. |
| Recursos | Buscar, filtrar y administrar la mediateca. |
| Validar | Auditar targets, archivos, anclajes y estado de guardado. |
| Probar y publicar | Abrir validacion y QA movil, y exportar la experiencia. |
| Gestionar proyectos | Administrar y transferir proyectos. |
| Ayuda | Abrir el manual integrado. |

El lienzo central permite componer la escena y seleccionar objetos directamente sobre la interfaz. El inspector derecho contiene transformaciones, anclaje, archivo multimedia, interacciones, dimensiones y notas del objeto seleccionado. En pantallas estrechas los paneles se compactan para conservar el area de trabajo.

## Contenido soportado

| Extensiones | Clasificacion | Uso |
|---|---|---|
| `.glb`, `.gltf` | `model` | Modelos 3D. |
| `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` | `image` | Targets visuales e imagenes AR. |
| `.mp4`, `.webm`, `.mov` | `video` | Paneles de video AR. |
| `.mp3`, `.wav`, `.ogg`, `.m4a`, `.aac` | `audio` | Reproductor de audio AR. |
| `.mind` | `target` | Targets compilados de MindAR. |
| `.json` | `data` | Datos internos protegidos. |

Los recursos se guardan localmente en `moby_studio/output/`. Esta carpeta es runtime generado y no se versiona en Git.

## Targets MindAR

Un target usa estos campos principales:

- `markerImage`: imagen fisica de referencia.
- `mindTargetUrl`: ruta al archivo `.mind` compilado.
- `mindTargetIndex`: indice de la imagen dentro de ese `.mind`.
- `trackingMode: "image"`: modo de tracking activo.
- `recognitionKey`: identificador del target.

El contenido se vincula mediante `arAnchor`, que contiene el `uuid` del target. Si queda en `base`, pertenece a la mesa de composicion y no se activara como contenido de un marcador.

## Proyectos y archivos

```text
EvasARn/
|-- README.md
|-- requirements.txt
`-- moby_studio/
    |-- editor.html
    |-- index.html
    |-- lanzador_ar.py
    |-- ARCHITECTURE.md
    |-- TUTORIAL_PRIMEROS_PASOS.md
    |-- MEJORAS_PENDIENTES.md
    |-- scripts/
    |   `-- compress_model.py
    |-- projects/
    |   |-- default/layout.json
    |   `-- users.json
    |-- output/             # generado localmente
    `-- _archive/           # proyectos archivados localmente
```

Cada proyecto activo se guarda en `moby_studio/projects/<proyecto>/layout.json`. Al guardar, la app tambien actualiza `moby_studio/output/layout.json`, que es el layout cargado por el visor.

El proyecto `default` esta protegido. Los demas proyectos y `output/` se ignoran en Git.

## Transferencia y exportacion

Hay dos paquetes diferentes:

- **Exportar proyecto**: ZIP editable con manifiesto, layout y assets locales usados. Se importa desde `Gestionar proyectos` en otra PC.
- **Exportar experiencia**: entrega del visor y recursos necesarios para ejecutar la experiencia publicada.

La importacion de proyectos no sobrescribe proyectos existentes. Si un asset entrante tiene el mismo nombre y contenido diferente, se renombra y se actualizan sus referencias.

## API principal

| Endpoint | Metodo | Funcion |
|---|---:|---|
| `/api/save-layout?project=...&version=...` | POST | Guarda e incrementa la version del proyecto. |
| `/api/load-layout?project=...` | GET | Carga un proyecto. |
| `/api/list-projects` | GET | Lista proyectos activos. |
| `/api/list-archived-projects` | GET | Lista proyectos archivados. |
| `/api/duplicate-project` | POST | Duplica un proyecto. |
| `/api/rename-project` | POST | Renombra un proyecto. |
| `/api/archive-project` | POST | Archiva un proyecto. |
| `/api/restore-project` | POST | Restaura un proyecto. |
| `/api/delete-project` | POST | Elimina un proyecto excepto `default`. |
| `/api/export-project?project=...` | POST | Genera un ZIP editable. |
| `/api/import-project?name=...` | POST | Importa un ZIP editable como proyecto nuevo. |
| `/api/list-assets` | GET | Lista la mediateca y su uso. |
| `/api/upload-media?name=...` | POST | Sube un recurso multimedia. |
| `/api/upload-model?name=...` | POST | Sube GLB o GLTF. |
| `/api/delete-asset?name=...` | POST | Elimina un asset no protegido. |
| `/api/export-experience?name=...` | POST | Genera el paquete de experiencia. |
| `/api/compress-model` | POST | Comprime un GLB mediante Blender. |
| `/api/collab-heartbeat` | POST | Actualiza presencia y lock. |
| `/api/collab-release` | POST | Libera locks del usuario. |
| `/api/collab-state?project=...` | GET | Consulta colaboracion y version. |
| `/api/login` | POST | Inicia sesion remota. |
| `/api/register` | POST | Registra un usuario local del servidor. |
| `/api/connection-info` | GET | Informa IP y tipo de acceso. |

`/api/generate-model` se conserva solo como respuesta de compatibilidad y no genera modelos.

## Diagnostico

```powershell
python -m py_compile moby_studio\lanzador_ar.py
Invoke-WebRequest -UseBasicParsing http://localhost:8000/editor.html
Invoke-WebRequest -UseBasicParsing http://localhost:8000/index.html
git diff --check
```

Opciones del visor para QA:

- `?debugConsole=1`: muestra la consola visual.
- `?debugMarkers=1`: muestra ayudas de diagnostico de marcadores.

## Documentacion

- [Tutorial de primeros pasos](moby_studio/TUTORIAL_PRIMEROS_PASOS.md)
- [Arquitectura](moby_studio/ARCHITECTURE.md)
- [Mejoras pendientes](moby_studio/MEJORAS_PENDIENTES.md)
