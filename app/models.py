"""Database models."""
from sqlalchemy import Column, String, Integer, Float
from app.database import Base


class Vehicle(Base):
    """Vehicle table model.
    
    VINs are stored in uppercase to enforce case-insensitive uniqueness.
    """
    __tablename__ = "vehicles"

    vin = Column(String(17), primary_key=True, index=True)
    manufacturer_name = Column(String(100), nullable=False)
    description = Column(String(500))
    horse_power = Column(Integer, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_year = Column(Integer, nullable=False)
    purchase_price = Column(Float, nullable=False)
    fuel_type = Column(String(50), nullable=False)

