import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';

/**
 * @typedef {Object} StateNode
 * @property {string} uuid - UUID único de la entidad 3D.
 * @property {string} name - Nombre amigable de la entidad para mostrar en el Outliner.
 * @property {string} type - Tipo de objeto Three.js (e.g., 'Mesh', 'Group', 'AmbientLight').
 * @property {THREE.Object3D} object3D - Referencia al objeto 3D en la escena.
 * @property {StateNode[]} children - Colección jerárquica de nodos hijos.
 */

/**
 * Gestor de Estado Centralizado (Scene Graph & Pub/Sub) para Moby Studio
 */
export class StateManager {
    /**
     * @param {THREE.Scene} scene - La escena activa de Three.js
     */
    constructor(scene) {
        if (!scene) {
            throw new Error("[StateManager] Se requiere una instancia válida de THREE.Scene.");
        }
        /** @type {THREE.Scene} */
        this.scene = scene;
        /** @type {Set<Function>} */
        this.listeners = new Set();
    }

    /**
     * Registrar una suscripción al estado de la jerarquía 3D
     * @param {Function} callback - Función receptora de la jerarquía
     * @returns {Function} Función para cancelar la suscripción
     */
    subscribe(callback) {
        this.listeners.add(callback);
        // Notificación inicial inmediata para el suscriptor
        callback(this.getTree());
        return () => this.listeners.delete(callback);
    }

    /**
     * Notifica a todos los suscriptores activos con el árbol actualizado de objetos de usuario
     * @private
     */
    _notify() {
        const tree = this.getTree();
        for (const callback of this.listeners) {
            try {
                callback(tree);
            } catch (error) {
                console.error("[StateManager] Error ejecutando callback de suscripción:", error);
            }
        }
    }

    /**
     * Añade un objeto de forma interactiva a la jerarquía de Three.js
     * @param {THREE.Object3D} object - El objeto a añadir
     * @param {THREE.Object3D} [parent=null] - Contenedor padre de destino (por defecto la escena)
     */
    addObject(object, parent = null) {
        if (!object) {
            console.error("[StateManager] Intento de añadir un objeto nulo o inválido.");
            return;
        }
        
        const targetParent = parent || this.scene;
        targetParent.add(object);
        object.updateMatrixWorld(true);
        
        this._notify();
        console.log(`[StateManager] Objeto añadido: ${object.name || object.uuid}. Parent: ${targetParent.type}`);
    }

    /**
     * Elimina un objeto de forma interactiva de la jerarquía de Three.js
     * @param {THREE.Object3D} object - El objeto a eliminar
     */
    removeObject(object) {
        if (!object) {
            console.error("[StateManager] Intento de remover un objeto nulo o inválido.");
            return;
        }

        if (object.parent) {
            object.parent.remove(object);
        } else {
            this.scene.remove(object);
        }

        this._notify();
        console.log(`[StateManager] Objeto eliminado: ${object.name || object.uuid}`);
    }

    /**
     * Construye y retorna la representación lógica en árbol filtrando objetos del sistema
     * @returns {StateNode[]}
     */
    getTree() {
        const rootNodes = [];
        for (const child of this.scene.children) {
            if (this._isUserObject(child)) {
                rootNodes.push(this._buildNode(child));
            }
        }
        return rootNodes;
    }

    /**
     * Construye recursivamente un nodo de estado lógico a partir de un objeto 3D
     * @param {THREE.Object3D} object 
     * @returns {StateNode}
     * @private
     */
    _buildNode(object) {
        const childrenNodes = [];
        if (object.children) {
            for (const child of object.children) {
                if (this._isUserObject(child)) {
                    childrenNodes.push(this._buildNode(child));
                }
            }
        }
        
        return {
            uuid: object.uuid,
            name: object.name || `${object.type} (${object.uuid.substring(0, 4)})`,
            type: object.type,
            object3D: object,
            children: childrenNodes
        };
    }

    /**
     * Filtra objetos auxiliares internos para que no contaminen la jerarquía del Outliner
     * @param {THREE.Object3D} obj 
     * @returns {boolean}
     * @private
     */
    _isUserObject(obj) {
        if (!obj) return false;

        // Excluir controles interactivos de transformación (Gizmo)
        if (obj.isTransformControls || obj.constructor.name.includes('TransformControls') || obj.name.includes('TransformControls')) {
            return false;
        }

        // Excluir elementos auxiliares del Viewport (Grillas, Líneas visuales)
        if (obj.isGridHelper || obj.isAxesHelper || obj.isCameraHelper) {
            return false;
        }

        // Excluir luces o cámaras internas del sistema marcadas con guiones dobles
        if (obj.name && (obj.name.startsWith('__') || obj.name.includes('system_'))) {
            return false;
        }

        return true;
    }
}
