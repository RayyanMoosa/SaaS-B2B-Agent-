from fastapi import FastAPI, Request
from fastapi.responses import Response, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from datetime import datetime

app = FastAPI()

# Allow all CORS (optional, depends on usage)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple JSON file to log opens and clicks
LOG_FILE = "tracking_log.json"

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {"opens": {}, "clicks": {}}

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

@app.get("/track_open")
async def track_open(email_id: str):
    logs = load_logs()
    now = datetime.utcnow().isoformat()

    # Mark email_id as opened
    logs["opens"][email_id] = now
    save_logs(logs)

    # Return a 1x1 transparent pixel
    pixel = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAn8B9uUiMjcAAAAASUVORK5CYII="
    return Response(content=pixel, media_type="image/png")

@app.get("/redirect")
async def redirect(email_id: str, target: str):
    logs = load_logs()
    now = datetime.utcnow().isoformat()

    # Log click time
    logs["clicks"][email_id] = now
    save_logs(logs)

    # Redirect to target URL (Calendly)
    return RedirectResponse(url=target)

@app.get("/stats")
async def stats():
    return load_logs()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
