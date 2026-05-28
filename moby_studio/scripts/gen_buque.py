import bpy
import os
import sys

def crear_material(nombre, color_rgb, roughness=0.5, metallic=0.1):
    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color_rgb
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

def crear_contenedor_cubierta(nombre, loc, escala, color_rgb, buque_cuerpo):
    """
    Crea un contenedor de carga simplificado con relieve vertical
    para encajar estéticamente sobre la cubierta del buque.
    """
    mat = crear_material(f"Mat_{nombre}", color_rgb, roughness=0.5, metallic=0.0)
    
    # Cubo base del contenedor
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    c_box = bpy.context.active_object
    c_box.name = nombre
    c_box.scale = escala
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    c_box.data.materials.append(mat)
    c_box.parent = buque_cuerpo
    
    # Relieves laterales (Ribs)
    # 4 relieves distribuidos a lo largo del eje Y (escala de contenedor más pequeña)
    y_posiciones = [-0.18, -0.06, 0.06, 0.18]
    x_semiancho = escala[0] * 0.5
    z_alto = escala[2] * 0.95
    
    for lado in [-1, 1]:
        for y_pos in y_posiciones:
            bpy.ops.mesh.primitive_cube_add(size=1)
            rib = bpy.context.active_object
            rib.name = f"{nombre}_rib_{lado}_{y_pos}"
            rib.scale = (0.015, 0.03, z_alto)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            rib.parent = c_box
            rib.location = (lado * x_semiancho, y_pos, 0)
            rib.data.materials.append(mat)
            
    # Postes de esquina
    for x_esq in [-1, 1]:
        for y_esq in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(size=1)
            poste = bpy.context.active_object
            poste.name = f"{nombre}_poste_{x_esq}_{y_esq}"
            poste.scale = (0.03, 0.03, escala[2])
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            poste.parent = c_box
            poste.location = (x_esq * (x_semiancho - 0.01), y_esq * (escala[1]*0.5 - 0.01), 0)
            poste.data.materials.append(mat)

    return c_box

def main():
    try:
        print("=== Iniciando la generación del modelo Buque de Carga ===")
        
        # 1. Limpiar escena
        print("Limpiando escena...")
        if bpy.ops.object.select_all:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

        # 2. Configurar materiales del buque
        print("Configurando materiales del casco...")
        mat_rojo_casco = crear_material("Mat_Rojo_Casco", (0.55, 0.08, 0.08, 1.0), roughness=0.6, metallic=0.2)
        mat_negro_casco = crear_material("Mat_Negro_Casco", (0.08, 0.08, 0.08, 1.0), roughness=0.5, metallic=0.3)
        mat_blanco_cabina = crear_material("Mat_Blanco_Cabina", (0.9, 0.9, 0.9, 1.0), roughness=0.4, metallic=0.0)
        mat_ventanas = crear_material("Mat_Ventanas", (0.05, 0.1, 0.2, 1.0), roughness=0.1, metallic=0.9)

        # 3. Modelar Casco del Buque
        # Cuerpo del casco inferior (Rojo)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.1))
        casco_rojo = bpy.context.active_object
        casco_rojo.name = "Buque_Casco_Rojo"
        casco_rojo.scale = (0.8, 3.0, 0.2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        casco_rojo.data.materials.append(mat_rojo_casco)

        # Cuerpo del casco superior (Negro)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.3))
        casco_negro = bpy.context.active_object
        casco_negro.name = "Buque_Casco_Negro"
        casco_negro.scale = (0.8, 3.0, 0.2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        casco_negro.parent = casco_rojo
        casco_negro.data.materials.append(mat_negro_casco)

        # Proa puntiaguda (pointed bow using a rotated 4-vertex cone)
        print("Modelando proa del buque...")
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.56, radius2=0.0, depth=0.4, location=(0, 1.7, 0.2), rotation=(0, 0, 0.785))
        proa = bpy.context.active_object
        proa.name = "Buque_Proa"
        proa.scale = (1.0, 1.0, 1.0)
        proa.parent = casco_rojo
        proa.data.materials.append(mat_negro_casco)

        # 4. Modelar Cabina / Puente de Mando (Blanco)
        print("Modelando puente de mando...")
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.0, 0.6))
        cabina = bpy.context.active_object
        cabina.name = "Buque_Cabina"
        cabina.scale = (0.68, 0.65, 0.4)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        cabina.parent = casco_rojo
        cabina.data.materials.append(mat_blanco_cabina)

        # Chimenea en el puente (Rojo)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.25, location=(0, -1.18, 0.9))
        chimenea = bpy.context.active_object
        chimenea.name = "Buque_Chimenea"
        chimenea.parent = cabina
        chimenea.data.materials.append(mat_rojo_casco)

        # Ventanas del puente (Bloques azules oscuros finos)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.67, 0.68))
        ventana = bpy.context.active_object
        ventana.name = "Buque_Ventana"
        ventana.scale = (0.55, 0.01, 0.12)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        ventana.parent = cabina
        ventana.data.materials.append(mat_ventanas)

        # 5. Cargar contenedores de colores sobre la cubierta (2 pilas de 2)
        print("Apilando contenedores en cubierta...")
        color_celeste = (0.18, 0.74, 0.78, 1.0)
        color_amarillo = (0.90, 0.70, 0.15, 1.0)
        color_azul_osc = (0.12, 0.32, 0.76, 1.0)
        color_rojo = (0.86, 0.16, 0.16, 1.0)
        
        dim_cont = (0.58, 0.58, 0.36)

        # Pila delantera (Y = 0.7)
        # Abajo Celeste
        crear_contenedor_cubierta("Pila_Celeste", (0.0, 0.7, 0.58), dim_cont, color_celeste, casco_rojo)
        # Arriba Amarillo
        crear_contenedor_cubierta("Pila_Amarillo", (0.0, 0.7, 0.94), dim_cont, color_amarillo, casco_rojo)

        # Pila media (Y = 0.0)
        # Abajo Azul Oscuro
        crear_contenedor_cubierta("Pila_Azul", (0.0, 0.0, 0.58), dim_cont, color_azul_osc, casco_rojo)
        # Arriba Rojo
        crear_contenedor_cubierta("Pila_Rojo", (0.0, 0.0, 0.94), dim_cont, color_rojo, casco_rojo)

        # 6. Exportar buque completo a GLB
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        ruta_exportacion = os.path.abspath(os.path.join(output_dir, "buque_carga.glb"))
        print(f"Exportando buque a: {ruta_exportacion}...")
        
        bpy.ops.export_scene.gltf(
            filepath=ruta_exportacion,
            export_format='GLB',
            use_selection=False,
            export_apply=True
        )

        print(f"=== ÉXITO: Modelo buque_carga.glb generado exitosamente ===")
        sys.exit(0)

    except Exception as e:
        print(f"=== ERROR CRÍTICO EN gen_buque.py: {str(e)} ===", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
