
from mcp.server.fastmcp import FastMCP
import os , pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base64 import urlsafe_b64encode, urlsafe_b64decode
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.message import EmailMessage
from mimetypes import guess_type as guess_mime_type

SCOPES = ['https://mail.google.com/',] # also need to add google addsense and calander web page here
my_email = 'bhasinsukh@gmail.com'

mcp = FastMCP("Gmail MCP Server") 

def credentials():
    creds = None
    
    if os.path.exists("token.pickle"):
        
        with open("token.pickle", "rb") as token:
            creds= pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expires and creds.refresh_token:
                creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.pickle","wb")as token:
            pickle.dump(creds,token)
    return build('gmail','v1',credentials=creds)

service = credentials()

@mcp.tool()
def check_message_type(message, filename):
    content_type, encoded = guess_mime_type(filename)
    if content_type is None or encoded is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/',1) 

    if main_type =='text':
        with open(filename,"rb") as mssg:
            message = MIMEText(mssg.read().decode(), _subtype = sub_type)
        mssg.close()
    elif main_type == 'image':
        with open(filename,'rb') as image_mssg:
            message =  MIMEImage(image_mssg.read(), _subtype = sub_type)
        image_mssg.close()
    else:
        with open(filename,'rb') as basic_mssg:
            message =  MIMEBase(main_type, sub_type)
            message.set_payload(basic_mssg.read())
        basic_mssg.close()
    
    filename = os.path.basename(filename)
    message.add_header('content','attachement', filename = filename)
    return message

@mcp.tool()
def send_message(content, email_from:str,email_to:str,subject:str ):
    auth=service
    try:
        mail_service=build('gmail','v1',credentials=auth)
        message = EmailMessage()
        message.set_content(content)
        
        message["To"]= email_to
        message["from"] = email_from
        message["subject"] = subject
        
        encoded_messg = urlsafe_b64encode(message.as_bytes()).decode()
        
        raw_message = {'raw':encoded_messg}
        
        send_message = {
            mail_service.users()
            .messages()
            .send(raw_message)
            .execute()
        }
    except:
        
    
        
        
        
        
        
        

# https://thepythoncode.com/article/use-gmail-api-in-python
    
    
            
        
        
        

