from fastapi import Depends, FastAPI, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal, PantryItem
from datetime import datetime

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fake_yolo_scan():
    return ["apple", "banana", "milk"]


def fake_receipt_scan():
    return ["eggs", "bread", "orange juice"]


# -------------------------
# PANTRY APIs
# -------------------------

@app.get("/pantry")
def get_pantry(db: Session = Depends(get_db)):
    items = db.query(PantryItem).all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "last_seen": item.last_seen
        }
        for item in items
    ]


@app.post("/pantry/add")
def add_pantry_item(name: str, quantity: int = 1, db: Session = Depends(get_db)):
    new_item = PantryItem(
        name=name,
        quantity=quantity,
        last_seen=datetime.utcnow()
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {
        "message": "Item added",
        "item": {
            "id": new_item.id,
            "name": new_item.name,
            "quantity": new_item.quantity,
            "last_seen": new_item.last_seen
        }
    }


@app.put("/pantry/update/{item_id}")
def update_pantry_item(item_id: int, quantity: int, db: Session = Depends(get_db)):
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()

    if not item:
        return {"error": "Item not found"}

    item.quantity = quantity
    item.last_seen = datetime.utcnow()

    db.commit()
    db.refresh(item)

    return {
        "message": "Item updated",
        "item": {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "last_seen": item.last_seen
        }
    }


@app.delete("/pantry/delete/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()

    if not item:
        return {"error": "Item not found"}

    db.delete(item)
    db.commit()

    return {"message": "Item deleted"}


@app.delete("/pantry")
def clear_pantry(db: Session = Depends(get_db)):
    db.query(PantryItem).delete()
    db.commit()

    return {"message": "Pantry cleared"}


# -------------------------
# SCAN APIs
# -------------------------

@app.post("/scan/pantry")
async def scan_pantry(file: UploadFile = File(...), db: Session = Depends(get_db)):
    detected_items = fake_yolo_scan()

    db.query(PantryItem).delete()

    for item_name in detected_items:
        new_item = PantryItem(
            name=item_name,
            quantity=1,
            last_seen=datetime.utcnow()
        )
        db.add(new_item)

    db.commit()

    return {
        "message": "Pantry scan complete",
        "items_detected": detected_items
    }


@app.post("/scan/receipt")
async def scan_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    detected_items = fake_receipt_scan()

    for item_name in detected_items:
        new_item = PantryItem(
            name=item_name,
            quantity=1,
            last_seen=datetime.utcnow()
        )
        db.add(new_item)

    db.commit()

    return {
        "message": "Receipt scan complete",
        "items_detected": detected_items
    }


# -------------------------
# GROCERY LIST API
# -------------------------

@app.get("/grocery-list")
def get_grocery_list(db: Session = Depends(get_db)):
    pantry_items = db.query(PantryItem).all()

    grocery_list = []

    for item in pantry_items:
        if item.quantity <= 1:
            grocery_list.append({
                "name": item.name,
                "current_quantity": item.quantity,
                "suggested_quantity": 2
            })

    return grocery_list