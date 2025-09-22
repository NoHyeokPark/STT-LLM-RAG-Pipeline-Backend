# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from models import htmlModel
from datetime import datetime
# MongoDB 연결 정보 (Docker 예제 기반)
MONGO_DETAILS = "mongodb://sys:1234@localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)

# 데이터베이스 선택
database = client.meeting

# 컬렉션 선택
student_collection = database.get_collection("members")
html_collection = database.get_collection("html")

async def insert_html_document(html_dict: dict) -> dict:
    """
    새로운 HTML 문서를 생성하여 데이터베이스에 저장합니다.

    - **title**: 문서의 제목
    - **content**: HTML 본문 내용
    - **participants**: 문서에 참여한 사용자 이메일 리스트
    """
    
    # 서버에서 현재 시간을 'uploadedAt' 필드에 추가
    if html_dict['uploadedAt'] is None:
        html_dict['uploadedAt'] = datetime.now()

    # 데이터베이스에 삽입
    new_html = await html_collection.insert_one(html_dict)
    
    # 삽입된 문서를 다시 조회하여 클라이언트에 반환
    created_html = await html_collection.find_one({"_id": new_html.inserted_id})

    if created_html is None:
        raise ValueError("Document could not be created in DB")

    return created_html