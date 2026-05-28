import os
import pytest
from server import generar_modelo_docker_3d

def test_generar_modelo_docker_3d():
    """
    Prueba de integración que invoca directamente a la herramienta expuesta
    por el servidor MCP, asegurándose de que ejecuta Blender correctamente,
    retorna un mensaje exitoso y crea el archivo GLB esperado.
    """
    output_dir = "output"
    output_glb = os.path.join(output_dir, "contenedor_docker.glb")
    
    # 1. Preparar entorno: Eliminar el archivo de salida si ya existe para asegurar prueba limpia
    if os.path.exists(output_glb):
        os.remove(output_glb)
        print(f"Limpieza previa: Se eliminó {output_glb}")

    # 2. Ejecutar la herramienta expuesta por el servidor MCP
    print("Iniciando la llamada a la herramienta MCP 'generar_modelo_docker_3d'...")
    resultado = generar_modelo_docker_3d()
    print("Resultado obtenido de la herramienta:")
    print(resultado)
    
    # 3. Aserciones para asegurar el comportamiento esperado
    # Verificar que el resultado retornado indica éxito
    assert "Éxito" in resultado, f"La herramienta no reportó éxito. Mensaje devuelto: {resultado}"
    
    # Verificar que el archivo GLB de salida fue efectivamente creado
    assert os.path.exists(output_glb), f"El archivo de salida '{output_glb}' no fue creado."
    
    # Verificar que el archivo no está vacío
    file_size = os.path.getsize(output_glb)
    print(f"Archivo GLB creado exitosamente con tamaño: {file_size} bytes")
    assert file_size > 0, "El archivo GLB generado tiene un tamaño de 0 bytes."
