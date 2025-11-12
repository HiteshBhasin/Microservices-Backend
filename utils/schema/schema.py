from pydantic import BaseModel, EmailStr

class user_credentials(BaseModel):
    email: EmailStr
    username:str
    password: str