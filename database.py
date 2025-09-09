# database.py
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB 연결 정보 (Docker 예제 기반)
MONGO_DETAILS = "mongodb://sys:1234@localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)

# 데이터베이스 선택
database = client.meeting

# 컬렉션 선택
student_collection = database.get_collection("members")