import logging
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import engine, get_db, Base
from . import models
from . import crud, schemas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("addressbook")

Base.metadata.create_all(bind=engine)
log.info("db tables ready")

app = FastAPI(
    title="Address Book API",
    description="Create / update / delete addresses and find ones within a given distance.",
    version="1.0",
)

@app.get("/")
def root():
    return {"message": "Address Book API. See /docs for swagger."}

@app.post("/addresses", response_model=schemas.AddressOut, status_code=201)
def create_address(payload: schemas.AddressCreate, db: Session = Depends(get_db)):
    return crud.create(db, payload)


@app.get("/addresses", response_model=list[schemas.AddressOut])
def list_addresses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.get_all(db, skip=skip, limit=limit)

@app.get("/addresses/nearby", response_model=list[schemas.NearbyOut])
def nearby_addresses(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    distance_km: float = Query(..., gt=0, description="radius in kilometers"),
    db: Session = Depends(get_db),
):
    hits = crud.nearby(db, latitude, longitude, distance_km)
    out = []
    for dist, row in hits:
        data = schemas.AddressOut.model_validate(row).model_dump()
        data["distance_km"] = dist
        out.append(data)
    return out


@app.get("/addresses/{address_id}", response_model=schemas.AddressOut)
def get_address(address_id: int, db: Session = Depends(get_db)):
    row = crud.get_one(db, address_id)
    if not row:
        log.warning("address %s not found", address_id)
        raise HTTPException(status_code=404, detail="address not found")
    return row

@app.put("/addresses/{address_id}", response_model=schemas.AddressOut)
def update_address(
    address_id: int,
    payload: schemas.AddressUpdate,
    db: Session = Depends(get_db),
):
    row = crud.get_one(db, address_id)
    if not row:
        log.warning("address %s not found for update", address_id)
        raise HTTPException(status_code=404, detail="address not found")
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="nothing to update")
    return crud.update(db, row, payload)

@app.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    row = crud.get_one(db, address_id)
    if not row:
        log.warning("address %s not found for delete", address_id)
        raise HTTPException(status_code=404, detail="address not found")
    crud.delete(db, row)
    return {"ok": True, "deleted": address_id}
