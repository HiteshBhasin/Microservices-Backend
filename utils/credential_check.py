from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schema.schema import user_credentials
from pymongo import AsyncMongoClient
import asyncio, os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("MONGODB")

mongo_db = AsyncMongoClient(URI)

async def get_databases():
    collections = await mongo_db.list_database_names()
    for collection in collections:
        print(collection)
    
print(asyncio.run(get_databases()))
# form_app = FastAPI(title="form_app")

# @form_app.post("/register")
# async def register_credentials(cred:user_credentials):
#     name = cred.username
#     passw = cred.password
    


# @form_app.post("/login")
# async def check_credentials(cred:user_credentials):