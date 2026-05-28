import bpy
import os
import sys
import math

def main():
    try:
        print("=== Iniciando la generación del modelo Laptop Caos ===")
        
        # 1. Limpiar escena
        print("Limpiando escena...")
        if bpy.ops.object.select_all:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

        # 2. Crear chasis de la base
        print("Creando base de la laptop...")
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.0075))
        base = bpy.context.active_object
        base.name = "Laptop_Base"
        base.scale = (0.35, 0.25, 0.015)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # 3. Crear chasis de la pantalla (inclinada hacia atrás ~15 grados)
        print("Creando marco de la pantalla...")
        # Colocar el pivote/posición inicial cerca de la bisagra trasera (Y = -0.11, Z = 0.13)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.11, 0.13))
        screen_frame = bpy.context.active_object
        screen_frame.name = "Laptop_Screen_Frame"
        screen_frame.scale = (0.35, 0.015, 0.25)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # Rotar alrededor de X para dar efecto de abierta
        screen_frame.rotation_euler[0] = math.radians(-15)

        # 4. Crear panel de pantalla emisivo (rojo brillante / error)
        print("Creando pantalla emisiva...")
        bpy.ops.mesh.primitive_cube_add(size=1)
        display = bpy.context.active_object
        display.name = "Laptop_Display"
        display.scale = (0.32, 0.005, 0.22)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # Emparentar a la pantalla para que rote y se mueva solidariamente
        display.parent = screen_frame
        # Desplazar localmente ligeramente hacia el frente en el eje Y local
        display.location = (0, 0.008, 0)

        # 5. Crear detalles: Teclado y Trackpad (opcional low-poly)
        print("Creando detalles de teclado y trackpad...")
        # Teclado
        bpy.ops.mesh.primitive_cube_add(size=1)
        keyboard = bpy.context.active_object
        keyboard.name = "Laptop_Keyboard"
        keyboard.scale = (0.30, 0.12, 0.002)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        keyboard.parent = base
        keyboard.location = (0, -0.03, 0.008)

        # Trackpad
        bpy.ops.mesh.primitive_cube_add(size=1)
        trackpad = bpy.context.active_object
        trackpad.name = "Laptop_Trackpad"
        trackpad.scale = (0.08, 0.05, 0.002)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        trackpad.parent = base
        trackpad.location = (0, 0.07, 0.008)

        # 6. Crear y asignar materiales
        print("Configurando materiales...")
        # Material Chasis (Gris oscuro mate)
        mat_chasis = bpy.data.materials.new(name="Mat_Chasis_Gris")
        mat_chasis.use_nodes = True
        bsdf_chasis = mat_chasis.node_tree.nodes.get("Principled BSDF")
        if bsdf_chasis:
            bsdf_chasis.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1.0)
            bsdf_chasis.inputs['Roughness'].default_value = 0.8
            bsdf_chasis.inputs['Metallic'].default_value = 0.2
        base.data.materials.append(mat_chasis)
        screen_frame.data.materials.append(mat_chasis)

        # Material Detalles (Gris muy oscuro/Negro)
        mat_detalles = bpy.data.materials.new(name="Mat_Teclado_Negro")
        mat_detalles.use_nodes = True
        bsdf_detalles = mat_detalles.node_tree.nodes.get("Principled BSDF")
        if bsdf_detalles:
            bsdf_detalles.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
            bsdf_detalles.inputs['Roughness'].default_value = 0.9
        keyboard.data.materials.append(mat_detalles)
        trackpad.data.materials.append(mat_detalles)

        # Material Pantalla Emisiva (Rojo brillante / Estado de Error)
        mat_display = bpy.data.materials.new(name="Mat_Display_Emisivo")
        mat_display.use_nodes = True
        bsdf_display = mat_display.node_tree.nodes.get("Principled BSDF")
        if bsdf_display:
            # Color base rojo/naranja
            color_error = (1.0, 0.05, 0.05, 1.0)
            bsdf_display.inputs['Base Color'].default_value = color_error
            # Soporte de emisión para múltiples versiones de Blender
            for input_name in ['Emission Color', 'Emission', 'Emission color']:
                if input_name in bsdf_display.inputs:
                    bsdf_display.inputs[input_name].default_value = color_error
            if 'Emission Strength' in bsdf_display.inputs:
                bsdf_display.inputs['Emission Strength'].default_value = 4.0
            bsdf_display.inputs['Roughness'].default_value = 0.2
        display.data.materials.append(mat_display)

        # 7. Exportar modelo GLB
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        ruta_exportacion = os.path.abspath(os.path.join(output_dir, "laptop_caos.glb"))
        print(f"Exportando a {ruta_exportacion}...")
        
        bpy.ops.export_scene.gltf(
            filepath=ruta_exportacion,
            export_format='GLB',
            use_selection=False,
            export_apply=True
        )

        print(f"=== ÉXITO: Modelo laptop_caos.glb generado en {ruta_exportacion} ===")
        sys.exit(0)

    except Exception as e:
        print(f"=== ERROR CRÍTICO EN gen_laptop.py: {str(e)} ===", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
