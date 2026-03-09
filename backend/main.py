from fastapi import FastAPI
from database import engine, Base
from routers import users, capsules, files, ai
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AR Memory Capsule Backend")

# Mount static for media (in real app, use nginx/CDN)
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(users.router)
app.include_router(capsules.router)
app.include_router(files.router)
app.include_router(ai.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AR Memory Capsule API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
