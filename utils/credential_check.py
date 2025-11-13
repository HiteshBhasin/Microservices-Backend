from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from schema.schema import UserCredentials
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os, logging, hashlib

load_dotenv()
URI = os.getenv("MONGODB")

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_client = AsyncMongoClient(URI)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client["nesthost_db"]
    app.state.collections = app.state.db["users"]
    yield
    await mongo_client.close()
    print("Application shut down successfully")

form_app = FastAPI(lifespan=lifespan)

form_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@form_app.get("/")
async def index():
    return {"message": "hi"}

@form_app.post("/register")
async def register_credentials(cred: UserCredentials, request: Request):
    hash_obj = hashlib.sha256(cred.password.encode("utf-8"))
    encoded_obj = hash_obj.hexdigest()
    collection = request.app.state.collections
    new_user = {
        "emai":cred.email,
        "username":cred.username,
        "password": encoded_obj
    }
    result = await collection.insert_one(new_user)
    return {"message": "User registered successfully!", "user_id": str(result.inserted_id)}

@form_app.post("/login")
async def login_page(cred:UserCredentials, request:Request):
    collection = request.app.state.collections
    user = await collection.find_one({"username":cred.username})
    if not user:
        return f"Username or password are not correct{cred.username}or {cred.password}"
    else:
        
        
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("credential_check:form_app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)), reload=True)
