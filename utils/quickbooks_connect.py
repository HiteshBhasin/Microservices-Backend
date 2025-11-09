from fastapi import FastAPI, Request
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from dotenv import load_dotenv
from pyngrok import ngrok
import os


ngrok.connect("8000")
load_dotenv()
app = FastAPI()

auth_client = AuthClient(
    client_id=os.getenv("QUICKBOOKS_CLIENT_ID"),
    client_secret=os.getenv("QUICKBOOKS_CLIENT_SECRET"),
    redirect_uri=os.getenv("QUICKBOOKS_CONNECT_URL", "").strip('"'),
    environment="sandbox"
)

@app.get("/")
def root():
    return {
        "status": "QuickBooks API Server Running",
        "redirect_uri": os.getenv("QUICKBOOKS_CONNECT_URL", "").strip('"')
    }

@app.get("/login")
def login():
    #  Generate authorization URL
    auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING, Scopes.PAYMENT])
    return {"auth_url": auth_url}

@app.get("/callback")
def callback(request: Request):
    try:
        #  Capture code + realmId after QuickBooks redirects
        code = request.query_params.get("code")
        realm_id = request.query_params.get("realmId")

        print("Authorization Code:", code)
        print("Realm ID:", realm_id)

        if not code or not realm_id:
            return {"error": "Missing code or realmId"}

        # Exchange code for tokens
        auth_client.get_bearer_token(code, realm_id=realm_id)
        print("Auth client:", auth_client)
       
        #  Create QuickBooks client
        from quickbooks.objects.company_info import CompanyInfo
        
        qbo = QuickBooks(
            auth_client=auth_client,
            refresh_token=auth_client.refresh_token,
            company_id=realm_id
        )
        
        # Query CompanyInfo correctly
        company_info = CompanyInfo.get(realm_id, qb=qbo)
        company_name = company_info.CompanyName if company_info else None

        return {
            "realm_id": realm_id,
            "company_name": company_name,
            "access_token": auth_client.access_token
        }
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "details": "Check server logs for more information"}
