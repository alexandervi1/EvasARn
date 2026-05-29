# Mejoras pendientes

Este backlog queda ordenado por utilidad real despues de implementar el flujo AR target+contenido, proyectos, versionado, presencia, locks y sincronizacion por version.

## Implementado recientemente

- Exportacion ZIP con `index.html`, `layout.json`, assets usados, `manifest.json` y README.
- Modal AR con target fisico + contenido proyectado en un solo flujo.
- Contenido por subida local o URL directa para imagen, video y modelo.
- Nodos OIRA generados sin usar modelos base heredados.
- Plantillas OIRA1, OIRA2 y OIRA3 desde el editor.
- Contenidos OIRA con posicion relativa al target y narracion por clic.
- Cliente movil sin paneles de simulacion, salvo `?debugMarkers=1`.
- Proyectos guardados en `projects/<proyecto>/layout.json`.
- Versionado basico y conflicto `409` si se guarda una version vieja.
- Presencia de usuarios activos.
- Bloqueo temporal por objeto seleccionado.
- Sincronizacion por version: recarga si no hay cambios locales, aviso si hay cambios sin guardar.

## Siguientes mejoras por utilidad

1. Editor guiado de targets MindAR
   - Subir imagen target y explicar que debe entrenarse a `.mind`.
   - Asistente visual de estado: imagen fisica, QR, `.mind`, contenido asociado.
   - Previsualizacion del target dentro del modal.
   - Prueba rapida de camara con resultado claro: detectado/no detectado.

2. Inspector profesional de contenido AR
   - Ajustar ancho/alto de paneles de imagen y video.
   - Controles de autoplay, loop, volumen, orientacion y distancia al target.
   - Presets de panel flotante tipo Vision Pro: ficha, reproductor, galeria, CTA.
   - Vista de escala real aproximada sobre el target.

3. Optimizacion de assets 3D
   - Deteccion de modelos pesados.
   - Advertencias por texturas demasiado grandes.
   - Accion para comprimir GLB.
   - Recomendaciones de escala, poligonos y peso para telefono.

4. QA movil
   - Vista de simulacion iPhone dentro del editor.
   - Checklist separado para permisos de camara, HTTPS/LAN, MindAR y QR.
   - Logs visibles del cliente movil para depurar pruebas.
   - Prueba de performance: FPS aproximado, peso de escena y assets faltantes.

5. Colaboracion profesional
   - Roles: owner, editor, revisor, cliente solo lectura.
   - Comentarios o notas por objeto.
   - Estados: borrador, revision, listo para publicar, publicado.
   - Historial de publicaciones por fecha.
   - Duplicar, renombrar, archivar y restaurar proyectos.

6. Sincronizacion granular en vivo
   - Enviar patches de crear/mover/borrar/asignar sin esperar guardado completo.
   - WebSocket para cambios inmediatos.
   - Resolucion de conflictos por operacion o CRDT si se necesita edicion simultanea real.
   - Indicadores de cursor/seleccion en viewport.

7. OIRA avanzado
   - OCR real para palabras clave.
   - Reconocimiento de objetos entrenados.
   - Navegacion manual avanzada para pipeline OIRA3.
   - Secuencias guiadas con pasos y progreso.

8. Publicacion final
   - QR final de acceso por experiencia.
   - Pagina de entrega para cliente con instrucciones minimas.
   - Validacion avanzada del paquete en telefono antes de entregar.
