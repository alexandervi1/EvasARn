# Tutorial para usuarios primerizos

Este tutorial explica como crear una experiencia WebAR basica en Moby Studio usando una imagen fisica como target y contenido proyectado encima.

## Que vas a crear

Una escena donde la camara reconoce una imagen fisica, por ejemplo una tarjeta, etiqueta, poster o foto impresa, y muestra encima:

- un modelo 3D;
- una imagen;
- un video;
- o un rotulo informativo.

## Antes de empezar

Necesitas:

1. Moby Studio corriendo en tu PC.
2. Una imagen fisica que funcionara como target.
3. Un archivo `.mind` generado para esa imagen.
4. Un contenido para mostrar encima: imagen, video o modelo 3D.
5. Un telefono con navegador moderno si quieres probar con camara real.

Importante: Moby Studio usa MindAR. Eso significa que la camara no reconoce objetos genericos como "una PC" o "una mesa" por si sola. Reconoce imagenes entrenadas en un archivo `.mind`.

## 1. Abrir Moby Studio

Desde PowerShell:

```powershell
cd "C:\Users\ALEXANDER VILLALVA\Desktop\mcpBlender\moby_studio"
.\venv\Scripts\python.exe lanzador_ar.py
```

Abre el editor:

```text
http://localhost:8000/editor.html
```

El visor final esta en:

```text
http://localhost:8000/index.html
```

## 2. Crear un proyecto

1. Abre el editor.
2. Usa el selector de proyecto si quieres crear o cambiar de proyecto.
3. Guarda con frecuencia.

Cada proyecto guarda su escena en:

```text
moby_studio/projects/<nombre-del-proyecto>/layout.json
```

El visor usa el layout activo publicado en:

```text
moby_studio/output/layout.json
```

## 3. Crear un target AR

Un target AR es la imagen que la camara debe reconocer.

Ejemplos de buenos targets:

- una tarjeta con mucho detalle;
- una portada;
- una etiqueta con texto e imagen;
- un poster;
- una foto con contraste.

Evita:

- imagenes muy borrosas;
- superficies lisas sin detalles;
- patrones repetidos;
- imagenes con reflejos fuertes;
- objetos 3D sin una imagen plana clara.

En el editor:

1. Ve a `Crear`.
2. Elige `Flujo AR` o `Marcador AR`.
3. Selecciona el target creado.
4. En el inspector o modal AR, sube la imagen fisica del target.

## 4. Subir el archivo `.mind`

El archivo `.mind` es el target compilado para MindAR.

Por ahora Moby Studio no compila `.mind` localmente. Debes generarlo fuera de la app y luego subirlo.

Cuando ya tengas el archivo:

1. Selecciona el target en el editor.
2. Busca `Target MindAR (.mind)`.
3. Pulsa `Subir`.
4. Selecciona tu archivo `.mind`.
5. Verifica que el campo `mindTargetUrl` quede lleno.

Si solo tienes un target, deja:

```text
mindTargetIndex = 0
```

## 5. Caso con varios targets

Si quieres reconocer varias tarjetas, por ejemplo 12 tarjetas:

1. Compila las 12 imagenes dentro de un solo archivo `.mind`.
2. Crea 12 targets en Moby Studio.
3. A todos les asignas el mismo `.mind`.
4. A cada target le asignas un indice distinto:

```text
Tarjeta 1  -> mindTargetIndex 0
Tarjeta 2  -> mindTargetIndex 1
Tarjeta 3  -> mindTargetIndex 2
...
Tarjeta 12 -> mindTargetIndex 11
```

No uses 12 archivos `.mind` distintos en la misma escena. MindAR usa un solo `.mind` por escena.

## 6. Agregar contenido AR

Puedes agregar contenido desde `Crear` o desde la mediateca.

Tipos comunes:

- Modelo 3D: `.glb` o `.gltf`.
- Imagen: `.png`, `.jpg`, `.jpeg`, `.webp` o `.gif`.
- Video: `.mp4`, `.webm` o `.mov`.
- Nodo OIRA: rotulo o panel informativo dentro de la escena.

Pasos:

1. Sube o selecciona el contenido.
2. Agrégalo a la escena.
3. Selecciona el contenido.
4. En el inspector, busca la opcion de anclaje.
5. Asigna el contenido al target correcto.

Si un contenido queda en `Mesa base`, aparecera como contenido no anclado. Para AR real debe estar anclado a un target.

## 7. Acomodar el holograma

En el lienzo central:

1. Selecciona el contenido.
2. Usa mover, rotar y escalar.
3. Colocalo encima del target.
4. Ajusta su altura para que no quede pegado a la imagen.

Recomendacion inicial:

- Para imagenes o videos, empieza con escala pequena.
- Para modelos 3D, revisa que no sean demasiado grandes.
- Guarda despues de ajustar.

## 8. Validar antes de publicar

Ve a `Publicar` y ejecuta la validacion.

La escena debe cumplir:

1. Tener al menos un target.
2. Cada target debe tener imagen fisica.
3. Cada target debe tener archivo `.mind`.
4. Todos los targets deben usar el mismo `.mind`.
5. Los indices `mindTargetIndex` no deben repetirse.
6. El contenido debe estar anclado a un target.
7. Las imagenes/videos/modelos deben tener archivo asignado.
8. El proyecto debe estar guardado.

Si la validacion marca errores, corrígelos antes de abrir el visor.

## 9. Probar en PC

Guarda el proyecto y abre:

```text
http://localhost:8000/index.html
```

Pulsa `Camara RA`.

Si estas en la misma PC, `localhost` puede usar camara. Apunta la camara al target fisico o a la imagen mostrada en otra pantalla.

## 10. Probar en telefono

En telefono, la camara suele requerir HTTPS.

Usa Cloudflare Tunnel, ngrok u otra herramienta similar apuntando al puerto:

```text
8000
```

Luego abre la URL HTTPS en el telefono.

Pasos:

1. Abre la URL HTTPS del visor.
2. Pulsa `Camara RA`.
3. Acepta permisos de camara.
4. Apunta al target fisico.
5. Espera a que MindAR detecte la imagen.

Si no detecta:

- mejora la luz;
- evita reflejos;
- aleja o acerca la camara;
- revisa que el `.mind` corresponda a esa imagen;
- confirma que el `mindTargetIndex` sea correcto;
- confirma que todos los targets usen el mismo `.mind`.

## 11. Ejemplo rapido: tarjeta con video

Objetivo: al ver una tarjeta, aparece un video encima.

1. Prepara la imagen de la tarjeta.
2. Genera el archivo `.mind`.
3. Crea un target en Moby Studio.
4. Sube la imagen fisica al target.
5. Sube el `.mind`.
6. Sube el video `.mp4`.
7. Agrega el video a la escena.
8. Ancla el video al target.
9. Ajusta posicion y escala.
10. Guarda.
11. Valida en `Publicar`.
12. Abre `index.html` y prueba con la camara.

## 12. Ejemplo rapido: rotulo encima de una PC

Objetivo: al mirar una imagen asociada a la PC, aparece un rotulo con especificaciones.

1. Crea una etiqueta o imagen target para pegar cerca de la PC.
2. Genera el `.mind` de esa etiqueta.
3. Crea un target en Moby Studio.
4. Sube la imagen de la etiqueta.
5. Sube el `.mind`.
6. Crea un nodo OIRA o una imagen con texto, por ejemplo:

```text
PC Principal
CPU: Ryzen 7
RAM: 32 GB
GPU: RTX
Almacenamiento: 1 TB SSD
```

7. Ancla el rotulo al target.
8. Ajusta para que parezca colocado encima o al lado de la PC.
9. Guarda y prueba desde el visor.

## Problemas comunes

### La camara no abre en telefono

Usa HTTPS. En movil, HTTP normal suele bloquear la camara.

### El target no detecta

Revisa que el `.mind` fue generado desde la misma imagen fisica que estas mostrando.

### Tengo varios targets y algunos no funcionan

Todos deben estar dentro del mismo `.mind`. Luego usa `mindTargetIndex` diferente para cada uno.

### El contenido aparece en el editor pero no en el visor

Revisa que este anclado a un target y que el proyecto este guardado.

### El video no se reproduce

Prueba con `.mp4` optimizado para web. En algunos telefonos el autoplay puede depender de permisos o interaccion del usuario.

## Flujo recomendado

```text
Crear target -> subir imagen fisica -> subir .mind -> agregar contenido -> anclar -> ajustar -> validar -> guardar -> probar en visor
```

Ese es el flujo principal para crear experiencias WebAR con Moby Studio.
