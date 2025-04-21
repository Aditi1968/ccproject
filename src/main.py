# src/main.py
from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .models import Function, init_db, engine
from sqlalchemy.orm import sessionmaker
from .executor import execute_with_runtime, warm_up_container, precreate_pool
from datetime import datetime
import os
import json

# 🔧 Initialize DB and session
init_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Initialize FastAPI app
app = FastAPI(title="Serverless Function Execution Platform ")

# ✅ Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    warm_up_container()
    precreate_pool(count=3)

# 🧠 Function execution model
class ExecuteRequest(BaseModel):
    code: str
    timeout: int = 5
    runtime: str = "docker"

@app.post("/execute/")
def run_function(req: ExecuteRequest):
    output = execute_with_runtime(req.code, req.timeout, req.runtime)
    return {"output": output}

class FunctionSchema(BaseModel):
    id: int = None
    name: str
    route: str
    language: str
    timeout: int
    filename: str  # ✅ NEW

    class Config:
        from_attributes = True


# 🗄️ DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/functions/", response_model=FunctionSchema)
def create_function(function_data: FunctionSchema):
    db = next(get_db())
    db_func = Function(
        name=function_data.name,
        route=function_data.route,
        language=function_data.language,
        timeout=function_data.timeout,
	filename=function_data.filename

    )
    db.add(db_func)
    db.commit()
    db.refresh(db_func)
    return db_func

# 📄 Read all
@app.get("/functions/", response_model=List[FunctionSchema])
def read_functions():
    db = next(get_db())
    return db.query(Function).all()

# 🔍 Read one
@app.get("/functions/{function_id}", response_model=FunctionSchema)
def read_function(function_id: int):
    db = next(get_db())
    db_func = db.query(Function).filter(Function.id == function_id).first()
    if not db_func:
        raise HTTPException(status_code=404, detail="Function not found")
    return db_func

# ✏️ Update
@app.put("/functions/{function_id}", response_model=FunctionSchema)
def update_function(function_id: int, function_data: FunctionSchema):
    db = next(get_db())
    db_func = db.query(Function).filter(Function.id == function_id).first()
    if not db_func:
        raise HTTPException(status_code=404, detail="Function not found")
    db_func.name = function_data.name
    db_func.route = function_data.route
    db_func.language = function_data.language
    db_func.timeout = function_data.timeout
    db_func.filename = function_data.filename

    db.commit()
    db.refresh(db_func)
    return db_func

# ❌ Delete
@app.delete("/functions/{function_id}")
def delete_function(function_id: int):
    db = next(get_db())
    db_func = db.query(Function).filter(Function.id == function_id).first()
    if not db_func:
        raise HTTPException(status_code=404, detail="Function not found")
    db.delete(db_func)
    db.commit()
    return {"detail": "Function deleted successfully"}

# 📊 Metrics API with filters
@app.get("/metrics/")
def get_metrics(
    runtime: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    from_ts: Optional[float] = Query(None),
    to_ts: Optional[float] = Query(None)
):
    if not os.path.exists("metrics.json"):
        return []

    with open("metrics.json", "r") as f:
        data = json.load(f)

    if runtime:
        data = [m for m in data if m["runtime"] == runtime]
    if success is not None:
        data = [m for m in data if m["success"] == success]
    if from_ts:
        data = [m for m in data if m["timestamp"] >= from_ts]
    if to_ts:
        data = [m for m in data if m["timestamp"] <= to_ts]

    return data

@app.post("/functions/{function_id}/run")
def run_function_by_id(function_id: int):
    db = next(get_db())
    db_func = db.query(Function).filter(Function.id == function_id).first()
    if not db_func:
        raise HTTPException(status_code=404, detail="Function not found")

    # Try to read a file named function_{id}.py
    code_path = f"functions/{db_func.filename}"
    if not os.path.exists(code_path):
        raise HTTPException(status_code=400, detail="No code found for this function.")

    with open(code_path, "r") as f:
        code = f.read()

    output = execute_with_runtime(code, timeout=db_func.timeout, runtime="docker")
    return {"output": output}
