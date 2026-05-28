import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
import { TransformControls } from 'https://unpkg.com/three@0.128.0/examples/jsm/controls/TransformControls.js';
import { TransformCommand, RemoveObjectCommand } from './HistoryManager.js';

/**
 * Motor Principal de Interacción del Viewport (Gizmo, Snapping y Atajos)
 */
export class EditorCore {
    /**
     * @param {THREE.Scene} scene - La escena activa de Three.js
     * @param {THREE.PerspectiveCamera} camera - La cámara de visualización activa
     * @param {HTMLElement} domElement - El contenedor DOM para el control de eventos (render.domElement)
     * @param {Object} historyManager - Instancia del HistoryManager
     * @param {Object} stateManager - Instancia del StateManager
     */
    constructor(scene, camera, domElement, historyManager, stateManager) {
        if (!scene || !camera || !domElement || !historyManager || !stateManager) {
            throw new Error("[EditorCore] Faltan dependencias críticas para la inicialización.");
        }

        /** @type {THREE.Scene} */
        this.scene = scene;
        /** @type {THREE.PerspectiveCamera} */
        this.camera = camera;
        /** @type {HTMLElement} */
        this.domElement = domElement;
        /** @type {Object} */
        this.historyManager = historyManager;
        /** @type {Object} */
        this.stateManager = stateManager;

        /** @type {boolean} */
        this.isSnapEnabled = false;
        
        /** @type {Object|null} */
        this.orbitControls = null;
        /** @type {THREE.Matrix4|null} */
        this.oldMatrix = null;

        // Callbacks de notificación a la interfaz de usuario externa
        this.onChangeCallback = null;
        this.onModeChange = null;
        this.onSnapToggle = null;

        // Inicializar TransformControls
        /** @type {TransformControls} */
        this.transformControls = new TransformControls(camera, domElement);
        this.transformControls.name = "system_transform_controls";
        this.scene.add(this.transformControls);

        // Enlazar listeners de eventos del Gizmo
        this._setupGizmoEvents();
        
        // Habilitar atajos de teclado globales
        this.setupKeyBindings();
    }

    /**
     * Define los eventos para la interacción física y lógica del Gizmo
     * @private
     */
    _setupGizmoEvents() {
        // Evento de cambio (necesario para forzar re-renderizado si no hay loop activo)
        this.transformControls.addEventListener('change', () => {
            if (this.onChangeCallback) {
                this.onChangeCallback();
            }
        });

        // Evento de arrastre de cambio de matriz (Drag-Start / Drag-End)
        this.transformControls.addEventListener('dragging-changed', (event) => {
            const isDragging = event.value;

            // Deshabilitar navegación orbital de cámara para prevenir peleas en el Viewport
            if (this.orbitControls) {
                this.orbitControls.enabled = !isDragging;
            }

            if (isDragging) {
                // Al iniciar el arrastre, clonamos el estado espacial actual
                if (this.transformControls.object) {
                    this.oldMatrix = this.transformControls.object.matrix.clone();
                }
            } else {
                // Al finalizar, guardamos la transformación en el historial si hubo cambios reales
                if (this.transformControls.object && this.oldMatrix) {
                    const object = this.transformControls.object;
                    object.updateMatrix();
                    const newMatrix = object.matrix.clone();

                    if (!this.oldMatrix.equals(newMatrix)) {
                        const command = new TransformCommand(object, this.oldMatrix, newMatrix);
                        this.historyManager.execute(command);
                    }
                    this.oldMatrix = null;
                }
            }
        });

        // Restricción matemática de Snapping interactivo durante la transformación física del objeto
        this.transformControls.addEventListener('objectChange', () => {
            if (this.isSnapEnabled && this.transformControls.object) {
                const object = this.transformControls.object;
                const mode = this.transformControls.mode;

                if (mode === 'translate') {
                    // Snapping en pasos exactos de 0.5 unidades
                    object.position.x = Math.round(object.position.x / 0.5) * 0.5;
                    object.position.y = Math.round(object.position.y / 0.5) * 0.5;
                    object.position.z = Math.round(object.position.z / 0.5) * 0.5;
                } else if (mode === 'rotate') {
                    // Snapping en pasos exactos de 15 grados (Math.PI / 12)
                    const step = Math.PI / 12;
                    object.rotation.x = Math.round(object.rotation.x / step) * step;
                    object.rotation.y = Math.round(object.rotation.y / step) * step;
                    object.rotation.z = Math.round(object.rotation.z / step) * step;
                } else if (mode === 'scale') {
                    // Snapping en pasos de escala del 10% (0.1 unidades)
                    object.scale.x = Math.round(object.scale.x / 0.1) * 0.1;
                    object.scale.y = Math.round(object.scale.y / 0.1) * 0.1;
                    object.scale.z = Math.round(object.scale.z / 0.1) * 0.1;
                }
            }
        });
    }

    /**
     * Enlaza y mapea atajos de teclado estándar de la industria (Unity/Blender layout)
     */
    setupKeyBindings() {
        this.keyListener = (event) => {
            // Ignorar atajos si el usuario escribe en inputs, textareas o formularios
            const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
            if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select') {
                return;
            }

            const key = event.key.toLowerCase();
            const ctrlOrMeta = event.ctrlKey || event.metaKey;

            switch (key) {
                // Tecla Q: Modo Órbita / Selección pura (Libera el Gizmo)
                case 'q':
                    this.detach();
                    if (this.onModeChange) this.onModeChange('orbit');
                    break;
                // Tecla W: Modo de Posición / Traslación
                case 'w':
                    this.transformControls.setMode('translate');
                    if (this.transformControls.object) {
                        this.attach(this.transformControls.object);
                    }
                    if (this.onModeChange) this.onModeChange('translate');
                    break;
                // Tecla E: Modo de Rotación
                case 'e':
                    this.transformControls.setMode('rotate');
                    if (this.transformControls.object) {
                        this.attach(this.transformControls.object);
                    }
                    if (this.onModeChange) this.onModeChange('rotate');
                    break;
                // Tecla R: Modo de Escala proporcional
                case 'r':
                    this.transformControls.setMode('scale');
                    if (this.transformControls.object) {
                        this.attach(this.transformControls.object);
                    }
                    if (this.onModeChange) this.onModeChange('scale');
                    break;
                // Tecla S: Habilitar o inhabilitar snapping manual
                case 's':
                    if (!ctrlOrMeta) {
                        this.isSnapEnabled = !this.isSnapEnabled;
                        console.log(`[EditorCore] Snapping conmutado a: ${this.isSnapEnabled}`);
                        if (this.onSnapToggle) this.onSnapToggle(this.isSnapEnabled);
                    }
                    break;
                // Tecla Z con Ctrl/Cmd: Comando Deshacer (Undo)
                case 'z':
                    if (ctrlOrMeta) {
                        event.preventDefault();
                        if (event.shiftKey) {
                            // Ctrl+Shift+Z para Rehacer (Redo)
                            this.historyManager.redo();
                        } else {
                            this.historyManager.undo();
                        }
                    }
                    break;
                // Tecla Y con Ctrl/Cmd: Comando Rehacer (Redo)
                case 'y':
                    if (ctrlOrMeta) {
                        event.preventDefault();
                        this.historyManager.redo();
                    }
                    break;
                // Suprimir o Retroceso: Eliminar objeto de usuario activo en el lienzo
                case 'delete':
                case 'backspace':
                    const activeObject = this.transformControls.object;
                    if (activeObject) {
                        event.preventDefault();
                        const command = new RemoveObjectCommand(activeObject, this.stateManager);
                        this.historyManager.execute(command);
                        this.detach();
                    }
                    break;
            }
        };

        window.addEventListener('keydown', this.keyListener);
    }

    /**
     * Vincula el componente interactivo de cámara orbital
     * @param {Object} controls - La instancia de OrbitControls del visor
     */
    setOrbitControls(controls) {
        this.orbitControls = controls;
    }

    /**
     * Acopla físicamente el Gizmo de transformaciones a una entidad 3D
     * @param {THREE.Object3D} object 
     */
    attach(object) {
        if (!object) {
            this.detach();
            return;
        }
        this.transformControls.attach(object);
        console.log(`[EditorCore] Gizmo acoplado a objeto: ${object.name || object.uuid}`);
    }

    /**
     * Desacopla el Gizmo de transformación activo de cualquier objeto
     */
    detach() {
        this.transformControls.detach();
    }

    /**
     * Registra un callback que se llamará ante cualquier alteración visual en el Viewport
     * @param {Function} callback 
     */
    setOnChange(callback) {
        this.onChangeCallback = callback;
    }

    /**
     * Libera listeners y elimina los controles interactivos de la escena
     */
    dispose() {
        window.removeEventListener('keydown', this.keyListener);
        this.transformControls.dispose();
        this.scene.remove(this.transformControls);
        console.log("[EditorCore] Recursos del Viewport y listeners destruidos.");
    }
}
