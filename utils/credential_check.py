from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from schema.schema import user_credentials 
from pymongo import AsyncMongoClient
import asyncio, os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("MONGODB")

@asynccontextmanager
async def lifespan(app:FastAPI):
    mongo_db = AsyncMongoClient(URI)
    app.state.mongo_client = mongo_db
    app.state.db = mongo_db["nesthost_db"]
    app.state.collections = app.state.db["users"]
    yield
    
    await mongo_db.close()
    print("application shut donw successfully")
    


form_app = FastAPI(lifespan=lifespan)

@form_app.post("/register")
async def register_credentials(cred:user_credentials, request:Request):
    collection = request.app.state.collections
    return collection
        

    
    
    
    

# @form_app.post("/login")
# async def check_credentials(cred:user_credentials):