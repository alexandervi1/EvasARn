# Mejoras pendientes

Este documento deja el contexto actual del proyecto para poder continuar aunque se cierre la sesion.

## Prompt para continuar despues

Continuar el proyecto `mcpBlender / Moby Studio` desde este contexto:

Estamos convirtiendo Moby Studio en un editor y visor WebAR profesional tipo Vuforia, pero usando MindAR en navegador. La decision tecnica actual es separar claramente dos sistemas:

- El AR real y obligatorio funciona con MindAR: imagen fisica entrenada, archivo `.mind`, `mindTargetIndex` y contenido anclado al target.
- La vision IA con Ollama/Gemma (`/api/vision`) es solo una herramienta opcional de "Analizar Camara". No debe bloquear publicacion, tracking ni experiencia AR.

No volver al flujo antiguo de QR/BarcodeDetector/simulacion como sistema principal. El acceso al visor debe resolverse con URL HTTPS o instrucciones de publicacion, no con QR dentro del runtime.

Estado actual importante:

- `editor.html` ya esta orientado a targets MindAR.
- `index.html` ya esta limpiado para presentarse como visor WebAR/MindAR.
- Se oculto la consola debug salvo `?debugConsole=1`.
- El simulador visual de marcadores solo aparece con `?debugMarkers=1`.
- `/api/vision` ya fue corregido para `gemma4:e2b` usando `"think": false`.
- `localhost:8000/api/vision` y el tunel Cloudflare funcionaron despues del arreglo.
- El servidor se ejecuta con `moby_studio/venv/Scripts/python.exe lanzador_ar.py` desde la carpeta `moby_studio`.

Lo siguiente que toca hacer:

1. Mejorar la zona de trabajo del editor.
   - El lienzo debe sentirse como taller de composicion AR.
   - El target debe verse como superficie fisica de referencia.
   - El contenido debe poder acomodarse claramente encima del target.
   - Si un contenido no esta anclado a un target, debe verse como incompleto.

2. Probar ciclo real con target.
   - Subir imagen fisica.
   - Compilar `.mind`.
   - Subir `.mind`.
   - Anclar contenido.
   - Probar en `index.html` por localhost y Cloudflare HTTPS.

3. Refinar publicacion profesional.
   - La publicacion debe validar MindAR, no vision IA.
   - Generar entrega clara para cliente: target imprimible, URL, instrucciones y checklist.

4. Mantener vision IA como modulo opcional.
   - El boton "Analizar Camara" debe funcionar si Ollama esta activo.
   - Si falla, mostrar error claro sin romper AR.
   - No mezclar vision IA con deteccion del target.

5. Limpiar legado restante.
   - Evitar textos de Docker/demo si no aportan al visor final.

Cuando retomes, empieza revisando:

```powershell
git status --short
python -m py_compile moby_studio/lanzador_ar.py
git diff --check
Invoke-WebRequest -UseBasicParsing http://localhost:8000/index.html
Invoke-WebRequest -UseBasicParsing http://localhost:8000/editor.html
```

Si el servidor no esta activo:

```powershell
cd C:\Users\ALEXANDER VILLALVA\Desktop\mcpBlender\moby_studio
.\venv\Scripts\python.exe lanzador_ar.py
```

Si la vision IA falla, comprobar primero:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:11434/api/tags
```

Debe existir `gemma4:e2b`. El backend ya manda `"think": false`; no quitar eso.

## Contexto actual

Moby Studio debe funcionar como un editor WebAR tipo Vuforia usando tracking por imagen entrenada con MindAR. El flujo principal ya no debe depender de QR, BarcodeDetector ni simulaciones falsas de deteccion.

El flujo esperado es:

1. En el editor se crea un target AR.
2. El target tiene una imagen fisica imprimible.
3. Esa imagen debe convertirse en un target entrenado `.mind`; la compilacion local queda como modulo pendiente.
4. El `.mind` se sube al editor y se asigna al target.
5. El contenido AR se ancla a ese target.
6. En `index.html`, MindAR detecta la imagen real con la camara y muestra el contenido.

La zona de trabajo del editor es el taller de composicion: ahi se colocan, escalan y rotan target y contenido. La deteccion real ocurre en el visor final, no en el lienzo del editor.

## Estado implementado

- `index.html` usa MindAR como flujo principal para targets con `trackingMode: "image"` y `mindTargetUrl`.
- Se quitaron rutas activas de QR, BarcodeDetector y simulacion como camino principal del visor.
- El visor final avisa si falta el archivo `.mind`.
- El visor final bloquea el flujo si hay varios `.mind` distintos; MindAR debe usar un solo archivo `.mind` por escena y varios indices cuando hay varios targets.
- El editor crea targets nuevos con `trackingMode: "image"`, `mindTargetUrl: null` y `mindTargetIndex: 0`.
- El modal AR ahora guia imagen fisica + `.mind` + contenido anclado.
- La opcion de generar QR fue retirada del editor.
- La prueba de camara del editor ya no simula deteccion exitosa; solo sirve como apoyo visual y estado de configuracion.
- La vista final y la exportacion se bloquean si la escena MindAR no esta lista.
- La mediateca reconoce assets tipo `target` para archivos `.mind`.
- La mediateca tiene filtro visible `Targets`.
- Los archivos `.mind` se asignan a un target seleccionado; no se agregan como objetos sueltos a la escena.
- El buscador de Poly Pizza fue corregido para llamar a `buscarEnPolyPizza()`.
- La API de vision fue ajustada con timeout mas largo y mas tokens para respuestas de Gemma/Ollama.

## Pruebas realizadas

- `python -m py_compile moby_studio/lanzador_ar.py`
- Validacion de sintaxis JavaScript embebida de `editor.html` con Node.
- `git diff --check`
- `http://localhost:8000/editor.html` responde `200 OK`.
- `http://localhost:8000/index.html` responde `200 OK`.
- El tunel Cloudflare usado en esta sesion fue `https://lodging-won-dressing-color.trycloudflare.com`.
- `editor.html` por ese tunel respondio `200 OK`.
- `index.html` por ese tunel respondio `200 OK`.
- `/api/vision` funciono por localhost y por Cloudflare.

Nota: los tuneles rapidos de Cloudflare pueden cambiar de URL al reiniciarse. Al retomar, verificar la URL activa antes de probar en telefono.

## Pendientes prioritarios

1. Probar el ciclo completo con un target real
   - Subir una imagen fisica al target.
   - Compilarla en `.mind`.
   - Subir el `.mind`.
   - Asignar contenido 3D, imagen o video.
   - Abrir `index.html` por localhost o Cloudflare HTTPS.
   - Apuntar la camara al target impreso o mostrado en otra pantalla.

2. Mejorar la zona de trabajo del editor
   - Mostrar claramente el target como superficie fisica de referencia.
   - Añadir guias visuales de anclaje para contenido encima del target.
   - Separar mejor "Mesa / sin disparador" de contenido listo para AR.
   - Hacer que mover, rotar y escalar contenido sea mas evidente en relacion al target.
   - Mostrar advertencias visuales si un contenido no esta anclado a ningun target.

3. Mejorar el asistente de targets
   - Mostrar estado por target: falta imagen, falta `.mind`, falta contenido, listo.
   - Explicar cuando usar `mindTargetIndex`.
   - Advertir si dos targets usan el mismo indice.
   - Implementar compilacion local de uno o varios targets dentro de un solo `.mind`.

4. Prueba movil real
   - Probar en telefono con Cloudflare HTTPS.
   - Verificar permisos de camara.
   - Verificar que MindAR cargue el `.mind` sin errores CORS.
   - Medir tiempo de deteccion y estabilidad.
   - Ajustar escala/posicion inicial del contenido segun resultado real.

5. Publicacion profesional
   - Generar una pagina de entrega para cliente con instrucciones minimas.
   - Incluir target imprimible, URL del visor y checklist de compatibilidad.
   - Validar paquete exportado en telefono antes de entregar.

7. OIRA avanzado
   - OCR real para palabras clave.
   - Reconocimiento de objetos entrenados.
   - Navegacion manual avanzada para pipeline OIRA3.
   - Secuencias guiadas con pasos y progreso.

8. Sincronizacion granular en vivo
   - Enviar patches de crear, mover, borrar y asignar sin guardar layout completo.
   - WebSocket para cambios inmediatos.
   - Indicadores de cursor y seleccion en viewport.
   - Resolver conflictos por operacion si hay edicion simultanea real.

## Archivos clave

- `moby_studio/editor.html`: editor 3D, modal AR, mediateca, validacion de publicacion y exportacion.
- `moby_studio/index.html`: visor final WebAR con MindAR y llamada a vision.
- `moby_studio/lanzador_ar.py`: servidor local, APIs, subida de assets, vision, proyectos y exportacion.
- `moby_studio/output/layout.json`: layout activo servido al visor.
- `moby_studio/projects/default/layout.json`: proyecto default.
- `README.md`: documentacion general.
- `moby_studio/ARCHITECTURE.md`: arquitectura del sistema.

## Recordatorio de arquitectura MindAR

MindAR no funciona igual que Vuforia Cloud Recognition. En esta version:

- El reconocimiento ocurre en el navegador usando `mind-ar`.
- El archivo `.mind` debe estar disponible por HTTP/HTTPS.
- Una escena MindAR usa un `imageTargetSrc`.
- Si hay varios targets, deben estar compilados dentro del mismo `.mind`.
- Cada marcador usa `mindTargetIndex` para decidir que imagen del `.mind` lo activa.
- El contenido se muestra cuando MindAR dispara `targetFound` y se oculta con `targetLost`.

## Comandos utiles al retomar

```powershell
cd C:\Users\ALEXANDER VILLALVA\Desktop\mcpBlender
python -m py_compile moby_studio/lanzador_ar.py
git diff --check
Invoke-WebRequest -UseBasicParsing http://localhost:8000/editor.html
Invoke-WebRequest -UseBasicParsing http://localhost:8000/index.html
```
