from pathlib import Path
import sys, logging
from redis import Redis
PROJECT_PATH= Path(__file__).absolute().parent.parent

if str(PROJECT_PATH) not in sys.path:
 	sys.path.insert(0, str(PROJECT_PATH))

from redis_layer import (cache_data_retireive,
                         cache_properties_to_redis,
                         cache_tenants_to_redis,redis)

try:
    from services import google_analytics

except Exception as e:
    logging.exception(f"this is an error loading google analytics {e}")
    
def _helper_function(raw_data:dict):
    if not raw_data:
        return logging.error("there is an issue getting the data")
    
    try:
        if isinstance(raw_data, dict):
            required_data = raw_data.get("data")
            if isinstance(required_data,list):
                for idx, data in enumerate(required_data):
                    flag_value = cache_tenants_to_redis(data)
                    if flag_value==True:
                        retrieved_data = cache_data_retireive(data)
                        return f"caching is successfull!", retrieved_data
    except Exception as e:
        return False 
        logging.exception(f" the data didnt get cc")
        
                  
    
active_user = google_analytics.get_active_users()
try:
    if isinstance(active_user, dict):
        _helper_function(active_user)
except Exception as e:
    logging.exception(f" No services {e}")
    
country_analysis  = google_analytics.get_analytics_by_country()
try:
    if isinstance(country_analysis, dict):
        _helper_function(country_analysis)
except Exception as e:
    logging.exception(f" No services {e}")


if __name__ == "__main__":
    print(active_user)
    print(country_analysis)
    
    
    


    
    

