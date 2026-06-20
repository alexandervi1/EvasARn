# Tutorial de primeros pasos

Este tutorial crea una experiencia WebAR que reconoce una imagen fisica y muestra contenido asociado.

## 1. Preparar el entorno

Desde la raiz del repositorio:

```powershell
python moby_studio\lanzador_ar.py
```

Abre:

```text
http://localhost:8000/editor.html
```

El visor final esta en:

```text
http://localhost:8000/index.html
```

Al entrar desde la misma PC, el editor usa el perfil administrador local. En una conexion remota, inicia sesion o registra un usuario.

## 2. Preparar el target

Necesitas dos archivos relacionados:

1. La imagen fisica que mostraras impresa o en otra pantalla.
2. El archivo `.mind` generado a partir de esa imagen.

Moby Studio no compila `.mind` actualmente. Debes generarlo con una herramienta compatible con MindAR antes de configurar la escena.

Un buen target tiene detalle, contraste y rasgos no repetitivos. Evita imagenes borrosas, superficies lisas, patrones repetidos y reflejos fuertes.

## 3. Crear o seleccionar un proyecto

1. Abre `Gestionar proyectos` desde el engranaje de la barra izquierda.
2. Crea un proyecto o selecciona uno existente.
3. Cierra el gestor y confirma el nombre activo en la barra superior.

El proyecto se guarda en:

```text
moby_studio/projects/<proyecto>/layout.json
```

## 4. Elegir una plantilla

Abre `Agregar contenido` en la barra izquierda. Las plantillas actuales son:

- `Marcador + Imagen`
- `Marcador + Video`
- `Marcador + Audio`
- `Marcador + Modelo 3D`
- `Boton interactivo`

Cada plantilla crea un target y un contenido ya vinculado. Para empezar desde cero tambien puedes crear un `Marcador AR` y agregar recursos manualmente.

## 5. Configurar el target

En el modal de configuracion AR:

1. Sube la imagen fisica del target.
2. Sube el archivo `.mind` correspondiente.
3. Deja `mindTargetIndex` en `0` si el `.mind` contiene una sola imagen.
4. Comprueba que el resumen muestre el target y el archivo compilado.

Para varios targets, compila todas las imagenes en un solo `.mind`, asigna ese mismo archivo a cada target y usa indices distintos:

```text
Target A -> mindTargetIndex 0
Target B -> mindTargetIndex 1
Target C -> mindTargetIndex 2
```

El visor rechaza una escena que intente usar varios archivos `.mind` diferentes.

## 6. Agregar contenido

Puedes subir el archivo desde el modal AR o desde `Recursos`.

| Contenido | Formatos comunes |
|---|---|
| Modelo 3D | `.glb`, `.gltf` |
| Imagen | `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` |
| Video | `.mp4`, `.webm`, `.mov` |
| Audio | `.mp3`, `.wav`, `.ogg`, `.m4a`, `.aac` |
| Boton | `.glb`, `.gltf` para boton 3D; o texto y color para boton 2D |

Al usar la mediateca:

1. Sube el recurso.
2. Filtra por su tipo si es necesario.
3. Pulsa agregar para crear contenido o asignalo al objeto seleccionado.
4. Para un `.mind`, selecciona primero el target y usa la accion de asignacion.
5. Para un boton, define su aspecto y luego asigna la accion al contenido que deba controlar.

Los `.mind` no se agregan como objetos visuales independientes.

## 7. Revisar el anclaje

Selecciona el contenido en `Escena` y revisa el inspector derecho.

- Si `arAnchor` apunta al target, el contenido aparecera cuando MindAR lo detecte.
- Si aparece como `Mesa base`, no esta vinculado a un marcador.

Las plantillas crean este vinculo automaticamente, pero debes revisarlo si mueves o reasignas contenido.

## 8. Componer en el lienzo

Usa el lienzo para ajustar el resultado relativo al target:

1. Selecciona el contenido.
2. Usa los controles de mover, rotar o escalar.
3. Ajusta valores precisos desde el inspector.
4. Usa el visor movil integrado como referencia de encuadre.
5. Guarda cuando el resultado sea correcto.

En pantallas estrechas, abre los paneles desde la barra lateral y cierralos al trabajar sobre el lienzo.

## 9. Particularidades por tipo

### Imagen y video

Ajusta ancho y alto del panel desde el inspector. Para video, revisa autoplay, loop, volumen y silencio. Los navegadores pueden exigir una interaccion antes de habilitar audio.

### Audio

El visor crea un reproductor espacial con ondas animadas. No muestra controles internos de play/pausa; la reproduccion se controla con botones externos o con la interaccion que configures en la escena. Si autoplay es bloqueado, usa un boton de la propia experiencia.

### Botones interactivos

Los botones son contenido AR normal. Puedes:

1. Poner un boton 2D con texto y color.
2. Subir un modelo GLB como boton personalizado.
3. Asignar acciones como `next`, `previous`, `show`, `hide`, `toggle`, `play`, `pause` y `stop`.
4. Hacer que el boton permanezca oculto hasta que se detecte por primera vez su target asociado.

Si el boton no tiene target asociado, no se publica como control global.

### Modelo 3D

Prefiere GLB optimizados. Si Blender esta instalado, la mediateca permite comprimir GLB con Draco. Comprueba siempre la escala porque los modelos externos usan unidades diferentes.

## 10. Validar y guardar

Abre `Validar`. Una experiencia lista debe cumplir:

1. Existe al menos un target.
2. Cada target tiene imagen fisica y `.mind`.
3. Todos los targets usan el mismo `.mind`.
4. Los indices no se repiten.
5. Cada contenido AR esta anclado.
6. Cada contenido multimedia tiene un archivo.
7. El proyecto no tiene cambios pendientes de guardar.

Corrige los errores, guarda y vuelve a ejecutar la validacion.

## 11. Probar en la PC

1. Abre `http://localhost:8000/index.html`.
2. Pulsa `Iniciar AR`.
3. Concede acceso a la camara.
4. Apunta al target impreso o mostrado en otro dispositivo.

El contenido aparece en `targetFound` y se oculta o pausa en `targetLost`.

Los botones asociados al target se activan despues de esa primera deteccion; antes de eso permanecen ocultos.

## 12. Probar en telefono

La camara movil normalmente requiere HTTPS. Publica el puerto `8000` mediante un tunel HTTPS y abre en el telefono la ruta `/index.html`.

Comprueba:

- permiso de camara;
- carga del `.mind`;
- iluminacion y reflejos;
- indice correcto;
- escala del contenido;
- reproduccion de video o audio tras tocar la pantalla.

No uses una URL de tunel antigua: estas direcciones suelen cambiar al reiniciar el servicio.

## 13. Transferir el proyecto a otra PC

1. Guarda el proyecto.
2. Abre `Gestionar proyectos`.
3. En `Transferir entre PCs`, pulsa `Exportar proyecto`.
4. Lleva el ZIP a la otra PC.
5. En la segunda instalacion, pulsa `Importar ZIP`.
6. Indica otro nombre si ya existe un proyecto igual.

El ZIP conserva el layout editable y los assets locales utilizados. Las URLs externas se conservan como referencias y requieren red en la PC de destino.

## 14. Entregar una experiencia

Usa `Exportar experiencia` cuando quieras un paquete para ejecucion, no para continuar editando. Antes de entregarlo:

1. valida y guarda;
2. prueba el target real;
3. revisa el ZIP exportado;
4. confirma que el entorno final sirve los archivos por HTTPS;
5. incluye el target fisico y las instrucciones para el usuario.

## Solucion de problemas

### El lienzo queda cargando

- Abre la consola del navegador.
- Confirma que A-Frame carga desde CDN.
- Recarga sin cache.
- Verifica que `editor.html` responda desde el servidor, no como archivo local.

### El target no se detecta

- Confirma que `.mind` corresponde a la imagen mostrada.
- Revisa `mindTargetIndex`.
- Usa buena luz y evita reflejos.
- Verifica que todos los targets compartan el mismo `.mind`.

### La camara no abre

- Concede permisos al navegador.
- Usa `localhost` en la PC o HTTPS en el telefono.
- Cierra otras aplicaciones que esten usando la camara.

### El audio no inicia

- Toca un boton externo configurado para reproducir el audio.
- Comprueba el volumen del objeto y del dispositivo.
- Verifica que el formato sea compatible con el navegador.

### Un boton no responde

- Confirma que el boton tenga un `arAnchor` valido.
- Revisa que el target asociado ya haya sido detectado al menos una vez.
- Verifica que la accion configurada apunte a un objeto existente.
