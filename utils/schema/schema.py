from pydantic import BaseModel, EmailStr, field_validator
from pymongo import AsyncMongoClient
import asyncio, os, re
from dotenv import load_dotenv

load_dotenv()
class user_credentials(BaseModel):
    email: EmailStr
    username:str
    password: str

    @field_validator("password")
    @classmethod
    def validator(cls,v):
        if len(v)<5:
            raise Exception (" Password length is less than 5 letters and/or digits. Please try again ")
        elif not re.search(r"[A-Z]", v):
            raise ValueError ("Password must contain at least one uppercase letter")
        elif not re.search(r"[a-z]",v):
            raise ValueError("Password must contain at least one lowercase lette")
        elif not re.search(r"[0-9]",v):
            raise ValueError("Password must contain at least one digit lette")
        elif not re.search(r"[@$!%*?&]",v):
            raise ValueError ("Password must contain at least one special character lette")
        return v


URI = os.getenv("MONGODB")
async def create_database():
    mongo_db = AsyncMongoClient(URI)
    db = mongo_db["nesthost_db"]
    collection = db["users"]
    # Database and collection are created automatically when you insert the first document
    await collection.insert_one({"initialized": True})
    print("Database and collection created successfully")
    collections = await mongo_db.list_database_names()
    for collection in collections:
        print(collection)
    
   
asyncio.run(create_database()) 