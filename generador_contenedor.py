import bpy
import math

# 1. Limpiar la escena por defecto (borrar el cubo, luces y cámara iniciales)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Crear las proporciones de un contenedor estándar de 20 pies
# Dimensiones en metros: Ancho: 2.44m, Largo: 6.06m, Alto: 2.59m
bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 1.295))
contenedor = bpy.context.active_object
contenedor.name = "Contenedor_Docker"

# Escalar a las dimensiones reales (Blender usa el sistema métrico por defecto)
contenedor.scale[0] = 2.44  # Eje X (Ancho)
contenedor.scale[1] = 6.06  # Eje Y (Largo)
contenedor.scale[2] = 2.59  # Eje Z (Alto)

# Aplicar la escala para que la geometría base sea definitiva
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 3. Darle un toque limpio para AR (Biselar los bordes)
bevel_mod = contenedor.modifiers.new(name="Biselado_Suave", type='BEVEL')
bevel_mod.width = 0.05
bevel_mod.segments = 3

# 4. Asignar un color base (Azul Docker clásico)
material_docker = bpy.data.materials.new(name="Material_Azul_Docker")
material_docker.use_nodes = True
bsdf = material_docker.node_tree.nodes.get("Principled BSDF")

# RGBA para el color azul (los valores van de 0.0 a 1.0)
bsdf.inputs['Base Color'].default_value = (0.04, 0.38, 0.85, 1.0) 
bsdf.inputs['Roughness'].default_value = 0.6 # Hacerlo un poco mate

contenedor.data.materials.append(material_docker)

# 5. Exportar el modelo a formato .glb en el mismo directorio de ejecución
ruta_exportacion = "contenedor_docker_ar.glb"
bpy.ops.export_scene.gltf(
    filepath=ruta_exportacion,
    export_format='GLB',
    use_selection=False,  # Exportar toda la escena
    export_apply=True     # Aplicar el modificador de biselado al exportar
)

print(f"=== ÉXITO: El modelo se ha exportado como {ruta_exportacion} ===")