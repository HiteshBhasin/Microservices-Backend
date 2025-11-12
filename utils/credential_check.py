from fastapi import FastAPI, 
from fastapi.middleware.cors import CORSMiddleware
from schema.schema import user_credentials

form_app = FastAPI(title="form_app")

@form_app.post("/register")
async def register_credentials(cred:user_credentials):
    name = cred.username
    passw = cred.password
    


@form_app.post("/login")
async def check_credentials(cred:user_credentials):