import os, logging
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from services import doorloop_services as services
except Exception as e:
    logging.exception(" The Mcp service file never imported")
    