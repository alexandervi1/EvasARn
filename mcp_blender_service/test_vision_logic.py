import sys
import os

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import lanzador_ar

# Imagen base64 mínima (1x1 pixel negro)
import base64
from io import BytesIO

# Generar una imagen real de 100x100 usando PIL (Pillow se instala con ultralytics)
try:
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    dummy_base64 = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()
    print("[OK] Imagen de prueba JPEG 100x100 generada dinámicamente.")
except Exception as e:
    print(f"[Aviso] No se pudo usar PIL: {str(e)}. Usando fallback base64...")
    dummy_base64 = (
        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////"
        "////////////////////////////////////////////////////////////////////wgALCAAB"
        "AAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
    )

print("Iniciando prueba local de la lógica YOLOv8 + Ollama...")
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
