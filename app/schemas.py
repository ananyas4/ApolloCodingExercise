"""Pydantic schemas for request/response validation."""
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class VehicleBase(BaseModel):
    """Base schema for Vehicle with common fields."""

    manufacturer_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    horse_power: int = Field(..., gt=0)
    model_name: str = Field(..., min_length=1, max_length=100)
    model_year: int = Field(..., ge=1900, le=2100)
    purchase_price: float = Field(..., gt=0.0)
    fuel_type: str = Field(..., min_length=1, max_length=50)


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle."""

    vin: str = Field(..., min_length=1, max_length=17)

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, v):
        """Normalize and validate VIN."""
        if not v or not v.strip():
            raise ValueError("VIN cannot be empty")
        return v.upper().strip()


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle (all fields optional)."""

    manufacturer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    horse_power: Optional[int] = Field(None, gt=0)
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    model_year: Optional[int] = Field(None, ge=1900, le=2100)
    purchase_price: Optional[float] = Field(None, gt=0.0)
    fuel_type: Optional[str] = Field(None, min_length=1, max_length=50)


class VehicleResponse(VehicleBase):
    """Schema for vehicle response."""

    vin: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""

    errors: dict
