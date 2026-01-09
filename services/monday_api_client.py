import os, logging
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# qualified sales board id 3496733949
load_dotenv()

# try:
#     from services import doorloop_services as services
# except Exception as e:
#     logging.exception(" The Mcp service file never imported")

monday_key = os.getenv("MONDAY_COM_API_KEY2")

query = """
      query getBoardId {
        boards {
          id
          name
        }
      }

"""

MONDAY_URL = "https://api.monday.com/v2"

def get_information(query, variables=None):
    headers = {
        "Authorization": monday_key,
        "Content-Type": "application/json",
        "API-Version": "2024-10"
    }
    
    # Monday.com API expects an empty object for variables, not null
    if variables is None:
        variables = {}
    
    try:
        response = requests.post(
            MONDAY_URL,
            json={"query": query, "variables": variables},
            headers=headers
        )
        
        # Print response details for debugging
        # print(f"Status Code: {response.status_code}")
        # print(f"Response: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        maindata = data.get("data")
        return maindata["boards"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making request to Monday.com API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response content: {e.response.text}")
        return None
      
      
      
      



if __name__ == "__main__":
    result = get_information(query=query)
    if result:
        print(result)

  