import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';

/**
 * Clase base abstracta para todos los comandos editables del escenario
 * @interface
 */
export class Command {
    execute() {
        throw new Error("El método execute() debe ser implementado.");
    }
    undo() {
        throw new Error("El método undo() debe ser implementado.");
    }
}

/**
 * Gestor de historial encargado de orquestar las pilas de deshacer (Undo) y rehacer (Redo)
 */
export class HistoryManager {
    constructor() {
        /** @type {Command[]} */
        this.undoStack = [];
        /** @type {Command[]} */
        this.redoStack = [];
        /** @type {Set<Function>} */
        this.listeners = new Set();
    }

    /**
     * Suscribirse a los cambios en el historial de comandos
     * @param {Function} callback 
     * @returns {Function} Función para cancelar suscripción
     */
    subscribe(callback) {
        this.listeners.add(callback);
        return () => this.listeners.delete(callback);
    }

    /**
     * Notificar a los observadores suscritos el estado de las pilas
     * @private
     */
    _notify() {
        for (const listener of this.listeners) {
            listener({
                canUndo: this.undoStack.length > 0,
                canRedo: this.redoStack.length > 0,
                undoCount: this.undoStack.length,
                redoCount: this.redoStack.length
            });
        }
    }

    /**
     * Ejecuta y agrega un nuevo comando al historial activo
     * @param {Command} command 
     */
    execute(command) {
        command.execute();
        this.undoStack.push(command);
        this.redoStack = []; // Se limpia la pila de rehacer al realizar una nueva acción
        this._notify();
        console.log(`[Historial] Ejecutado: ${command.constructor.name}. Undo: ${this.undoStack.length}, Redo: 0`);
    }

    /**
     * Deshace el último comando en la pila
     */
    undo() {
        if (this.undoStack.length === 0) {
            console.warn("[Historial] No hay comandos que deshacer.");
            return;
        }
        const command = this.undoStack.pop();
        command.undo();
        this.redoStack.push(command);
        this._notify();
        console.log(`[Historial] Deshecho: ${command.constructor.name}. Undo: ${this.undoStack.length}, Redo: ${this.redoStack.length}`);
    }

    /**
     * Rehace el último comando deshecho en la pila
     */
    redo() {
        if (this.redoStack.length === 0) {
            console.warn("[Historial] No hay comandos que rehacer.");
            return;
        }
        const command = this.redoStack.pop();
        command.execute();
        this.undoStack.push(command);
        this._notify();
        console.log(`[Historial] Rehecho: ${command.constructor.name}. Undo: ${this.undoStack.length}, Redo: ${this.redoStack.length}`);
    }

    /**
     * Limpia todo el historial de comandos
     */
    clear() {
        this.undoStack = [];
        this.redoStack = [];
        this._notify();
        console.log("[Historial] Historial de comandos limpiado con éxito.");
    }
}

/**
 * Comando para añadir un objeto 3D a la escena
 * @implements {Command}
 */
export class AddObjectCommand extends Command {
    /**
     * @param {THREE.Object3D} object Objeto a añadir
     * @param {THREE.Object3D} parent Contenedor padre de destino
     * @param {Object} stateManager Referencia al gestor de estado
     */
    constructor(object, parent, stateManager) {
        super();
        this.object = object;
        this.parent = parent;
        this.stateManager = stateManager;
    }

    execute() {
        this.stateManager.addObject(this.object, this.parent);
    }

    undo() {
        this.stateManager.removeObject(this.object);
    }
}

/**
 * Comando para eliminar un objeto 3D de la escena
 * @implements {Command}
 */
export class RemoveObjectCommand extends Command {
    /**
     * @param {THREE.Object3D} object Objeto a eliminar
     * @param {Object} stateManager Referencia al gestor de estado
     */
    constructor(object, stateManager) {
        super();
        this.object = object;
        this.stateManager = stateManager;
        this.parent = object.parent || null;
    }

    execute() {
        this.stateManager.removeObject(this.object);
    }

    undo() {
        this.stateManager.addObject(this.object, this.parent);
    }
}

/**
 * Comando para registrar y revertir transformaciones de posición, rotación y escala
 * @implements {Command}
 */
export class TransformCommand extends Command {
    /**
     * @param {THREE.Object3D} object Objeto transformado
     * @param {THREE.Matrix4} oldMatrix Matriz 4x4 original
     * @param {THREE.Matrix4} newMatrix Matriz 4x4 final
     */
    constructor(object, oldMatrix, newMatrix) {
        super();
        this.object = object;
        this.oldMatrix = oldMatrix.clone();
        this.newMatrix = newMatrix.clone();
    }

    execute() {
        this.object.matrix.copy(this.newMatrix);
        this.object.matrix.decompose(this.object.position, this.object.quaternion, this.object.scale);
        this.object.updateMatrixWorld(true);
    }

    undo() {
        this.object.matrix.copy(this.oldMatrix);
        this.object.matrix.decompose(this.object.position, this.object.quaternion, this.object.scale);
        this.object.updateMatrixWorld(true);
    }
}
