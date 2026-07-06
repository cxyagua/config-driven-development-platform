from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from app.db_init import init_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} API"}