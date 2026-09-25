import logging
from sqlalchemy.orm import Session
from . import models, schemas
from .distance import haversine

log = logging.getLogger(__name__)

def get_one(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Address)
        .order_by(models.Address.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create(db: Session, data: schemas.AddressCreate):
    row = models.Address(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    log.info("created address id=%s", row.id)
    return row

def update(db: Session, row: models.Address, data: schemas.AddressUpdate):
    changes = data.model_dump(exclude_unset=True)
    for k, v in changes.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    log.info("updated address id=%s fields=%s", row.id, list(changes.keys()))
    return row

def delete(db: Session, row: models.Address):
    aid = row.id
    db.delete(row)
    db.commit()
    log.info("deleted address id=%s", aid)

def nearby(db: Session, lat: float, lon: float, radius_km: float):
    hits = []
    for row in db.query(models.Address).all():
        d = haversine(lat, lon, row.latitude, row.longitude)
        if d <= radius_km:
            hits.append((round(d, 3), row))
    hits.sort(key=lambda item: item[0])
    log.info("nearby search (%s, %s) r=%skm -> %s result(s)", lat, lon, radius_km, len(hits))
    return hits
