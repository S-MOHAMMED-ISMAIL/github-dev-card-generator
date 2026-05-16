import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent import github_card_agent
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="GitHub Dev Card Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists and mount it
static_path = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(static_path, "cards"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

class GenerateRequest(BaseModel):
    username: str
    theme: str = "dark"

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def serve_frontend():
    if os.path.exists(frontend_path):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    return {"status": "Backend API is running"}

@app.post("/generate")
async def generate_card(request: GenerateRequest):
    try:
        result = await github_card_agent.run_agent(
    request.username,
    request.theme
)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def get_card(username: str):
    file_path = os.path.join(static_path, "cards", f"{username}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Card not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
