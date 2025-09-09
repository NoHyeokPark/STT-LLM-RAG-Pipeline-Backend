from fastapi import APIRouter, Body, HTTPException, status, Response, Query, Depends
from starlette.responses import JSONResponse
from typing import List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
import bcrypt
from pymongo import MongoClient
from datetime import datetime, timedelta

# 이 파일 내에서는 데이터베이스와 모델을 직접 임포트합니다.
from database import student_collection
from models import UpdateUserModel, UserModel

# APIRouter 인스턴스 생성
router = APIRouter()
SECRET_KEY = 'POLYTEC_AISW_HITECH_2025_SECRET'
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    토큰을 검증하고, 유효하다면 해당 유저 정보를 반환하는 의존성 함수입니다.
    이 함수를 Depends()로 사용하는 API는 자동으로 토큰 인증을 거치게 됩니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰 디코딩 및 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("id")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # DB에서 사용자 정보 조회
    user = await student_collection.find_one({"id": username})
    if user is None:
        raise credentials_exception
    
    # 비밀번호는 제외하고 사용자 정보 반환
    user_info = {"id": user["id"], "name": user["name"]}
    return user_info


def user_helper(student) -> dict:
    return {
        "uid": str(student["_id"]),
        "name": student["name"],
        "id": student["id"],
        "pw": student["pw"],
    }

# READ: 모든 학생 조회
@router.get("/", response_description="List all users", response_model=List[UserModel])
async def list_students(    skip: int = Query(0,
                       title="Skip",
                       description="건너뛸 데이터의 수 (페이지네이션 시작점).",
                       ge=0), # ge=0: 0보다 크거나 같은 값만 허용
                            limit: int = Query(10,
                       title="Limit",
                       description="한 페이지에 가져올 최대 데이터의 수.",
                       ge=1, # ge=1: 1 이상의 값만 허용
                       le=100) # le=100: 100 이하의 값만 허용
):
    # .skip()과 .limit()을 find()에 연결
    cursor = student_collection.find().skip(skip).limit(limit)
    students = [user_helper(student) async for student in cursor]
    return students

# CREATE: 새 학생 추가
@router.post("/register",
             response_description="Add new user",
             status_code=status.HTTP_201_CREATED) # <--- 1. 상태 코드 여기로 이동
async def create_user(user: UserModel = Body(...)): # <--- 2. 이름 일관성 있게 변경
    try:
        password = user.pw  # 평문 비밀번호
            # 비밀번호 해싱
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user.pw = hashed_password.decode('utf-8')  # 해싱된 비밀번호로 교체
        user_dict = user.dict()
        new_user = await student_collection.insert_one(user_dict)

        # 3. 불필요한 find_one 제거하고 직접 응답 구성
        # user_helper가 ObjectId를 str으로 변환한다고 가정
        created_user = await student_collection.find_one({"_id": new_user.inserted_id})
        return {'result': 'success', 'message': '회원가입이 완료되었습니다.'}

    except DuplicateKeyError:
        # 4. 이 구문이 동작하려면 MongoDB에 unique index가 반드시 필요함
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with email '{user.id}' already exists")

# login: 사용자 로그인
@router.post("/login",
             response_description="Login user",
             status_code=status.HTTP_202_ACCEPTED) # <--- 1. 상태 코드 여기로 이동
async def login_user(user: UserModel = Body(...)): # <--- 2. 이름 일관성 있게 변경
    try:
        # 클라이언트로부터 username, password 받기
        username = user.id
        password = user.pw

        if not (username and password):
            raise HTTPException(status_code=400, detail="아이디와 비밀번호를 모두 입력해주세요.")

        # 데이터베이스에서 사용자 찾기
        user = await student_collection.find_one({"id": username})
        if not user:
            raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
        # 사용자가 존재하고, 비밀번호가 일치하는지 확인
        if bcrypt.checkpw(password.encode('utf-8'), user['pw'].encode('utf-8')):
            # JWT 페이로드(Payload) 설정
            payload = {
                'id': username,
                'exp': datetime.now() + timedelta(hours=1)  # 토큰 만료 시간 (1시간)
            }
            # JWT 생성
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

            return {"access_token": token, "token_type": "bearer"}

        else:
            # 사용자가 없거나 비밀번호가 틀린 경우
            raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 일치하지 않습니다.")

    except Exception as e:
        return {'error': str(e)}


# DELETE: 사용자 정보 삭제
@router.delete("/", response_description="Delete a user")
async def delete_student(current_user: Annotated[dict, Depends(get_current_user)]): # -> Response 타입 힌트 제거 또는 Response 임포트
    user_id = current_user["id"]  # dict에서 id 가져오기

    delete_result = await student_collection.delete_one({"id": user_id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Student with id {user_id} not found"
    )