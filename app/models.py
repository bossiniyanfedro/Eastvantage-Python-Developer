from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String
from .database import Base

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    street = Column(String(255), nullable=False)
    city = Column(String(80), nullable=False)
    country = Column(String(80), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Address {self.id} {self.name}>"
