import  jwt,os
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Dict
from dotenv import load_dotenv

load_dotenv()
secret=os.getenv("SECRET_KEY")
algo = os.getenv("ALGORITHM")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

def Create_access_token(data:Dict):
    if not secret or not algo:
        raise ValueError("SECRET_KEY or ALGORITHM not configured")
    encoded_data = data.copy()
    encoded_data["exp"] = datetime.now(timezone.utc)+timedelta(hours=3)
    return jwt.encode(payload=encoded_data, key=secret, algorithm=algo)

data = {
  "_id": "123",
  "email": "ceo@company.com",
  "username": "ceo1",
  "password": "hashed-password",
  "role": "CEO"
}
print(Create_access_token(data))

def get_current_user(token:str = Depends(oauth2_schema)):
  try:
    payload = jwt.decode(token)
    return payload
  except PyJWTError:
    raise HTTPException(status_code=404, detail="No details were found")
  
def required_roles(*allowed_roles):
  def role_checker(user:Dict = Depends(get_current_user)):
    if user["role"] not in allowed_roles:
      raise HTTPException(status_code=403, detail="invalid route")
    else:
      return user
  
  return role_checker
    

  