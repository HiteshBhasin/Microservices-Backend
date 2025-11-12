from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from schema.schema import UserCredentials
from pymongo import AsyncMongoClient
import asyncio, os
from dotenv import load_dotenv
import logging

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
    print("application shut down successfully")
    


form_app = FastAPI(lifespan=lifespan)

@form_app.post("/register")
async def register_credentials(cred:UserCredentials, request:Request):
    collection = request.app.state.collections
    await collection.insert_one(cred)
    return {"message": "Success!"}



if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("credential_check:form_app", host="0.0.0.0", port=int(os.getenv("PORT", 3000)), reload=True)
    except Exception as exc:
        import logging
        logging.error("Failed to start uvicorn: %s", exc)