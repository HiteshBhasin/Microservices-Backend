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

# Add CORS middleware
form_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@form_app.post("/register")
async def register_credentials(cred: UserCredentials, request: Request):
    collection = request.app.state.collections
    # Convert Pydantic model to dict for MongoDB
    user_dict = cred.model_dump()
    result = await collection.insert_one(user_dict)
    return {"message": "User registered successfully!", "user_id": str(result.inserted_id)}



if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("credential_check:form_app", host="0.0.0.0", port=int(os.getenv("PORT", 3000)), reload=True)
    except Exception as exc:
        import logging
        logging.error("Failed to start uvicorn: %s", exc)