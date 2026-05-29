# Mejoras pendientes

Este backlog queda ordenado por utilidad real despues de implementar el flujo AR target+contenido, proyectos, versionado, presencia, locks y sincronizacion por version.

## Implementado recientemente

- Colaboración profesional (Roles: owner, editor, revisor, cliente solo lectura; comentarios o notas flotantes e interactivos por objeto en A-Frame y el inspector; estados de flujo de trabajo: borrador, revisión, listo, publicado con historial y logs; y APIs de duplicado, renombrado, archivado y restauración de proyectos).
- QA Móvil y Consola de Depuración (Simulador de iPhone X con Dynamic Island integrado en el editor, consola flotante de logs transparente en tiempo real en index.html, checklists automáticos de compatibilidad LAN/HTTPS, y estimador de rendimiento de FPS y peso en bytes).
- Optimización de assets 3D (Detección de peso de modelos GLB, insignias visuales dinámicas de advertencia "⚠️ Pesado" o "✓ Ligero", y botón de compresión Draco con Blender optimizado para cualquier modelo en el servidor).
- Editor guiado de targets MindAR (Asistente visual de estado, radar láser de escaneo, visor de cámara web y escáner jsQR integrado).
- Inspector profesional de contenido AR (Ajustes de ancho/alto dinámicos, presets estilo Vision Pro, estimación métrica física de escala real, y propiedades Loop, Autoplay y Mute de video).
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
