import bpy
import os
import sys

def main():
    try:
        print("=== Iniciando compresión Draco del modelo Blue Whale ===")
        
        # 1. Limpiar escena
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # 2. Importar GLB original
        input_path = os.path.abspath(os.path.join("output", "blue whale 3d model.glb"))
        print(f"Importando modelo original desde: {input_path}")
        bpy.ops.import_scene.gltf(filepath=input_path)
        
        # 3. Exportar con compresión Draco habilitada
        output_path = os.path.abspath(os.path.join("output", "blue whale 3d model.glb"))
        print(f"Exportando modelo optimizado a: {output_path}")
        
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
            export_apply=True
        )
        
        print("=== COMPRESIÓN COMPLETADA EXITOSAMENTE ===")
        sys.exit(0)
    except Exception as e:
        print(f"=== ERROR EN LA COMPRESIÓN: {str(e)} ===", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
