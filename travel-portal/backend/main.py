# backend/main.py
import os
from typing import List, Optional
from datetime import date, datetime
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, text, Boolean, Numeric, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from tenacity import retry, stop_after_attempt, wait_fixed

# 1. Database Connection String (Pointing to client-onboarding)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:secret_postgres_password@postgres-db:5432/client-onboarding"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SCHEMA-MATCHED SQLALCHEMY MODELS (BOUND TO ONBOARDING SCHEMA) ---

class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tax_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("onboarding.companies.id", ondelete="CASCADE"), nullable=False)
    plate_number = Column(String, unique=True, nullable=False)
    model = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Driver(Base):
    __tablename__ = "drivers"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("onboarding.companies.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("onboarding.companies.id", ondelete="SET NULL"), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String)

class Route(Base):
    __tablename__ = "routes"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    estimated_duration_hours = Column(Numeric(5, 2))

class Revenue(Base):
    __tablename__ = "revenues"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("onboarding.companies.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    statement_date = Column(Date, nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Amenity(Base):
    __tablename__ = "amenities"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("onboarding.vehicles.id", ondelete="CASCADE"), nullable=False)
    provides_snacks = Column(Boolean, default=False)
    has_wifi = Column(Boolean, default=False)
    has_ac = Column(Boolean, default=False)
    has_charging_ports = Column(Boolean, default=False)
    has_reclining_seats = Column(Boolean, default=False)
    has_reading_light = Column(Boolean, default=False)
    has_blanket = Column(Boolean, default=False)
    has_first_aid = Column(Boolean, default=False)
    has_gps = Column(Boolean, default=False)
    has_cctv = Column(Boolean, default=False)

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "onboarding"}
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("onboarding.companies.id", ondelete="CASCADE"), nullable=False)
    has_rc = Column(Boolean, default=False)          # Registration Certificate (RC)
    has_fitness = Column(Boolean, default=False)     # Fitness Certificate
    has_permit = Column(Boolean, default=False)      # Road/AITP Permit
    has_insurance = Column(Boolean, default=False)   # Vehicle Insurance
    has_puc = Column(Boolean, default=False)         # Pollution Under Control (PUC)
    has_road_tax = Column(Boolean, default=False)    # Road Tax Receipt



# --- RECOVERY CONNECTION ENGINE ---
@retry(stop=stop_after_attempt(10), wait=wait_fixed(3))
def verify_database_connection():
    print("⏳ Connecting to PostgreSQL 18 and checking 'onboarding' schema layout...")
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS onboarding"))
    Base.metadata.create_all(bind=engine)
    print("✅ Successfully linked to 'onboarding' schema database objects!")

verify_database_connection()

# 2. Initialize FastAPI Application
app = FastAPI(title="Travel Portal API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PYDANTIC VALIDATION MODELS ---
class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2)
    tax_id: str = Field(..., min_length=4)

class CompanyResponse(CompanyCreate):
    id: int
    class Config:
        from_attributes = True

class VehicleCreate(BaseModel):
    company_id: int
    plate_number: str
    model: str

class VehicleResponse(VehicleCreate):
    id: int
    class Config:
        from_attributes = True

class DriverCreate(BaseModel):
    company_id: int
    full_name: str
    license_number: str

class DriverResponse(DriverCreate):
    id: int
    class Config:
        from_attributes = True

class EmployeeCreate(BaseModel):
    company_id: Optional[int] = None
    first_name: str
    last_name: str
    email: str
    role: Optional[str] = None

class EmployeeResponse(EmployeeCreate):
    id: int
    class Config:
        from_attributes = True

class RouteCreate(BaseModel):
    route_name: Optional[str] = None
    origin: str
    destination: str
    estimated_duration_hours: Optional[float] = None

class RouteResponse(RouteCreate):
    id: int
    class Config:
        from_attributes = True

class RevenueCreate(BaseModel):
    company_id: int
    amount: float
    statement_date: date

class RevenueResponse(RevenueCreate):
    id: int
    class Config:
        from_attributes = True

class AmenityCreate(BaseModel):
    vehicle_id: int
    has_wifi: Optional[bool] = False
    has_ac: Optional[bool] = False
    has_charging_ports: Optional[bool] = False
    has_reclining_seats: Optional[bool] = False
    has_reading_light: Optional[bool] = False
    has_blanket: Optional[bool] = False
    has_first_aid: Optional[bool] = False
    has_gps: Optional[bool] = False
    has_cctv: Optional[bool] = False

class AmenityResponse(AmenityCreate):
    id: int
    class Config:
        from_attributes = True

class DocumentCreate(BaseModel):
    company_id: int
    has_rc: Optional[bool] = False
    has_fitness: Optional[bool] = False
    has_permit: Optional[bool] = False
    has_insurance: Optional[bool] = False
    has_puc: Optional[bool] = False
    has_road_tax: Optional[bool] = False

class DocumentResponse(DocumentCreate):
    id: int
    class Config:
        from_attributes = True



# --- API ROUTING ENDPOINTS ---

# --- Companies ---
@app.post("/company", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(name=company.name, tax_id=company.tax_id)
    db.add(db_company)
    try:
        db.commit()
        db.refresh(db_company)
        return db_company
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Company or Tax ID already exists in schema.")

@app.get("/company", response_model=List[CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

# --- Vehicles ---
@app.post("/vehicle", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(company_id=vehicle.company_id, plate_number=vehicle.plate_number, model=vehicle.model)
    db.add(db_vehicle)
    try:
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Vehicle registration failed. Ensure company_id exists.")

@app.get("/vehicle", response_model=List[VehicleResponse])
def get_vehicles(db: Session = Depends(get_db)):
    return db.query(Vehicle).all()

# --- Drivers ---
@app.post("/driver", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    db_driver = Driver(company_id=driver.company_id, full_name=driver.full_name, license_number=driver.license_number)
    db.add(db_driver)
    try:
        db.commit()
        db.refresh(db_driver)
        return db_driver
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Driver insertion failed. Ensure company_id exists.")

@app.get("/driver", response_model=List[DriverResponse])
def get_drivers(db: Session = Depends(get_db)):
    return db.query(Driver).all()

# --- Employees ---
@app.post("/employee", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(
        company_id=employee.company_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        role=employee.role
    )
    db.add(db_employee)
    try:
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Employee creation failed. Verify email unique & company_id correct.")

@app.get("/employee", response_model=List[EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

# --- Routes ---
@app.post("/route", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    route_name = route.route_name or f"{route.origin} to {route.destination}"
    db_route = Route(
        route_name=route_name,
        origin=route.origin,
        destination=route.destination,
        estimated_duration_hours=route.estimated_duration_hours
    )
    db.add(db_route)
    try:
        db.commit()
        db.refresh(db_route)
        return db_route
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Route creation failed.")

@app.get("/route", response_model=List[RouteResponse])
def get_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()

# --- Revenues ---
@app.post("/revenue", response_model=RevenueResponse, status_code=status.HTTP_201_CREATED)
def create_revenue(revenue: RevenueCreate, db: Session = Depends(get_db)):
    db_revenue = Revenue(
        company_id=revenue.company_id,
        amount=revenue.amount,
        statement_date=revenue.statement_date
    )
    db.add(db_revenue)
    try:
        db.commit()
        db.refresh(db_revenue)
        return db_revenue
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Revenue entry failed. Ensure company_id exists.")

@app.get("/revenue", response_model=List[RevenueResponse])
def get_revenues(db: Session = Depends(get_db)):
    return db.query(Revenue).all()

# --- Amenities ---
@app.post("/amenity", response_model=AmenityResponse, status_code=status.HTTP_201_CREATED)
def create_amenity(amenity: AmenityCreate, db: Session = Depends(get_db)):
    db_amenity = db.query(Amenity).filter(Amenity.vehicle_id == amenity.vehicle_id).first()
    if db_amenity:
        db_amenity.has_wifi = amenity.has_wifi
        db_amenity.has_ac = amenity.has_ac
        db_amenity.has_charging_ports = amenity.has_charging_ports
        db_amenity.has_reclining_seats = amenity.has_reclining_seats
        db_amenity.has_reading_light = amenity.has_reading_light
        db_amenity.has_blanket = amenity.has_blanket
        db_amenity.has_first_aid = amenity.has_first_aid
        db_amenity.has_gps = amenity.has_gps
        db_amenity.has_cctv = amenity.has_cctv
    else:
        db_amenity = Amenity(**amenity.model_dump())
        db.add(db_amenity)
    try:
        db.commit()
        db.refresh(db_amenity)
        return db_amenity
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Amenity checklist registration failed. Ensure vehicle_id exists.")

@app.get("/amenity", response_model=List[AmenityResponse])
def get_amenities(db: Session = Depends(get_db)):
    return db.query(Amenity).all()

@app.get("/amenity/{vehicle_id}", response_model=AmenityResponse)
def get_vehicle_amenities(vehicle_id: int, db: Session = Depends(get_db)):
    record = db.query(Amenity).filter(Amenity.vehicle_id == vehicle_id).first()
    if not record:
        return Amenity(
            id=0,
            vehicle_id=vehicle_id,
            has_wifi=False,
            has_ac=False,
            has_charging_ports=False,
            has_reclining_seats=False,
            has_reading_light=False,
            has_blanket=False,
            has_first_aid=False,
            has_gps=False,
            has_cctv=False
        )
    return record

# --- Documents ---
@app.post("/document", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    db_document = db.query(Document).filter(Document.company_id == document.company_id).first()
    if db_document:
        db_document.has_rc = document.has_rc
        db_document.has_fitness = document.has_fitness
        db_document.has_permit = document.has_permit
        db_document.has_insurance = document.has_insurance
        db_document.has_puc = document.has_puc
        db_document.has_road_tax = document.has_road_tax
    else:
        db_document = Document(**document.model_dump())
        db.add(db_document)
    try:
        db.commit()
        db.refresh(db_document)
        return db_document
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Document checklist storage failed. Ensure company_id exists.")

@app.get("/document", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()

@app.get("/document/{company_id}", response_model=DocumentResponse)
def get_company_documents(company_id: int, db: Session = Depends(get_db)):
    record = db.query(Document).filter(Document.company_id == company_id).first()
    if not record:
        return Document(
            id=0,
            company_id=company_id,
            has_rc=False,
            has_fitness=False,
            has_permit=False,
            has_insurance=False,
            has_puc=False,
            has_road_tax=False
        )
    return record

