# Mejoras pendientes

Backlog vigente de Moby Studio. Este archivo contiene trabajo no implementado; las funciones terminadas se documentan en `README.md` y `ARCHITECTURE.md`.

## Prioridad 1: prueba AR real

- Ejecutar un ciclo completo con target impreso, `.mind` y cada tipo de contenido.
- Probar imagen, video, audio y GLB en Android e iOS compatibles.
- Medir tiempo de deteccion, estabilidad de `targetFound/targetLost` y consumo de memoria.
- Verificar autoplay, recuperacion de audio y pausa al perder el target.
- Definir una matriz de navegadores y dispositivos soportados.

## Prioridad 2: compilacion de targets

- Integrar un asistente para compilar una o varias imagenes en un unico `.mind`.
- Mostrar calidad estimada del target antes de compilar.
- Mantener el orden de imagenes y asignar `mindTargetIndex` automaticamente.
- Permitir recompilar sin romper las relaciones `arAnchor` existentes.
- Documentar o empaquetar la dependencia de compilacion elegida.

Hasta implementar este modulo, los `.mind` se generan externamente.

## Prioridad 3: publicacion y entrega

- Generar una pagina de entrega con URL, target imprimible e instrucciones breves.
- Validar automaticamente el ZIP exportado antes de ofrecer la descarga.
- Añadir version y checksum de assets al manifiesto de experiencia.
- Crear perfiles de publicacion para local, LAN y hosting HTTPS.
- Añadir un checklist final probado en telefono.

## Prioridad 4: pruebas automatizadas

- Extraer logica JavaScript critica a modulos comprobables.
- Cubrir creacion de plantillas y relaciones target-contenido.
- Probar auditoria de publicacion y reconstruccion del visor.
- Añadir pruebas de API para proyectos, conflictos de version y assets.
- Añadir round-trip de exportacion/importacion, conflictos de nombres y ZIP invalidos.
- Ejecutar las verificaciones en CI.

## Prioridad 5: colaboracion

- Sustituir polling por WebSocket si se necesita respuesta inmediata.
- Transmitir operaciones o patches en lugar del layout completo.
- Diseñar resolucion de conflictos por campo u operacion.
- Mostrar cursores y seleccion remota en el lienzo.
- Persistir auditoria de cambios si el producto pasa de uso local a equipos grandes.

La colaboracion actual por version y locks debe conservarse como fallback hasta que el reemplazo tenga pruebas de concurrencia.

## Prioridad 6: seguridad y despliegue

- Separar modo desarrollo local de modo servidor compartido.
- Revisar roles y autorizacion de cada endpoint, no solo autenticacion visual.
- Añadir sesiones seguras y almacenamiento de usuarios adecuado para despliegue publico.
- Configurar limites de subida por tipo de asset y validar contenido, no solo extension.
- Documentar reverse proxy, HTTPS, cabeceras y estrategia de backups.
- Revisar dependencias CDN y ofrecer una opcion versionada/offline si es necesaria.

## Prioridad 7: rendimiento y assets

- Generar thumbnails de modelos, video y audio sin bloquear la mediateca.
- Validar dimensiones, duracion, codecs y peso antes de publicar.
- Añadir recomendaciones o conversion automatica para formatos moviles.
- Medir escenas con varios targets y assets grandes.
- Liberar recursos de audio/video y objetos Three.js al cambiar de proyecto.

## Prioridad 8: limpieza tecnica

- Renombrar internamente `stage.viewer.chatEnabled` y clases `chat-panel` a terminologia de narracion, manteniendo migracion de layouts anteriores.
- Retirar textos y nombres heredados de demos Docker/OIRA donde no correspondan.
- Reducir JavaScript y estilos embebidos mediante modulos sin alterar el despliegue simple.
- Centralizar iconos, notificaciones y componentes repetidos.
- Definir una migracion explicita para futuras versiones del layout.

## Criterio para cerrar una mejora

Una tarea se considera terminada cuando:

1. funciona en editor y visor cuando corresponde;
2. conserva proyectos existentes o incluye migracion;
3. tiene validacion automatizada o un procedimiento reproducible;
4. actualiza los Markdown afectados;
5. no deja archivos de prueba en `output/`, `projects/` o `_archive/`.

## Comandos de control

```powershell
python -m py_compile moby_studio\lanzador_ar.py
Invoke-WebRequest -UseBasicParsing http://localhost:8000/editor.html
Invoke-WebRequest -UseBasicParsing http://localhost:8000/index.html
git status --short
git diff --check
```
