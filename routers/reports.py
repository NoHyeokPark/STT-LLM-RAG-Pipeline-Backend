from database import html_collection
from models import htmlModel
from fastapi import APIRouter, HTTPException, status, Body, Query
from typing import List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from fastapi import Depends
from typing import Annotated
from datetime import datetime


router = APIRouter()

@router.get("/")
async def hello():
    return "HTML 문서 저장 서비스 API입니다."

@router.post("/insert", response_description="새로운 HTML 문서 추가", response_model=htmlModel, status_code=status.HTTP_201_CREATED)
async def create_html_document(html: htmlModel = Body(...)):
    """
    새로운 HTML 문서를 생성하여 데이터베이스에 저장합니다.

    - **title**: 문서의 제목
    - **content**: HTML 본문 내용
    - **participants**: 문서에 참여한 사용자 이메일 리스트
    """
    # Pydantic 모델을 dict로 변환
    html_dict = html.model_dump()
    
    # 서버에서 현재 시간을 'uploadedAt' 필드에 추가
    html_dict['uploadedAt'] = datetime.now()

    # 데이터베이스에 삽입
    new_html = await html_collection.insert_one(html_dict)
    
    # 삽입된 문서를 다시 조회하여 클라이언트에 반환
    created_html = await html_collection.find_one({"_id": new_html.inserted_id})

    if created_html is None:
        raise HTTPException(status_code=404, detail="Document could not be created")

    return created_html

@router.get("/list", response_description="모든 HTML 문서 조회", response_model=List[htmlModel])
async def list_html_documents():
    """
    (임시)데이터베이스에 저장된 모든 HTML 문서를 조회합니다.
    """
    documents = []
    cursor = html_collection.find()
    async for document in cursor:
        documents.append(document)
    return documents

@router.get("/me", response_description="특정 사용자의 HTML 문서 조회", response_model=List[htmlModel])
async def get_html_document(id: str = Query(..., description="조회할 문서의 ID")):
    """
    주어진 ID에 해당하는 HTML 문서를 조회합니다.

    - **id**: 조회할 문서의 ID
    """
    cursor = html_collection.find({'participants': id})
    documents = await cursor.to_list(length=1000)
    return documents      

@router.delete("/delete/{id}", response_description="특정 HTML 문서 삭제")


async def delete_html_document(id: str):    
    """
    주어진 ID에 해당하는 HTML 문서를 삭제합니다.

    - **id**: 삭제할 문서의 ID
    """
    delete_result = await html_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return {"result": "success", "message": f"Document with ID {id} has been deleted."}

    raise HTTPException(status_code=404, detail=f"Document with ID {id} not found")

@router.put("/update/{id}", response_description="특정 HTML 문서 수정", response_model=htmlModel)
async def update_html_document(id: str, html: htmlModel = Body(...)):
    """
    주어진 ID에 해당하는 HTML 문서를 수정합니다.

    - **id**: 수정할 문서의 ID
    - **html**: 수정할 HTML 문서 데이터
    """
    html_dict = {k: v for k, v in html.model_dump().items() if v is not None}

    if len(html_dict) >= 1:
        update_result = await html_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": html_dict}
        )

        if update_result.modified_count == 1:
            if (
                updated_document := await html_collection.find_one({"_id": ObjectId(id)})
            ) is not None:
                return updated_document

    if (existing_document := await html_collection.find_one({"_id": ObjectId(id)})) is not None:
        return existing_document

    raise HTTPException(status_code=404, detail=f"Document with ID {id} not found") 

# 추가적인 엔드포인트나 기능을 여기에 구현할 수 있습니다.
# 예: 특정 사용자의 문서만 조회하는 기능 등

