from fastapi import FastAPI, Request, WebSocket 
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

clients = []  # Fixed variable name (was 'client')

@app.get('/')
async def get_dashboard_response():  # Fixed method name (typo)
    html_resp = """  # Fixed variable name (typo)
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
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const li = document.createElement("li");
            li.textContent = `New Form Submission: ${JSON.stringify(data)}`;
            document.getElementById("events").appendChild(li);
        };
        
        // Fixed JavaScript syntax errors:
        // - Changed 'Const' to 'const'
        // - Changed 'websocket_resp' to proper WebSocket implementation
        // - Fixed variable name from 'resp' to 'data'
    </script>
</body>
</html> 
    """
    return HTMLResponse(html_resp)  # Fixed variable name

@app.websocket('/ws')
async def get_websocket(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)  # Fixed variable name
    try:
        while True:
            await websocket.receive_text()
    except:
        clients.remove(websocket)  # Fixed variable name
            
@app.post('/connecteam-webhook')
async def connecteam_webhook(request: Request):
    payload = await request.json()
    print(payload)
    
    for ws in clients:  # Fixed variable name
        await ws.send_text(json.dumps(payload))
    
    return {"Status": "ok"}