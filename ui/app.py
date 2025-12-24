from fastapi import FastAPI
from ui.routes.portfolio import router as portfolio_router
from ui.routes.health import router as health_router

app = FastAPI(
    title="Crypto Portfolio Tracker",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(portfolio_router)
