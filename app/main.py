from fastapi import FastAPI

from app.routers.router import router as agent_router


app = FastAPI(title="CodePilot API", version="5.0.0")

app.include_router(agent_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodePilot"
    }