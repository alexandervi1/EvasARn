import sys
import os

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import lanzador_ar

# Imagen base64 mínima (1x1 pixel negro)
import base64
from io import BytesIO

# Cargar y codificar la imagen real de medios/image.png
ruta_imagen = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medios", "image.png"))

if os.path.exists(ruta_imagen):
    print(f"[OK] Cargando imagen real de prueba: {ruta_imagen}")
    with open(ruta_imagen, "rb") as image_file:
        dummy_base64 = "data:image/png;base64," + base64.b64encode(image_file.read()).decode('utf-8')
else:
    print(f"[Aviso] No se encontró {ruta_imagen}. Usando fallback en blanco...")
    try:
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        dummy_base64 = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        dummy_base64 = (
            "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////"
            "////////////////////////////////////////////////////////////////////wgALCAAB"
            "AAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
        )

print("Iniciando prueba local de la lógica YOLOv8 + Ollama sobre tu imagen real...")
print("-" * 80)
try:
    resultado = lanzador_ar.query_yolo_and_ollama(dummy_base64)

    print("=" * 80)
    print("RESULTADO DE MOBY:")
    print(resultado)
    print("=" * 80)
except Exception as e:
    print("=" * 80)
    print("EXCEPCIÓN ENCONTRADA:")
    import traceback
    traceback.print_exc()
    print("=" * 80)
