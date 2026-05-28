import bpy
import os
import sys

def crear_material(nombre, color_rgb, roughness=0.5, metallic=0.1):
    """
    Crea un material Principled BSDF compatible con múltiples versiones de Blender.
    """
    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color_rgb
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

def crear_contenedor_detallado(nombre, loc, color_rgb, cuerpo_ballena):
    """
    Crea proceduralmente un contenedor de carga ultra detallado con relieves
    verticales (ribs) y postes de esquina, tal como la imagen de referencia.
    """
    # 1. Crear el material
    mat = crear_material(f"Mat_{nombre}", color_rgb, roughness=0.55, metallic=0.05)
    
    # 2. Caja principal del contenedor
    # Ancho (X): 0.72, Largo (Y): 1.15, Alto (Z): 0.62
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    c_box = bpy.context.active_object
    c_box.name = nombre
    c_box.scale = (0.72, 1.15, 0.62)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c_box.data.materials.append(mat)
    c_box.parent = cuerpo_ballena
    
    # 3. Añadir costillas/relieves laterales verticales (Ribs)
    # Lado izquierdo (X = -0.36) y Lado derecho (X = 0.36)
    # Colocaremos 6 costillas distribuidas en el eje Y de cada lado
    y_posiciones = [-0.44, -0.26, -0.09, 0.09, 0.26, 0.44]
    
    for lado in [-1, 1]:
        for y_pos in y_posiciones:
            bpy.ops.mesh.primitive_cube_add(size=1)
            rib = bpy.context.active_object
            rib.name = f"{nombre}_rib_{lado}_{y_pos}"
            # Dimensión del relieve: muy delgado en X, corto en Y, casi altura completa en Z
            rib.scale = (0.018, 0.04, 0.58)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            rib.parent = c_box
            rib.location = (lado * 0.362, y_pos, 0)
            rib.data.materials.append(mat)
            
    # 4. Añadir marcos y postes de esquina para aspecto industrial real
    # Postes de esquina (4 esquinas en X = +-0.36, Y = +-0.575)
    for x_esq in [-1, 1]:
        for y_esq in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(size=1)
            poste = bpy.context.active_object
            poste.name = f"{nombre}_poste_{x_esq}_{y_esq}"
            poste.scale = (0.04, 0.04, 0.62)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            poste.parent = c_box
            poste.location = (x_esq * 0.34, y_esq * 0.555, 0)
            poste.data.materials.append(mat)

    # 5. Marcos horizontales superior e inferior
    for z_lado in [-1, 1]:
        # Marcos transversales (X)
        for y_lado in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(size=1)
            marco_x = bpy.context.active_object
            marco_x.name = f"{nombre}_marcox_{z_lado}_{y_lado}"
            marco_x.scale = (0.72, 0.04, 0.04)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            marco_x.parent = c_box
            marco_x.location = (0, y_lado * 0.555, z_lado * 0.29)
            marco_x.data.materials.append(mat)
            
    return c_box

def main():
    try:
        print("=== Iniciando la generación de la Ballena Docker Fiel a Medios ===")
        
        # 1. Limpiar escena
        print("Limpiando escena...")
        if bpy.ops.object.select_all:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

        # 2. Configurar materiales para la ballena y ojos
        print("Configurando materiales del avatar...")
        mat_azul_ballena = crear_material("Mat_Ballena_Azul", (0.05, 0.42, 0.88, 1.0), roughness=0.35, metallic=0.15)
        mat_blanco_panza = crear_material("Mat_Panza_Blanca", (0.92, 0.94, 0.96, 1.0), roughness=0.50, metallic=0.0)
        mat_ojo_negro = crear_material("Mat_Ojo_Negro", (0.01, 0.01, 0.01, 1.0), roughness=0.05, metallic=0.1)

        # 3. Modelar Cuerpo de la Ballena (Dos tonos: Azul arriba, Blanco abajo)
        print("Modelando cuerpo de la ballena en dos tonos...")
        
        # Cuerpo Superior (Azul)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.1))
        cuerpo_azul = bpy.context.active_object
        cuerpo_azul.name = "Ballena_Cuerpo_Azul"
        cuerpo_azul.scale = (1.25, 2.25, 0.8)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        subdiv_azul = cuerpo_azul.modifiers.new(name="Subdiv_Azul", type='SUBSURF')
        subdiv_azul.levels = 3
        subdiv_azul.render_levels = 3
        cuerpo_azul.data.materials.append(mat_azul_ballena)

        # Cuerpo Inferior/Panza (Blanco)
        # Ligeramente desplazado hacia abajo y adelante para esculpir el vientre
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.05, 0.72))
        cuerpo_blanco = bpy.context.active_object
        cuerpo_blanco.name = "Ballena_Cuerpo_Blanco"
        cuerpo_blanco.scale = (1.22, 2.1, 0.52)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        subdiv_blanco = cuerpo_blanco.modifiers.new(name="Subdiv_Blanco", type='SUBSURF')
        subdiv_blanco.levels = 3
        subdiv_blanco.render_levels = 3
        cuerpo_blanco.data.materials.append(mat_blanco_panza)
        cuerpo_blanco.parent = cuerpo_azul

        # 4. Modelar Aleta de Cola (Horizontal y elegante)
        print("Modelando aleta trasera de cola...")
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.85, 1.1))
        cola = bpy.context.active_object
        cola.name = "Ballena_Cola"
        cola.scale = (1.65, 0.45, 0.08)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        subdiv_cola = cola.modifiers.new(name="Subdiv_Cola", type='SUBSURF')
        subdiv_cola.levels = 2
        cola.parent = cuerpo_azul
        cola.data.materials.append(mat_azul_ballena)

        # 5. Modelar Aletas Laterales (Sweeping Flippers)
        print("Modelando aletas laterales estilizadas...")
        # Aleta Izquierda
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.82, 0.4, 0.8))
        aleta_izq = bpy.context.active_object
        aleta_izq.name = "Aleta_Izq"
        aleta_izq.scale = (0.58, 0.5, 0.08)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        aleta_izq.rotation_euler = (0.15, 0.25, -0.45)
        subdiv_izq = aleta_izq.modifiers.new(name="Subdiv_Izq", type='SUBSURF')
        subdiv_izq.levels = 2
        aleta_izq.parent = cuerpo_azul
        aleta_izq.data.materials.append(mat_azul_ballena)

        # Aleta Derecha
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.82, 0.4, 0.8))
        aleta_der = bpy.context.active_object
        aleta_der.name = "Aleta_Der"
        aleta_der.scale = (0.58, 0.5, 0.08)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        aleta_der.rotation_euler = (0.15, -0.25, 0.45)
        subdiv_der = aleta_der.modifiers.new(name="Subdiv_Der", type='SUBSURF')
        subdiv_der.levels = 2
        aleta_der.parent = cuerpo_azul
        aleta_der.data.materials.append(mat_azul_ballena)

        # 6. Ojos Estilizados (Negros brillantes a los costados)
        print("Añadiendo ojos...")
        # Ojo Izquierdo
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(-0.56, 0.82, 1.05))
        ojo_izq = bpy.context.active_object
        ojo_izq.name = "Ojo_Izq"
        ojo_izq.parent = cuerpo_azul
        ojo_izq.data.materials.append(mat_ojo_negro)

        # Ojo Derecho
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0.56, 0.82, 1.05))
        ojo_der = bpy.context.active_object
        ojo_der.name = "Ojo_Der"
        ojo_der.parent = cuerpo_azul
        ojo_der.data.materials.append(mat_ojo_negro)

        # 7. Modelar y Apilar la Pirámide de 5 Contenedores sobre el lomo
        print("Generando la pirámide industrial de 5 contenedores en el lomo...")
        # Definición de la pirámide:
        # Nivel 1 (Base): Z = 1.34
        # - Adelante (Y = 0.58): Celeste (Cyan)
        # - Atrás (Y = -0.58): Azul Oscuro
        # Nivel 2 (Medio): Z = 1.96
        # - Adelante (Y = 0.58): Amarillo
        # - Atrás (Y = -0.58): Morado
        # Nivel 3 (Cima): Z = 2.58
        # - Centro (Y = 0.0): Rojo
        
        # Colores RGB de la imagen de medios
        color_celeste = (0.18, 0.74, 0.78, 1.0)
        color_azul_osc = (0.12, 0.32, 0.76, 1.0)
        color_amarillo = (0.90, 0.70, 0.15, 1.0)
        color_morado = (0.46, 0.22, 0.68, 1.0)
        color_rojo = (0.86, 0.16, 0.16, 1.0)

        # Nivel 1: Base
        print("Añadiendo nivel inferior (Celeste y Azul Oscuro)...")
        crear_contenedor_detallado("Cont_Celeste", (0.0, 0.58, 1.34), color_celeste, cuerpo_azul)
        crear_contenedor_detallado("Cont_AzulOsc", (0.0, -0.58, 1.34), color_azul_osc, cuerpo_azul)

        # Nivel 2: Medio
        print("Añadiendo nivel medio (Amarillo y Morado)...")
        crear_contenedor_detallado("Cont_Amarillo", (0.0, 0.58, 1.96), color_amarillo, cuerpo_azul)
        crear_contenedor_detallado("Cont_Morado", (0.0, -0.58, 1.96), color_morado, cuerpo_azul)

        # Nivel 3: Cima
        print("Añadiendo cima (Rojo)...")
        crear_contenedor_detallado("Cont_Rojo", (0.0, 0.0, 2.58), color_rojo, cuerpo_azul)

        # 8. Exportar modelo completo a GLB
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        ruta_exportacion = os.path.abspath(os.path.join(output_dir, "ballena_docker.glb"))
        print(f"Exportando modelo unificado de alta fidelidad a: {ruta_exportacion}...")
        
        bpy.ops.export_scene.gltf(
            filepath=ruta_exportacion,
            export_format='GLB',
            use_selection=False,
            export_apply=True
        )

        print(f"=== ÉXITO: Modelo de alta fidelidad ballena_docker.glb generado exitosamente ===")
        sys.exit(0)

    except Exception as e:
        print(f"=== ERROR CRÍTICO EN gen_ballena.py: {str(e)} ===", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
