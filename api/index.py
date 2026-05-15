from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from tools.weather import get_weather
from tools.search import web_search

app = FastAPI()

# Tool Registry
TOOLS = {"get_weather": get_weather, "web_search": web_search}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join("static", "index.html"), "r") as f:
        return f.read()

@app.post("/api/agent")
async def ai_agent(request: Request):
    body = await request.json()
    user_input = body.get("query", "").lower()
    
    try:
        if "weather" in user_input:
            city = user_input.split("in")[-1].strip() or "Karachi"
            data = TOOLS["get_weather"](city)
            return {"status": "success", "tool": "Weather", "data": data}
        
        elif "search" in user_input:
            query = user_input.replace("search", "").strip()
            data = TOOLS["web_search"](query)
            return {"status": "success", "tool": "Search", "data": data}
        
        return JSONResponse(status_code=400, content={"status": "error", "message": "I don't know how to do that yet!"})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})