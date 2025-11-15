from fastapi import FastAPI
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
import os, re, asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, field_validator

load_dotenv()
URI = os.getenv("MONGODB")

class UserCredentials(BaseModel):
    email: EmailStr
    username: str
    password: str
    role:str

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        if len(v) < 5:
            raise ValueError("Password must be at least 5 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    
    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        if len(v) < 5:
            raise ValueError("Password must be at least 5 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Password must contain at least one special character")
        return v
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncMongoClient(URI)
    db = client["nesthost_db"]
    users = db["users"]

    #Run only once at app startup
    if "users" not in await db.list_collection_names():
        await users.insert_one({"initialized": True})
        print("Database and collection created successfully")

    app.state.db = db
    yield
    await client.close()


app = FastAPI(lifespan=lifespan)
