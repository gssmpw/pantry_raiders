import shutil
import os
import fiftyone as fo
import fiftyone.zoo as foz
from ultralytics import YOLO

MY_CLASSES = ["Apple", "Banana", "Bread", "Milk"]
output_dir = r"C:\Users\gsmit\Documents\pantry_raiders\grocery_dataset"

# Set per-class sample caps
caps = {
    "Apple": 150,
    "Banana": 150,
    "Bread": 200,
    "Milk": 500,
}

# Wipe old dataset
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

# Download each class separately with a cap, then merge
all_train = []
all_val = []

for cls in MY_CLASSES:
    print(f"Downloading {cls}...")

    train = foz.load_zoo_dataset(
        "open-images-v7",
        split="train",
        label_types=["detections"],
        classes=[cls],
        max_samples=caps[cls],
        dataset_name=f"oi_train_{cls.lower()}",
    )
    all_train.append(train)

    val = foz.load_zoo_dataset(
        "open-images-v7",
        split="validation",
        label_types=["detections"],
        classes=[cls],
        max_samples=50,
        dataset_name=f"oi_val_{cls.lower()}",
    )
    all_val.append(val)

# Merge into single datasets
train_dataset = fo.Dataset(name="grocery_train")
for ds in all_train:
    train_dataset.merge_samples(ds)

val_dataset = fo.Dataset(name="grocery_val")
for ds in all_val:
    val_dataset.merge_samples(ds)

# Export
train_dataset.export(
    export_dir=output_dir,
    dataset_type=fo.types.YOLOv5Dataset,
    label_field="ground_truth",
    split="train",
    classes=MY_CLASSES,
)

val_dataset.export(
    export_dir=output_dir,
    dataset_type=fo.types.YOLOv5Dataset,
    label_field="ground_truth",
    split="val",
    classes=MY_CLASSES,
)

print("Done! Counts:")
print("Train:", train_dataset.count_values("ground_truth.detections.label"))
print("Val:", val_dataset.count_values("ground_truth.detections.label"))

# --- TRAIN ---
model = YOLO("yolov8n.yaml")
model.train(
    data=os.path.join(output_dir, "dataset.yaml"),
    epochs=100,
    imgsz=640,
    batch=16,
    name="grocery_yolov8",
    device='cpu',
    workers=0,
    patience=20,
    save=True,
)