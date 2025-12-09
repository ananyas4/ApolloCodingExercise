"""Main FastAPI app."""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db, init_db, is_production
from app.models import Vehicle
from app.schemas import VehicleCreate, VehicleUpdate, VehicleResponse

app = FastAPI(title="Vehicle API", version="1.0.0")


@app.on_event("startup")
async def startup():
    """Set up db tables on startup (local dev only)."""
    # Only auto-create tables for local development
    # Production/remote databases should use migrations
    if not is_production:
        init_db()


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    """Catch validation errors and format them nicely."""
    error_dict = {}
    for err in exc.errors():
        # Handle malformed JSON
        if err["type"] == "json_invalid":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid JSON format"}
            )
        
        # Build field path
        field_path = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        if not field_path:
            field_path = "body"
        error_dict[field_path] = err["msg"]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": error_dict}
    )


@app.exception_handler(ValueError)
async def handle_value_error(request: Request, exc: ValueError):
    """Catch value errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": {"detail": str(exc)}}
    )


def _normalize_vin(vin: str) -> str:
    """Make VIN uppercase and strip whitespace."""
    return vin.upper().strip()


@app.get("/vehicle", response_model=List[VehicleResponse])
def list_vehicles(db: Session = Depends(get_db)):
    """Get all vehicles."""
    return db.query(Vehicle).all()


@app.post("/vehicle", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """Create a new vehicle."""
    vin_upper = _normalize_vin(vehicle.vin)
    
    # Check for duplicates
    existing = db.query(Vehicle).filter(Vehicle.vin == vin_upper).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": {"vin": "Vehicle with this VIN already exists"}}
        )
    
    # Create the vehicle
    new_vehicle = Vehicle(
        vin=vin_upper,
        manufacturer_name=vehicle.manufacturer_name,
        description=vehicle.description,
        horse_power=vehicle.horse_power,
        model_name=vehicle.model_name,
        model_year=vehicle.model_year,
        purchase_price=vehicle.purchase_price,
        fuel_type=vehicle.fuel_type
    )
    
    try:
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        return new_vehicle
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": {"vin": "Vehicle with this VIN already exists"}}
        )


@app.get("/vehicle/{vin}", response_model=VehicleResponse)
def get_vehicle(vin: str, db: Session = Depends(get_db)):
    """Get a vehicle by VIN."""
    vin_upper = _normalize_vin(vin)
    vehicle = db.query(Vehicle).filter(Vehicle.vin == vin_upper).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    return vehicle


@app.put("/vehicle/{vin}", response_model=VehicleResponse)
def update_vehicle(vin: str, vehicle_update: VehicleUpdate, db: Session = Depends(get_db)):
    """Update a vehicle by VIN."""
    vin_upper = _normalize_vin(vin)
    vehicle = db.query(Vehicle).filter(Vehicle.vin == vin_upper).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Only update fields that were provided
    updates = vehicle_update.model_dump(exclude_unset=True)
    for key, val in updates.items():
        setattr(vehicle, key, val)
    
    try:
        db.commit()
        db.refresh(vehicle)
        return vehicle
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": {"vin": "Update would violate unique constraint"}}
        )


@app.delete("/vehicle/{vin}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vin: str, db: Session = Depends(get_db)):
    """Delete a vehicle by VIN."""
    vin_upper = _normalize_vin(vin)
    vehicle = db.query(Vehicle).filter(Vehicle.vin == vin_upper).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    db.delete(vehicle)
    db.commit()
    return None

