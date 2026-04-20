from fastapi import Depends, FastAPI, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal, PantryItem
from datetime import datetime

app = FastAPI()

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- MOCK YOLO OUTPUT ---
def fake_yolo_scan():
    # Replace later with real model
    return ["apple", "banana", "milk"]


@app.post("/scan")
async def scan_pantry(file: UploadFile = File(...), db: Session = Depends(get_db)):

    detected_items = fake_yolo_scan()

    # Clear old pantry first
    db.query(PantryItem).delete()

    # Add fresh scan results
    for item_name in detected_items:
        new_item = PantryItem(
        name=item_name,
        quantity=1,
        last_seen=datetime.utcnow()
        )
        db.add(new_item)
        

    db.commit()
    return {"items_detected": detected_items}


@app.get("/pantry")
def get_pantry(db: Session = Depends(get_db)):
    items = db.query(PantryItem).all()

    return [
        {
            "name": item.name,
            "quantity": item.quantity,
            "last_seen": item.last_seen
        }
        for item in items
    ]
    
@app.delete("/pantry")
def clear_pantry(db: Session = Depends(get_db)):
    db.query(PantryItem).delete()
    db.commit()
    return {"message": "Pantry cleared"}