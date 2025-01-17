from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.database import create_db_and_tables
from app.core.config import Settings
import uvicorn


settings = Settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    await create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
