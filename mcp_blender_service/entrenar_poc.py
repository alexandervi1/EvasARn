# -*- coding: utf-8 -*-
import os
import shutil
import sys
from ultralytics import YOLO

def main():
    print("=" * 80)
    print("[ENTRENAMIENTO POC] INICIANDO ENTRENAMIENTO DE PRUEBA DE CONCEPTO")
    print("=" * 80)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # 1. Definir rutas
    medios_img = os.path.abspath(os.path.join(current_dir, "..", "medios", "image.png"))
    if not os.path.exists(medios_img):
        print(f"[ERROR] No se encontró la imagen en: {medios_img}")
        sys.exit(1)
        
    dataset_dir = os.path.join(current_dir, "dataset")
    img_train_dir = os.path.join(dataset_dir, "images", "train")
    img_val_dir = os.path.join(dataset_dir, "images", "val")
    lbl_train_dir = os.path.join(dataset_dir, "labels", "train")
    lbl_val_dir = os.path.join(dataset_dir, "labels", "val")
    
    # 2. Crear carpetas limpias
    for folder in [img_train_dir, img_val_dir, lbl_train_dir, lbl_val_dir]:
        os.makedirs(folder, exist_ok=True)
        
    # 3. Copiar la imagen a las carpetas de Train y Val
    shutil.copy(medios_img, os.path.join(img_train_dir, "image.png"))
    shutil.copy(medios_img, os.path.join(img_val_dir, "image.png"))
    print("[OK] Imagen de prueba copiada a las carpetas del dataset.")
    
    # 4. Crear etiquetas en formato YOLOv8
    # Formato YOLO: <class_id> <x_centro> <y_centro> <ancho> <alto> (normalizados entre 0 y 1)
    # Colocamos una caja de selección que cubre el 90% central de la pantalla
    label_content = "0 0.5 0.5 0.9 0.9\n"
    
    with open(os.path.join(lbl_train_dir, "image.txt"), "w") as f:
        f.write(label_content)
    with open(os.path.join(lbl_val_dir, "image.txt"), "w") as f:
        f.write(label_content)
    print("[OK] Archivos de etiquetas generados (Clase 0: interfaz-docker).")
    
    # 5. Generar data.yaml para el entrenamiento
    # Usar barras diagonales normales (/) compatibles con Windows y YOLOv8
    dataset_path_formatted = dataset_dir.replace("\\", "/")
    yaml_content = f"""path: {dataset_path_formatted}
train: images/train
val: images/val
nc: 1
names:
  0: interfaz-docker
"""
    yaml_path = os.path.join(dataset_dir, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    print(f"[OK] Archivo config 'data.yaml' creado en: {yaml_path}")
    
    # 6. Ejecutar entrenamiento rápido
    print("-" * 80)
    print("Iniciando entrenamiento local rápido (5 épocas)...")
    print("-" * 80)
    
    # Cargar modelo base nano
    model = YOLO("yolov8n.pt")
    
    # Entrenar de forma rápida (epochs=5)
    model.train(
        data=yaml_path.replace("\\", "/"),
        epochs=5,
        imgsz=640,
        device="cpu", # Forzar CPU para máxima compatibilidad sin requerir drivers GPU
        workers=0     # Evitar problemas de multiprocesamiento en Windows durante pruebas rápidas
    )
    
    # 7. Buscar y copiar pesos resultantes
    # Ultralytics guarda los pesos en runs/detect/train/weights/best.pt por defecto
    best_weights_src = os.path.join(current_dir, "runs", "detect", "train", "weights", "best.pt")
    custom_weights_dst = os.path.join(current_dir, "yolov8_docker_custom.pt")
    
    # Si ya existían carpetas de entrenamientos anteriores, buscamos la más reciente
    if not os.path.exists(best_weights_src):
        # Buscar en carpetas incrementales como train2, train3, etc.
        import glob
        runs = glob.glob(os.path.join(current_dir, "runs", "detect", "train*", "weights", "best.pt"))
        if runs:
            # Seleccionar la última carpeta creada
            best_weights_src = sorted(runs)[-1]
            
    if os.path.exists(best_weights_src):
        shutil.copy(best_weights_src, custom_weights_dst)
        print("=" * 80)
        print("[ÉXITO] MODELO PERSONALIZADO ENTRENADO CORRECTAMENTE")
        print(f"Pesos de salida guardados en: {custom_weights_dst}")
        print("=" * 80)
    else:
        print("[ADVERTENCIA] El entrenamiento finalizó pero no se encontraron los pesos de salida.")

if __name__ == "__main__":
    main()
