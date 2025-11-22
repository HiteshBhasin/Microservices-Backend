from fastapi import FastAPI, Request
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from fastapi import FastAPI, Request
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from dotenv import load_dotenv
from pyngrok import ngrok
import os

load_dotenv()
app = FastAPI()
public_url = None
_use_ngrok = os.getenv("QUICKBOOKS_USE_NGROK", "0").strip().lower() in ("1", "true", "yes")
if _use_ngrok:
    try:
        public_url = ngrok.connect("8000")
        print(public_url)
    except Exception as e:
        print(f"ngrok connect failed (continuing without ngrok): {e}")
else:
    print("ngrok disabled via QUICKBOOKS_USE_NGROK; not opening tunnel")
auth_client = AuthClient(
    client_id=os.getenv("QUICKBOOKS_CLIENT_ID"),
    client_secret=os.getenv("QUICKBOOKS_CLIENT_SECRET"),
    redirect_uri=os.getenv("QUICKBOOKS_CONNECT_URL"),
    environment="sandbox"
)

@app.get("/")
def root():
    if public_url:
        return {"ngrok_url": getattr(public_url, "public_url", str(public_url))}
    return {"status": "QuickBooks API Server Running", "ngrok_url": None}

@app.get("/login")
def login():
    # Step 1: Generate authorization URL
    auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    return {"auth_url": auth_url}

@app.get("/callback")
def callback(request: Request):
    # Step 2: Capture code + realmId after QuickBooks redirects
    code = request.query_params.get("code")
    realm_id = request.query_params.get("realmId")

    print("Authorization Code:", code)
    print("Realm ID:", realm_id)

    if not code or not realm_id:
        return {"error": "Missing code or realmId"}

    # Step 3: Exchange code for tokens
    auth_client.get_bearer_token(code, realm_id=realm_id)
    print (auth_client)
   
    # Step 4: Create QuickBooks client and fetch data
    qbo = QuickBooks(
        auth_client=auth_client,
        refresh_token=auth_client.refresh_token,
        company_id=realm_id
    )
    company_info = qbo.get('CompanyInfo', realm_id)
    if company_info:
        company_name = company_info[0].CompanyName
    else:
        company_name = None

    return {
        "realm_id": realm_id,
        "company_name": company_name,
        "access_token": auth_client.access_token
    }
    
