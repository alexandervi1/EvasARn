import bpy
import os
import sys

def main():
    try:
        print("=== Iniciando la generación del modelo Servidor Rack ===")
        
        # 1. Limpiar escena
        print("Limpiando escena...")
        if bpy.ops.object.select_all:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

        # 2. Crear el chasis principal del Rack (bloque vertical alto)
        print("Creando chasis del rack...")
        # Dimensiones aproximadas: Ancho: 0.6m, Largo/Profundo: 0.8m, Alto: 1.8m
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.9))
        rack = bpy.context.active_object
        rack.name = "Rack_Chasis"
        rack.scale = (0.6, 0.8, 1.8)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # 3. Configurar materiales comunes
        print("Configurando materiales...")
        # Material Chasis Rack (Metal Oscuro)
        mat_rack = bpy.data.materials.new(name="Mat_Rack_Metal")
        mat_rack.use_nodes = True
        bsdf_rack = mat_rack.node_tree.nodes.get("Principled BSDF")
        if bsdf_rack:
            bsdf_rack.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
            bsdf_rack.inputs['Roughness'].default_value = 0.6
            bsdf_rack.inputs['Metallic'].default_value = 0.8
        rack.data.materials.append(mat_rack)

        # Material Blades/Bandejas (Metal un poco más claro)
        mat_blade = bpy.data.materials.new(name="Mat_Blade_Metal")
        mat_blade.use_nodes = True
        bsdf_blade = mat_blade.node_tree.nodes.get("Principled BSDF")
        if bsdf_blade:
            bsdf_blade.inputs['Base Color'].default_value = (0.18, 0.18, 0.18, 1.0)
            bsdf_blade.inputs['Roughness'].default_value = 0.4
            bsdf_blade.inputs['Metallic'].default_value = 0.9

        # Material LED Verde Neón Emisivo
        mat_led = bpy.data.materials.new(name="Mat_LED_Verde")
        mat_led.use_nodes = True
        bsdf_led = mat_led.node_tree.nodes.get("Principled BSDF")
        if bsdf_led:
            color_led = (0.0, 1.0, 0.1, 1.0)
            bsdf_led.inputs['Base Color'].default_value = color_led
            for input_name in ['Emission Color', 'Emission', 'Emission color']:
                if input_name in bsdf_led.inputs:
                    bsdf_led.inputs[input_name].default_value = color_led
            if 'Emission Strength' in bsdf_led.inputs:
                bsdf_led.inputs['Emission Strength'].default_value = 5.0
            bsdf_led.inputs['Roughness'].default_value = 0.1

        # 4. Crear los 6 módulos/blades de servidor en la parte frontal (Y = 0.4m)
        print("Creando bandejas de servidores y LEDs...")
        for i in range(6):
            # Posición en Z de cada bandeja, distribuida entre 0.2m y 1.6m
            z_pos = 0.2 + i * 0.28
            
            # Crear la bandeja del servidor
            bpy.ops.mesh.primitive_cube_add(size=1)
            blade = bpy.context.active_object
            blade.name = f"Server_Blade_{i+1}"
            blade.scale = (0.54, 0.04, 0.20)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            blade.parent = rack
            # Colocar en la cara frontal (Y local = 0.38)
            blade.location = (0, 0.385, z_pos - 0.9)
            blade.data.materials.append(mat_blade)
            
            # Crear 3 pequeños LEDs en la parte izquierda frontal de cada bandeja
            for led_idx, x_offset in enumerate([-0.22, -0.17, -0.12]):
                bpy.ops.mesh.primitive_cube_add(size=1)
                led = bpy.context.active_object
                led.name = f"Blade_{i+1}_LED_{led_idx+1}"
                led.scale = (0.015, 0.01, 0.015)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                led.parent = blade
                # Colocar en la cara frontal de la bandeja
                led.location = (x_offset, 0.021, 0)
                led.data.materials.append(mat_led)

        # 5. Exportar modelo GLB
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        ruta_exportacion = os.path.abspath(os.path.join(output_dir, "servidor_rack.glb"))
        print(f"Exportando a {ruta_exportacion}...")
        
        bpy.ops.export_scene.gltf(
            filepath=ruta_exportacion,
            export_format='GLB',
            use_selection=False,
            export_apply=True
        )

        print(f"=== ÉXITO: Modelo servidor_rack.glb generado en {ruta_exportacion} ===")
        sys.exit(0)

    except Exception as e:
        print(f"=== ERROR CRÍTICO EN gen_server.py: {str(e)} ===", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
