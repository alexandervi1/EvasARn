# Moby Studio — Arquitectura de Software

Este documento proporciona una radiografía técnica exacta y detallada de la arquitectura, componentes, flujos de datos y pila tecnológica de **Moby Studio** tal como está programado en este momento.

---

## 1. Visión General del Sistema

**Moby Studio** es una plataforma interactiva de diseño y visualización en 3D y Realidad Aumentada (WebXR). El sistema se basa en una arquitectura desacoplada de dos capas:

```mermaid
graph TD
    subgraph Frontend (Cliente - Navegador)
        E[editor.html - Canvas de Diseño 3D]
        I[index.html - Experiencia AR + IA]
        EC[js/EditorCore.js]
        SM[js/StateManager.js]
        HM[js/HistoryManager.js]
        LS[js/LightingSetup.js]
    end

    subgraph Backend (Host Local / Servidor de Lanzamiento)
        L[lanzador_ar.py - Servidor HTTP/HTTPS]
        B[Blender Headless - Exportación GLB]
        Y[Inferencia YOLOv8]
        O[cerebro Ollama - Modelo qwen]
    end

    E <-->|API /api/save-layout & /api/generate-model| L
    I <-->|API /api/vision| L
    L <-->|Línea de comandos --background| B
    L <-->|Inferencia ultralytics| Y
    L <-->|HTTP POST 11434| O
```

1. **Frontend (Cliente - Ejecución en Sandbox de Navegador)**:
   - Administrado a través de módulos interactivos de JavaScript puro (ES6) y elementos personalizados de WebXR mediante **A-Frame**.
   - Proporciona dos experiencias diferenciadas: `editor.html` (estación interactiva de composición 3D al estilo de Unity y Blender) e `index.html` (visor inmersivo de Realidad Aumentada asistido por Inteligencia Artificial conversacional).
2. **Backend (Host Local - Servidor de Lanzamiento Python)**:
   - Orquestado por `lanzador_ar.py`, un servidor Web/API de alto rendimiento montado con el módulo estándar de Python `http.server` y configurado con soporte SSL/HTTPS nativo.
   - Actúa como coordinador de sistema de archivos y pasarela de orquestación local ejecutando Blender en modo desatendido (headless) y corriendo modelos de visión y lenguaje localmente.

---

## 2. Pila Tecnológica Actual

El ecosistema técnico del proyecto se compone de las siguientes herramientas de desarrollo:

- **Motor Gráfico & Renderizado**:
  - **Three.js (r128)**: Utilizado para la creación de primitivas, control espacial de transformaciones 3D, cálculos de matrices globales e inyección de flujos físicos de iluminación.
  - **A-Frame (1.4.2)**: Capa declarativa basada en componentes y entidades que expone la escena WebGL en HTML, adaptada para renderizado WebXR interactivo en dispositivos móviles.
- **Interacciones del Canvas**:
  - **THREE.TransformControls**: Control interactivo de Gizmos espaciales en pantalla (flechas/aros RGB) para alterar directamente matrices del escenario.
- **Herramientas de Servidor & Backend**:
  - **Python 3**: Entorno principal del servidor que gestiona rutas estáticas y endpoints asíncronos.
  - **Blender (Headless Mode)**: Motor procedural externo convocado dinámicamente mediante línea de comandos (`blender --background --python scripts/<script>`) para compilar y exportar archivos GLB PBR al vuelo.
- **Procesamiento de Inteligencia Artificial (IA)**:
  - **YOLOv8 (ultralytics)**: Modelo de visión artificial de red neuronal convolucional para la clasificación y delimitación física de objetos reales en fotogramas de la cámara.
  - **Ollama**: Entorno de ejecución de Modelos de Lenguaje Grandes (LLMs) configurado localmente en el puerto `11434` para ejecutar el modelo liviano y ágil `qwen`.

---

## 3. Desglose del Editor 3D (`editor.html`)

El editor en `editor.html` proporciona una suite completa de modelado espacial que imita el comportamiento dinámico de los motores de videojuegos de escritorio a través de cuatro módulos:

### A. Scene Graph y Árbol de Estado (`js/StateManager.js`)
- **Clase Central**: `StateManager` vinculada a la escena física `THREE.Scene`.
- **Estructura Jerárquica**: Almacena y computa una representación en árbol limpia de los objetos del usuario (Outliner), compuesta de nodos lógicos (`StateNode`).
- **Filtro del Sistema**: Excluye mediante la rutina privada `_isUserObject(obj)` todos los elementos auxiliares de Three.js que actúan como decoradores de interfaz (como `TransformControls`, `GridHelper`, `AxesHelper` y luces del sistema).
- **Pub/Sub (Observable)**: Cuenta con un método `subscribe(callback)` que acumula suscriptores en un `Set` interno. Dispara notificaciones asíncronas automáticas enviando el árbol reconstruido cada vez que se ejecutan los métodos `addObject(object, parent)` o `removeObject(object)`.

### B. Historial Undo/Redo (`js/HistoryManager.js`)
- **Patrón Command**: Implementa una interfaz base `Command` que expone los contratos `execute()` y `undo()`.
- **Comandos Concretos**:
  - `AddObjectCommand`: Invoca al `StateManager` para insertar el elemento en el lienzo físico y el árbol lógico.
  - `RemoveObjectCommand`: Desacopla el Gizmo y extrae la entidad, guardando referencias a su contenedor padre para restaurarlo si es necesario.
  - `TransformCommand`: Captura y clona la matriz de transformación original `oldMatrix` y la final `newMatrix` de tipo `THREE.Matrix4`. Ejecuta reversiones aplicando `matrix.copy()` y decompone las coordenadas espaciales (`matrix.decompose(position, quaternion, scale)`) actualizando el espacio del mundo.
- **Historial Lineal**: Controla dos arreglos (`undoStack` y `redoStack`) y limpia la pila de rehacer inmediatamente tras cualquier nueva acción ejecutada por el usuario.

### C. Viewport Controls & Snapping Matemático (`js/EditorCore.js`)
- **Orquestador**: La clase `EditorCore` inicializa e integra la instancia de `TransformControls`. Sincroniza la navegación deshabilitando dinámicamente los controles orbitales de cámara (`OrbitControls`) al interceptar el evento `dragging-changed` del Gizmo (evitando interferencias al arrastrar flechas).
- **Control de Cambios en Historial**:
  - Al detectar `drag-start`, clona y respalda la matriz tridimensional activa.
  - Al detectar `drag-end`, si la matriz resultante difiere de la original, instancia un `TransformCommand` y lo despacha al `HistoryManager` para habilitar el retorno de estado.
- **Snapping Manual**:
  - Evaluado en tiempo real dentro del callback del evento `objectChange` de `TransformControls` cuando `isSnapEnabled` es verdadero.
  - **Traslación**: Restringe la posición redondeando matemáticamente a intervalos fijos de `0.5` unidades.
  - **Rotación**: Restringe los ángulos redondeando matemáticamente a pasos exactos de `15 grados` (`Math.PI / 12` radianes).
  - **Escala**: Restringe las proporciones dimensionales a intervalos de `10%` (`0.1` unidades).

### D. Iluminación Profesional & PBR (`js/LightingSetup.js`)
- **Inyección de Luces**:
  - Inyecta una luz ambiental suave (`AmbientLight`) para iluminar zonas de sombra.
  - Inserta una luz direccional principal (`DirectionalLight`) configurada con `castShadow = true`.
- **Sombras Definidas**: Aumenta la resolución del mapa de sombras a `2048 x 2048` píxeles e implementa una cámara de sombras ortogonal adaptativa para evitar recortes. Aplica un leve offset negativo (`shadow.bias = -0.0003`) y `shadow.normalBias = 0.02` para eliminar interferencias de visualización sobre mallas cerradas (shadow acne).
- **Entorno Equirectangular**: Utiliza la extensión `RGBELoader` para cargar asíncronamente imágenes HDR de alta resolución. Procesa la textura cargada usando `PMREMGenerator` y compila los shaders reflectores asignando la textura resultante a `scene.environment`.

---

## 4. Desglose de AR e IA (`index.html`)

El visor `index.html` proporciona una experiencia híbrida de hologramas e interactividad en tiempo real asistida por Visión Computacional local:

### A. Transparencia Híbrida WebGL en A-Frame
Para fusionar objetos holográficos con el mundo real capturado por la cámara física en móviles sin pantallas opacas, el sistema realiza tres acciones en cascada:

1. **Parámetro Escena**: Configura `<a-scene background="transparent: true">`.
2. **Estilo CSS**: Sobrescribe y anula el fondo de borrado por defecto de A-Frame forzando total transparencia en el contenedor del lienzo:
   ```css
   a-scene, .a-canvas {
       background: transparent !important;
       background-color: transparent !important;
   }
   ```
3. **Controlador WebGLRenderer**: Escucha el evento `renderstart` de A-Frame para inyectarse directamente en el contexto del renderizador WebGL subyacente de Three.js:
   ```javascript
   sceneEl.addEventListener('renderstart', function () {
       this.renderer.setClearColor(0x000000, 0); // Canal alfa en cero
       this.renderer.alpha = true;
   });
   ```

### B. Pipeline de Inferencia Visual

La interacción del "Sonar Visual" de Moby sigue un flujo asíncrono estricto de cinco fases secuenciales:

```
[Feed de Video HTML5] ➔ [Captura Canvas 2D (Base64)] ➔ [API POST /api/vision]
                                                                  │
                                                                  ▼
[Speech TTS + HUD] 🔀 [Filtro de Texto MD] ◀ [Ollama (qwen)] ◀ [YOLOv8 Inferencia]
```

1. **Captura Físico-Digital (Navegador)**:
   - Al presionar **Escanear Entorno**, se extrae el fotograma activo del elemento HTML `<video>` y se dibuja sobre un lienzo auxiliar bidimensional en memoria de `640 x 480` píxeles.
   - Se exporta a formato JPEG codificado en Base64 utilizando `canvas.toDataURL("image/jpeg", 0.85)`.
2. **Ingesta y Transmisión Asíncrona**:
   - Envía el paquete JSON `{ image: base64Image }` mediante una llamada POST AJAX al endpoint local `/api/vision` de `lanzador_ar.py`.
3. **Inferencia de Visión (Servidor Python Local)**:
   - El backend decodifica la cadena a binario y la almacena en `temp_capture.jpg`.
   - Inicializa de forma perezosa (lazy-load) el módulo de `ultralytics`. Corre la inferencia física sobre la imagen temporal priorizando el modelo especializado `yolov8_docker_custom.pt` (y cayendo en `yolov8n.pt` si no existe).
   - Filtra las cajas de clasificación detectadas descartando aquellas con confianza inferior al `50%`. Destruye el archivo temporal.
4. **Pensamiento Cognitivo (Ollama Local)**:
   - Formatea un prompt estructurado de comportamiento inyectando los objetos detectados (ej. `"laptop (87% de confianza), cup (92% de confianza)"`).
   - Envía una petición HTTP interna a `http://localhost:11434/api/generate` indicando el modelo `"qwen"`.
   - Ollama genera en tiempo real una respuesta conversacional didáctica de máximo 2 oraciones en español simulando la personalidad de Moby (la ballena de Docker), realizando analogías inteligentes sobre cómo esos objetos cotidianos se relacionan con la contenedorización.
5. **HUD Subtitulado & Voz Sintetizada**:
   - El cliente recibe la respuesta del servidor y ejecuta `limpiarMarkdown(texto)` para normalizar la cadena (removiendo marcas de negritas, títulos o caracteres extraños de control).
   - Dispara la animación tridimensional `hacerSaltarMoby()`.
   - Lanza el Typewriter HUD (mecanografía por pasos de caracteres en subtítulos) e inicializa la API nativa de síntesis de voz del navegador (`window.speechSynthesis`) para que Moby relate de viva voz su análisis al usuario.

---

## 5. Estructura de Datos

El estado espacial completo del escenario tridimensional interactivo de Moby Studio se serializa, almacena y transmite a través de un archivo plano plano en formato JSON denominado `layout.json`, guardado en el subdirectorio de salida `output/`.

### Estructura de Datos de `layout.json`

La jerarquía del diseño se compone de un arreglo estructurado de objetos de entidad. Cada objeto expone estrictamente las siguientes propiedades de tipo primitivo y espacial:

```json
[
    {
        "uuid": "string",
        "nombre": "string",
        "modelId": "string",
        "posicion": {
            "x": "number",
            "y": "number",
            "z": "number"
        },
        "rotacion": {
            "x": "number",
            "y": "number",
            "z": "number"
        },
        "escala": "number"
    }
]
```

### Ejemplo de Datos de Producción Real

```json
[
    {
        "uuid": "entidad-laptop-1",
        "nombre": "Laptop Docker",
        "modelId": "laptop_caos",
        "posicion": {
            "x": 1.5,
            "y": 0.5,
            "z": -3.0
        },
        "rotacion": {
            "x": 0.0,
            "y": 45.0,
            "z": 0.0
        },
        "escala": 1.2
    },
    {
        "uuid": "entidad-ballena-2",
        "nombre": "Ballena Docker Procedural",
        "modelId": "ballena_docker",
        "posicion": {
            "x": 0.0,
            "y": 2.0,
            "z": -5.5
        },
        "rotacion": {
            "x": 0.0,
            "y": 180.0,
            "z": 0.0
        },
        "escala": 2.5
    }
]
```

### Flujo de Sincronización de Datos

- **Persistencia**: Al presionar **Guardar Escenario** en el panel, el cliente captura el estado activo de `escenaObjetos` y realiza una petición POST con los datos serializados a `/api/save-layout`, escribiendo físicamente el archivo `output/layout.json`.
- **Hidratación**: Al cargar el visor (`editor.html` o `index.html`), se efectúa un fetch GET a `output/layout.json`. Si el archivo existe, itera la colección, crea los elementos dinámicamente (`document.createElement('a-entity')`), inyecta los atributos espaciales correspondientes e hidrata el estado local.
