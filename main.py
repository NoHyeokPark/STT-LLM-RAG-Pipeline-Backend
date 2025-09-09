from fastapi import APIRouter, Body, HTTPException, status, Response, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import members, whispers
import nest_asyncio
import uvicorn
import os
import imageio_ffmpeg as iio_ffmpeg

ffmpeg_path = iio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
app = FastAPI()

app.include_router(members.router, tags=["Members"], prefix="/members")
app.include_router(whispers.router, tags=["Whispers"], prefix="/whispers")

origins = [
    "http://localhost:3000",  # 클라이언트 주소
    "*"                      # 또는 모든 주소 허용
     ]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

@app.get("/test")
async def hello():
    return "테스트 출력 성공"

nest_asyncio.apply()  # Jupyter 환경용
uvicorn.run(app, host="0.0.0.0", port=8001, ssl_keyfile="SSL/key.pem", ssl_certfile="SSL/cert.pem")
