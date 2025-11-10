from fastapi import APIRouter, Body, HTTPException, status, Response, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import members, whispers, reports
import nest_asyncio
import uvicorn


app = FastAPI()

origins = [
    'https://67102efe0111.ngrok-free.app',
    "https://awless-kathryn-always.ngrok-free.dev",
    "http://localhost:3000",
    '*',
]
@app.middleware("http")
async def log_request(request, call_next):
    print("📥 Headers:", request.headers)
    return await call_next(request)

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

app.include_router(members.router, tags=["Members"], prefix="/members")
app.include_router(whispers.router, tags=["Whispers"], prefix="/whispers")
app.include_router(reports.router, tags=["Reports"], prefix="/reports")

@app.get("/test")
async def hello():
    return "테스트 출력 성공"

nest_asyncio.apply()  # Jupyter 환경용
uvicorn.run(app, host="0.0.0.0", port=8001, ssl_keyfile="SSL/key.pem", ssl_certfile="SSL/cert.pem")
