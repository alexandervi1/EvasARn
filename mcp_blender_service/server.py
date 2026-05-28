import os
import subprocess
import shutil
import glob
from mcp.server.fastmcp import FastMCP

# Inicializar el servidor MCP llamado Blender_AR_Generator
mcp = FastMCP("Blender_AR_Generator")

def find_blender():
    """
    Busca de manera robusta el ejecutable de Blender en el sistema.
    Primero busca en el PATH del sistema, luego en ubicaciones por defecto de Windows.
    """
    # 1. Buscar en el PATH de manera nativa
    path_blender = shutil.which("blender")
    if path_blender:
        return path_blender
    
    # 2. Buscar en directorios estándar de Windows
    if os.name == 'nt':
        search_patterns = [
            r"C:\Program Files\Blender Foundation\Blender *\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender *\blender.exe",
            r"C:\Program Files\Blender Foundation\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\blender.exe"
        ]
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            if matches:
                # Devolver el ejecutable de la versión más reciente encontrada
                return sorted(matches)[-1]
                
    # Fallback por defecto si no se encuentra en las rutas comunes
    return "blender"

@mcp.tool()
def generar_modelo_docker_3d() -> str:
    """
    Genera un modelo 3D GLB de un contenedor Docker estándar de 20 pies con biselado suave
    y material azul mate utilizando Blender en modo headless.
    
    Retorna la ruta absoluta del archivo .glb generado.
    """
    blender_exe = find_blender()
    script_path = os.path.abspath(os.path.join("scripts", "generar_contenedor.py"))
    output_glb = os.path.abspath(os.path.join("output", "contenedor_docker.glb"))
    
    # Validar que el script core exista
    if not os.path.exists(script_path):
        return f"Error: No se encontró el script core de Blender en '{script_path}'"

    # Comando a ejecutar
    # Ejecuta Blender en modo headless (--background) pasándole el script de python (--python)
    cmd = [
        blender_exe,
        "--background",
        "--python",
        script_path
    ]
    
    print(f"Ejecutando subproceso: {' '.join(cmd)}")
    
    try:
        # Ejecutar el subproceso capturando stdout y stderr
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # No lanzamos excepción automática para manejar el código de salida
        )
        
        # Guardar logs de Blender para debugging o reporte
        logs_stdout = result.stdout or ""
        logs_stderr = result.stderr or ""
        
        if result.returncode == 0:
            # Éxito: Validar que el archivo .glb realmente se generó
            if os.path.exists(output_glb):
                return (
                    f"Éxito: Modelo GLB generado correctamente.\n"
                    f"Ruta absoluta: {output_glb}\n"
                    f"Logs de salida:\n{logs_stdout[-1000:]}"
                )
            else:
                return (
                    f"Error: Blender finalizó con código 0 pero el archivo '{output_glb}' no fue creado.\n"
                    f"Logs de salida:\n{logs_stdout[-1000:]}"
                )
        else:
            # Fallo: Retornar los logs de error detallados
            return (
                f"Error: Blender falló al ejecutarse (Código de salida: {result.returncode}).\n"
                f"Detalle de stderr:\n{logs_stderr}\n"
                f"Detalle de stdout:\n{logs_stdout[-2000:]}"
            )
            
    except FileNotFoundError:
        return (
            f"Error: No se pudo encontrar el ejecutable de Blender ({blender_exe}).\n"
            f"Por favor, asegúrate de que Blender esté instalado y que 'blender' esté en el PATH o en la ruta de instalación por defecto de Windows."
        )
    except Exception as e:
        return f"Error inesperado al ejecutar el subproceso de Blender: {str(e)}"

if __name__ == "__main__":
    mcp.run()
