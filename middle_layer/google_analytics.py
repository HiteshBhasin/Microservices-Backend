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
    
active_user = google_analytics.get_active_users()
# for debugging purpose


country_analysis  = google_analytics.get_analytics_by_country()



if __name__ == "__main__":
    print(active_user)
    print(country_analysis)
    
    
    


    
    

