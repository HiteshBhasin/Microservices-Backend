from fastapi import FastAPI , Request, WebSocket 
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

client = []

@app.get('/')
async def get_dashboard_responce():
    httml_resp = """
               <!DOCTYPE html>
<html lang="en">
        <head>
                 <meta charset="UTF-8">
                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Dashboard Form</title>
        </head>
        <body>
        <ul id="events"></ul>
            <script>
                const websocket_resp =(event)=>{
                    const resp = JSON.parse(event.data)
                    Const li = document.createElement("li");
                    li.textContent = `New Form Submission: ${JSON.stringify(data)}`;
                    document.getElementById("events").appendChild(li);
                }
            </script>
        </body>
</html> 
    
    """
    return HTMLResponse(httml_resp)

@app.websocket('/ws')
async def get_websocket(websocket:WebSocket):
    await websocket.accept()
    client.append(websocket)
    try:
        while True:
           await websocket.receive_text()
    except:
        client.remove(websocket)
        
            
@app.post('/connecteam-webhook')
async def connecteam_webhook(request:Request):
    payload = await request.json()
    print(payload)
    
    for ws in client:
        await ws.send_text(json.dumps(payload))
    
    return {"Status":"ok"}
    
    
if __name__=="__main__()":
    import uvicorn ,os
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
   