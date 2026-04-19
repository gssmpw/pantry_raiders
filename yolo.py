import shutil
import os
import fiftyone as fo
import fiftyone.zoo as foz
from ultralytics import YOLO

MY_CLASSES = ["Apple", "Banana", "Bread", "Milk"]
output_dir = r"C:\Users\gsmit\Documents\pantry_raiders\grocery_dataset"

# --- DOWNLOAD & EXPORT ---
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

train_dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=MY_CLASSES,
)
train_dataset.export(
    export_dir=output_dir,
    dataset_type=fo.types.YOLOv5Dataset,
    label_field="ground_truth",
    split="train",
    classes=MY_CLASSES,
)

val_dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="validation",
    label_types=["detections"],
    classes=MY_CLASSES,
)
val_dataset.export(
    export_dir=output_dir,
    dataset_type=fo.types.YOLOv5Dataset,
    label_field="ground_truth",
    split="val",
    classes=MY_CLASSES,
)

# --- TRAIN ---
model = YOLO("yolov8n.yaml")
model.train(
    data=os.path.join(output_dir, "dataset.yaml"),
    epochs=1,
    imgsz=640,
    batch=16,
    name="grocery_yolov8",
    device='cpu',
    workers=4,
    patience=20,
    save=True,
)