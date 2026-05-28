import * as THREE from 'https://unpkg.com/three@0.128.0/build/three.module.js';
import { RGBELoader } from 'https://unpkg.com/three@0.128.0/examples/jsm/loaders/RGBELoader.js';

/**
 * Sistema de Iluminación y Entorno PBR de Alta Fidelidad para Moby Studio
 */
export class LightingSetup {
    /**
     * @param {THREE.Scene} scene - La escena activa de Three.js
     * @param {THREE.WebGLRenderer} renderer - El renderizador de WebGL de la aplicación
     */
    constructor(scene, renderer) {
        if (!scene || !renderer) {
            throw new Error("[LightingSetup] Se requiere una instancia válida de THREE.Scene y THREE.WebGLRenderer.");
        }
        /** @type {THREE.Scene} */
        this.scene = scene;
        /** @type {THREE.WebGLRenderer} */
        this.renderer = renderer;
        
        // Habilitar sombras en el renderizador
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        /** @type {THREE.AmbientLight|null} */
        this.ambientLight = null;
        /** @type {THREE.DirectionalLight|null} */
        this.directionalLight = null;
        /** @type {THREE.Texture|null} */
        this.hdriTexture = null;
    }

    /**
     * Inyecta una iluminación base y carga un entorno de iluminación física realista
     * @param {string} [hdriUrl] - URL opcional del archivo .hdr para el mapa de entorno
     * @returns {Promise<void>}
     */
    async init(hdriUrl = null) {
        this.setupAmbientLight();
        this.setupDirectionalLight();
        
        if (hdriUrl) {
            try {
                await this.loadHDRI(hdriUrl);
            } catch (error) {
                console.error("[LightingSetup] Falló la carga del entorno HDRI. Usando luces estándar.", error);
            }
        }
    }

    /**
     * Configura e inyecta la luz ambiental de relleno
     * @param {number} [color=0xffffff] - Color hexadecimal de la luz
     * @param {number} [intensity=0.35] - Intensidad luminosa
     */
    setupAmbientLight(color = 0xffffff, intensity = 0.35) {
        if (this.ambientLight) {
            this.scene.remove(this.ambientLight);
        }
        
        this.ambientLight = new THREE.AmbientLight(color, intensity);
        this.ambientLight.name = "system_ambient_light";
        this.scene.add(this.ambientLight);
        
        console.log(`[Lighting] Luz ambiental configurada con éxito. Intensidad: ${intensity}`);
    }

    /**
     * Configura la luz direccional principal y el frustum de sombras de alta definición
     * @param {number} [color=0xfffdfa] - Color blanco cálido por defecto
     * @param {number} [intensity=1.1] - Intensidad para un brillo PBR vibrante
     * @param {THREE.Vector3} [position] - Posición espacial de la fuente
     */
    setupDirectionalLight(color = 0xfffdfa, intensity = 1.1, position = new THREE.Vector3(15, 25, 15)) {
        if (this.directionalLight) {
            this.scene.remove(this.directionalLight);
        }
        
        const light = new THREE.DirectionalLight(color, intensity);
        light.position.copy(position);
        light.name = "system_directional_light";
        
        // Habilitar sombras en la luz direccional
        light.castShadow = true;
        
        // Optimizar resolución del mapa de sombras (2048 x 2048 para bordes suaves y definidos)
        light.shadow.mapSize.width = 2048;
        light.shadow.mapSize.height = 2048;
        
        // Definir frustum de la cámara de sombras adaptativo al escenario
        const shadowCam = light.shadow.camera;
        shadowCam.near = 0.5;
        shadowCam.far = 100;
        shadowCam.left = -25;
        shadowCam.right = 25;
        shadowCam.top = 25;
        shadowCam.bottom = -25;
        
        // Reducir artefactos visuales (peter panning / shadow acne) aplicando un leve offset
        light.shadow.bias = -0.0003;
        light.shadow.normalBias = 0.02;
        
        this.directionalLight = light;
        this.scene.add(light);
        
        console.log(`[Lighting] Luz direccional configurada con sombras HD de 2048x2048.`);
    }

    /**
     * Carga y decodifica asíncronamente una textura de rango dinámico HDRI para generar
     * reflejos físicos realistas asignados a la propiedad scene.environment de Three.js
     * @param {string} url - URL absoluta o relativa del archivo HDR (.hdr)
     * @returns {Promise<THREE.Texture>}
     */
    loadHDRI(url) {
        return new Promise((resolve, reject) => {
            const loader = new RGBELoader();
            loader.setDataType(THREE.UnsignedByteType);
            
            console.log(`[Lighting] Cargando textura HDR desde: ${url}... ⏳`);
            
            loader.load(url, (texture) => {
                const pmremGenerator = new THREE.PMREMGenerator(this.renderer);
                pmremGenerator.compileEquirectangularShader();
                
                // Procesar la textura esférica equirectangular
                const envMapRenderTarget = pmremGenerator.fromEquirectangular(texture);
                
                // Asignar el entorno físico generado a la escena
                this.scene.environment = envMapRenderTarget.texture;
                
                // Limpieza de memoria para prevenir fugas
                texture.dispose();
                pmremGenerator.dispose();
                
                this.hdriTexture = envMapRenderTarget.texture;
                console.log(`[Lighting] Entorno HDRI cargado y procesado de forma exitosa. PMREM compilado.`);
                resolve(envMapRenderTarget.texture);
            }, 
            (xhr) => {
                // Progreso de descarga opcional en consola
                if (xhr.total > 0) {
                    const pct = Math.round((xhr.loaded / xhr.total) * 100);
                    console.log(`[Lighting] Descargando HDR: ${pct}%`);
                }
            }, 
            (error) => {
                reject(error);
            });
        });
    }

    /**
     * Limpia y destruye las referencias a las luces y entornos creados
     */
    dispose() {
        if (this.ambientLight) this.scene.remove(this.ambientLight);
        if (this.directionalLight) this.scene.remove(this.directionalLight);
        if (this.scene.environment) {
            this.scene.environment.dispose();
            this.scene.environment = null;
        }
        if (this.hdriTexture) {
            this.hdriTexture.dispose();
            this.hdriTexture = null;
        }
        console.log("[Lighting] Recursos de iluminación y entorno PBR destruidos.");
    }
}
