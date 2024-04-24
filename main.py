import sqlite3
import databases
from typing import Dict
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

URL = "sqlite:///addressbook.db"
database = databases.Database(URL)

@app.on_event("startup")
async def startup():
    await database.connect()
    await database.execute("""
        CREATE TABLE IF NOT EXISTS addresses
        (
            name TEXT PRIMARY KEY,
            address TEXT
        )
    """)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/address")
async def create_address(name: str, address: str, request: Request):
    try:
        await database.execute("INSERT INTO addresses values(:name, :address)", {"name": name, "address": address})
        return {"message": "Address created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Address already exists")

@app.get("/addresses/{name}")
async def get_address(name, request: Request):
    try:
        result = await database.fetch_one("SELECT address FROM addresses where name=:name", {"name": name})
        if result:
            return {"name": name, "address": result.address}
        else:
            raise HTTPException(status_code=404, detail="Address not found")
    except Exception as E:
        raise HTTPException(status_code=404, detail=str(E))

@app.post("/update")
async def update_address(name: str, new_address: str, request: Request):
    try:
        result = await database.execute("UPDATE addresses set address=:new_address where name=:name", {"new_address": new_address, "name":name})
        return {"message": "Address updated successfully"}
    except:
        raise HTTPException(status_code=404, detail="Address not found")

@app.post("/delete")
async def delete_address(name: str, request: Request):
    try:
        result = await database.execute("DELETE FROM addresses where name=:name", {"name":name})
        return {"message": "address deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="Address not found")


