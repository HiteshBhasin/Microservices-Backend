from fastapi import FastAPI, Request
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

auth_client = AuthClient(
    client_id=os.getenv("QUICKBOOKS_CLIENT_ID"),
    client_secret=os.getenv("QUICKBOOKS_CLIENT_SECRET"),
    redirect_uri="http://localhost:8000/callback",
    environment="sandbox"
)

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

    # Step 4: Create QuickBooks client and fetch data
    qbo = QuickBooks(
        auth_client=auth_client,
        refresh_token=auth_client.refresh_token,
        company_id=realm_id
    )

    company_info_list = qbo.get('CompanyInfo', qbo.company_id)
    if not company_info_list:
        return {"error": "Failed to retrieve company information"}
    
    company_info = company_info_list[0]
    print("Company Name:", company_info.CompanyName)

    return {"realm_id": realm_id, "company_name": company_info.CompanyName}
