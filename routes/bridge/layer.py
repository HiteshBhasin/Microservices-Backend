import redis 
from redis.cache import CacheConfig 
import logging
class middle_layer:
    def __init__(self) -> None:
        pass
    
    def connecte_redis(self, redis, data):
        r = redis.Redis(host = 'localhost',port= 6379, decode_responses= True)
        if not r:
            return f"Connection was un-successful , {r}"
        try:
            r.get(data)
            r.set('data', data)
            return True 
        except:
            return False 
    
    def layer_extraction(self,raw_date):
        dataobj = {}
        if len(raw_date)==0:
            logging.error("Error ! No data came through please check again")
        try:
            data = raw_date['data']
            for i in range(len(data)):
                dataobj['email'] = data[i]["emails"]
                dataobj ['first-name'] = data[i]["firstName"]
                dataobj ['last-name'] = data[i]["lasttName"]
                dataobj ['phone'] = data[i]["pstatushones"]
                dataobj ['status'] = data[i]["status"]

        except Exception as e:
            logging.exception(f"There was an error {e}")
        
            
            
                
                
            
            
            
        
        
