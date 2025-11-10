from fastapi import APIRouter
from fastapi import File, UploadFile, HTTPException
from typing import List, Dict, Tuple
from datetime import datetime
import whisper as whisper_model
import torch
import tempfile
import traceback
import os
import httpx
from pinecone_conection import RAG_search
import shutil
import asyncio
from util import format_timestamp
from pathlib import Path  # 경로 처리를 위한 모듈 추가
from models import TranscriptRequest, LocalFileAdapter
from database import insert_html_document
from wiki import wiki_data_load


router = APIRouter()
LLM_URL = "https://sliceable-maryanne-unforcedly.ngrok-free.dev"
device = "cuda" if torch.cuda.is_available() else "cpu"
UPLOAD_BASE_DIR = Path("uploads")
model = whisper_model.load_model("large-v3-turbo", device=device)

headers = {
    "ngrok-skip-browser-warning": "true"
}

@router.get("/")
async def hello():
    return "STT 서비스용 API입니다."

@router.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    """비디오 파일을 업로드하여 폴더에 저장"""
    try:
        # 업로드 파일명/확장자 확인
        filename = file.filename or ""
        if not filename.lower().endswith((".mp4", ".webm", ".wav", "mp3")):
            raise HTTPException(status_code=400, detail="mp4, webm, 또는 wav, mp3 파일만 지원합니다.")

        # --- 수정된 부분 시작 ---

        # 1. 파일명에서 폴더 이름 추출
        # 파일명 형식: "스피커명_폴더명.확장자" (예: "John_ProjectA.mp4")
        filename_stem = Path(filename).stem  # 확장자를 제외한 파일명 (예: "John_ProjectA")
        parts = filename_stem.split('_')

        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="파일명은 '스피커명_폴더명' 형식이어야 합니다.")
        
        # speaker_label = parts[0] # 필요 시 스피커명도 변수로 저장
        directory_name = parts[1]  # '_'의 두 번째 부분을 폴더 이름으로 사용

        # 2. 폴더 생성
        # 최종 저장 폴더 경로 (예: uploads/ProjectA)
        save_directory = UPLOAD_BASE_DIR / directory_name
        save_directory.mkdir(parents=True, exist_ok=True)  # 폴더가 이미 있어도 에러 없음

        # 3. 해당 폴더 안에 동영상 저장
        # 최종 파일 저장 경로 (예: uploads/ProjectA/John_ProjectA.mp4)
        video_path = save_directory / filename
        
        video_bytes = await file.read()
        with open(video_path, "wb") as buffer:
            buffer.write(video_bytes)

        # --- 수정된 부분 끝 ---

        # 이후 비디오 처리 로직에서는 위에서 저장된 `video_path`를 사용하면 됩니다.
        # 예: result = model.transcribe(str(video_path), ...)
        print(f"파일이 성공적으로 저장되었습니다: {video_path}")
        return {"status": "success", "message": f"파일이 성공적으로 저장되었습니다."}

    except Exception as e:
        # 에러 처리를 위해 HTTPException을 사용하는 것이 좋습니다.
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"서버 처리 중 오류가 발생했습니다: {str(e)}")

@router.post("/button")
async def process_videos_from_directory(request: TranscriptRequest):
    """폴더명을 받아 해당 폴더의 모든 비디오를 처리하여 통합 회의록 생성 후 폴더 삭제"""
    
    target_dir = UPLOAD_BASE_DIR / request.directory_name
    print(f"process_videos 시작 - 폴더 처리: {target_dir}")

    # 1. 대상 폴더 존재 여부 확인
    if not target_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"폴더를 찾을 수 없습니다: {request.directory_name}")

    try:
        # 2. 폴더 내 모든 비디오 파일 목록 가져오기
        supported_extensions = ["*.mp4", "*.webm", "*.wav", "*.mp3"]
        video_files = []
        for ext in supported_extensions:
            video_files.extend(target_dir.glob(ext))
        
        if not video_files:
            raise HTTPException(status_code=400, detail="폴더에 처리할 비디오 파일이 없습니다.")

        # 3. 각 파일을 개별적으로 전사
        all_segments = []
        participants = []
        for i, video_path in enumerate(video_files):
            print(f"파일 {i+1}/{len(video_files)} 처리 중: {video_path.name}")
            filename_stem = video_path.stem  # 확장자를 제외한 파일명
            parts = filename_stem.split('_')
            username = parts[0] if len(parts) > 0 else filename_stem
            if username not in participants:
                participants.append(username)
            
            segments, error = await transcribe_single_file(LocalFileAdapter(video_path))
            if error:
                raise HTTPException(status_code=500, detail=f"파일 {video_path.name} 처리 중 오류: {error}")
            
            all_segments.extend(segments)

        
        # 4. 시간순으로 정렬 및 회의록 생성 (기존 로직과 동일)
        srt_blocks = []
        # enumerate를 사용하여 1부터 시작하는 순번(index)을 생성
        for index, segment in enumerate(all_segments, 1):
            # 타임스탬프를 HH:MM:SS,ms 형식으로 변환
            start_time = format_timestamp(segment["start_time"])
            end_time = format_timestamp(segment["end_time"])
            
            # SRT 형식에 맞춰 블록 생성
            block = (
                f"{index}\n"
                f"{start_time} --> {end_time}\n"
                f"[{segment['username']}]: {segment['text']}"
            )
            srt_blocks.append(block)     

        # 각 블록을 두 번의 줄바꿈으로 연결하여 최종 SRT 형식 텍스트 완성
        transcribed_text = "\n".join(srt_blocks)

        
        # 5. 작업 완료 후 폴더 삭제
        shutil.rmtree(target_dir)
        print(f"작업 완료, 폴더 삭제: {target_dir}")

        print('Transcription completed. Sending to LLM server...')    

        # 결과 반환
        async with httpx.AsyncClient(verify=False) as client:
            try:
                # 비동기 GET 요청 보내기
                response = await client.post(f"{LLM_URL}/process_llm", json={'text': transcribed_text}, headers=headers, timeout=300.0)
                response.raise_for_status()
                print('✅ LLM 서버 응답 성공:')
                data = response.json()
                report = await asyncio.to_thread(RAG_search, data['final'], 3, "arXiv")
                pdf_link = [hit['fields']['link'] for hit in report['result']['hits']]
                pdf_title = [hit['fields']['title'] for hit in report['result']['hits']]
                news = await asyncio.to_thread(RAG_search, data['final'], 5, "news")
                news_link = [hit['fields']['link'] for hit in news['result']['hits']]
                news_title = [hit['fields']['title'] for hit in news['result']['hits']]
                wiki = []
                for x in data['top3']:
                    wiki.append(wiki_data_load(data['final'], x))
                res = await client.post(f"{LLM_URL}/process_llm2", json={'text': transcribed_text, 'summary':data['final'], 'actions_table':data['actions_table'],
                                                                   'pdf_link':pdf_link, 'pdf_title':pdf_title, 'wiki':wiki, 'top3':data['top3'],
                                                                   'news_link':news_link, 'news_title':news_title}, headers=headers, timeout=300.0)
                res.raise_for_status()
                print('✅ LLM 서버 응답 성공:')
                final_data = res.json()
                print(final_data['status'])
                # DB에 저장
                html_dict = {
                    "title": f"회의록_{request.directory_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "content": final_data['report'],
                    "uploadedAt": request.date,  # insert_html_document 함수에서 현재 시간으로 설정
                    "participants": participants
                }
                created_html = await insert_html_document(html_dict)
                print(f"DB에 회의록 저장 완료: {created_html.get('_id')}")
            except httpx.TimeoutException as e:
                # 타임아웃 에러를 명확하게 로깅하거나 반환
                print(f"Request timed out: {e}")
                return {"error": "The request to the LLM server timed out."}
            except httpx.RequestError as e:
                # 그 외 네트워크 관련 에러
                return {"error": f"An error occurred while requesting {e.request.url!r}."}
            except httpx.HTTPStatusError as e:
                # 4xx, 5xx 에러 (예: LLM 서버 내부 에러)
                return {"error": f"LLM server returned an error: {e.response.status_code}", "details": e.response.text}
                
        return {"status": "success" , "transcription": "회의 요약이 발송되었습니다."}        
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        # HTTPException인 경우 그대로 전달, 아닌 경우 500 에러로 래핑
        if isinstance(e, HTTPException):
            raise e
        return {
            "status": "error",
            "message": str(e),
            "traceback": error_traceback
        }

@router.post("/process_video2")
async def process_video2(file: UploadFile = File(...)):
    """하나의 비디오 파일을 처리하여 요약본 생성"""
    try:
        # 업로드 파일명/확장자 확인
        filename = (file.filename or "").lower()
        if not filename.endswith((".mp4", ".webm", ".wav")):
            return {"status": "error", "message": "mp4 또는 webm 또는 wav 파일만 지원합니다."}
        ext_map = {".webm": ".webm", ".mp4": ".mp4", ".wav": ".wav"}
        ext = next((v for k, v in ext_map.items() if filename.endswith(k)), None)

        # 업로드 파일을 메모리에서 읽기
        video_bytes = await file.read()
        _, ext = os.path.splitext(file.filename)
        speaker_label = file.filename.split('_')[0]
        # 임시로 업로드 확장자에 맞춰 저장
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_video:
            temp_video.write(video_bytes)
            video_path = temp_video.name


        # 3) Whisper로 음성 → 텍스트 변환
        result = model.transcribe(video_path, fp16=(device == "cuda"))
        # 3) 결과 포맷팅 (SRT와 유사한 형식)
        srt_blocks = []
        if "segments" in result:
            # enumerate를 사용해 1부터 시작하는 순번(index)을 생성
            for index, segment in enumerate(result["segments"], 1):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                text = segment["text"].strip()
                
                # 요청한 형식에 맞춰 블록 생성
                block = (
                    f"{index}\n"
                    f"{start_time} --> {end_time}\n"
                    f"[{speaker_label}]: {text}"
                )
                srt_blocks.append(block)

        # 각 블록을 두 번의 줄바꿈으로 연결하여 최종 텍스트 생성
        transcribed_text = "\n".join(srt_blocks)

        # 임시 파일 정리
        if os.path.exists(video_path):
            os.unlink(video_path)

        print('Transcription completed. Sending to LLM server...')    

        # 결과 반환
        async with httpx.AsyncClient(verify=False) as client:
            try:
                # 비동기 GET 요청 보내기
                response = await client.post(f"{LLM_URL}/process_llm", json={'text': transcribed_text}, timeout=300.0)
                response.raise_for_status()
                print('✅ LLM 서버 응답 성공:')
                data = response.json()
                report = await asyncio.to_thread(RAG_search, data['final'], 3, "arXiv")
                pdf_link = [hit['fields']['link'] for hit in report['result']['hits']]
                pdf_title = [hit['fields']['title'] for hit in report['result']['hits']]
                pdf_text = [hit['fields']['text'] for hit in report['result']['hits']]
                news = await asyncio.to_thread(RAG_search, data['final'], 5, "news")
                news_link = [hit['fields']['link'] for hit in news['result']['hits']]
                news_title = [hit['fields']['title'] for hit in news['result']['hits']]
                news_text = [hit['fields']['text'] for hit in news['result']['hits']]
                wiki = []
                print(transcribed_text[-100:])
                res = await client.post(f"{LLM_URL}/process_llm2", json={'text': transcribed_text, 'summary':data['final'], 'actions_table':data['actions_table'],
                                                                     'wiki':wiki, 'top3':data['top3'],
                                                                   'pdf_link':pdf_link, 'pdf_title':pdf_title,
                                                                   'news_link':news_link, 'news_title':news_title,}, timeout=600.0)
                res.raise_for_status()
                print('✅ LLM 서버 응답 성공:')
                final_data = res.json()
                print(final_data['status'])

            except httpx.TimeoutException as e:
                # 타임아웃 에러를 명확하게 로깅하거나 반환
                print(f"Request timed out: {e}")
                return {"error": "The request to the LLM server timed out."}
            except httpx.RequestError as e:
                # 그 외 네트워크 관련 에러
                return {"error": f"An error occurred while requesting {e.request.url!r}."}
            except httpx.HTTPStatusError as e:
                # 4xx, 5xx 에러 (예: LLM 서버 내부 에러)
                return {"error": f"LLM server returned an error: {e.response.status_code}", "details": e.response.text}
                
        return {"status": "success" , "transcription": "회의 요약이 발송되었습니다."}

    except Exception as e:
        error_traceback = traceback.format_exc()
        # 예외 발생 시 임시 파일 정리
        try:
            if 'video_path' in locals() and os.path.exists(video_path):
                os.unlink(video_path)
        finally:
            return {
                "status": "error",
                "message": str(e),
                "traceback": error_traceback
            }

@router.post("/process_video")
async def process_video(file: UploadFile = File(...)):
    """하나의 비디오 파일을 처리하여 요약본 생성"""
    print("process_video 시작")
    try:
        # 업로드 파일명/확장자 확인
        filename = (file.filename or "").lower()
        if not filename.endswith((".mp4", ".webm", ".wav")):
            return {"status": "error", "message": "mp4 또는 webm 또는 wav 파일만 지원합니다."}
        ext_map = {".webm": ".webm", ".mp4": ".mp4", ".wav": ".wav"}
        ext = next((v for k, v in ext_map.items() if filename.endswith(k)), None)

        # 업로드 파일을 메모리에서 읽기
        video_bytes = await file.read()
        # 임시로 업로드 확장자에 맞춰 저장
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_video:
            temp_video.write(video_bytes)
            video_path = temp_video.name


        # 3) Whisper로 음성 → 텍스트 변환
        result = model.transcribe(video_path, fp16=(device == "cuda"))
        transcribed_text = (result.get("text") or "").strip()

        # 임시 파일 정리
        if os.path.exists(video_path):
            os.unlink(video_path)

        # 결과 반환
        print(transcribed_text)
        return {"status": "success", "transcription": transcribed_text}

    except Exception as e:
        error_traceback = traceback.format_exc()
        # 예외 발생 시 임시 파일 정리
        try:
            if 'video_path' in locals() and os.path.exists(video_path):
                os.unlink(video_path)
        finally:
            return {
                "status": "error",
                "message": str(e),
                "traceback": error_traceback
            }
        
async def transcribe_single_file(file: UploadFile) -> Tuple[List[Dict], str]:
    """단일 파일을 처리하여 화자 정보가 포함된 텍스트 리스트를 반환"""
    try:
        # 업로드 파일명/확장자 확인
        filename = (file.filename or "").lower()
        if not filename.endswith((".mp4", ".webm", ".wav", ".mp3")):
            raise ValueError(f"mp4 또는 webm 파일만 지원합니다: {filename}")
        
        ext_map = {".webm": ".webm", ".mp4": ".mp4", ".wav": ".wav", ".mp3":".mp3"}
        ext = next((v for k, v in ext_map.items() if filename.endswith(k)), None)
        
        # 파일명에서 사용자 이름 추출 (첫 번째 "_" 이전까지)
        original_filename = file.filename or ""
        username = original_filename.split("_")[0] if "_" in original_filename else original_filename
        
        # 업로드 파일을 메모리에서 읽기
        video_bytes = await file.read()
        
        # 임시로 업로드 확장자에 맞춰 저장
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_video:
            temp_video.write(video_bytes)
            video_path = temp_video.name
        
        try:
            # Whisper로 음성 → 텍스트 변환 (타임스탬프 포함)
            result = model.transcribe(video_path, fp16=(device == "cuda"), word_timestamps=True)
            
            # 세그먼트별로 처리하여 타임스탬프 정보 보존
            segments_with_speaker = []
            
            for segment in result.get("segments", []):
                text = segment.get("text", "").strip()
                start_time = segment.get("start", 0)
                end_time = segment.get("end", 0)
                
                if text:  # 빈 텍스트가 아닌 경우만 추가
                    segments_with_speaker.append({
                        "username": username,
                        "text": text,
                        "start_time": start_time,
                        "end_time": end_time,
                        "filename": original_filename
                    })
            
            return segments_with_speaker, ""
            
        finally:
            # 임시 파일 정리
            if os.path.exists(video_path):
                os.unlink(video_path)
                
    except Exception as e:
        return [], str(e)

@router.post("/process_videos")
async def process_videos(files: List[UploadFile] = File(...)):
    """배열로 들어오는 비디오 파일을 처리하여 통합 회의록을 생성"""
    print(f"process_videos 시작 - {len(files)}개 파일 처리")
    
    try:
        all_segments = []
        
        # 각 파일을 개별적으로 처리
        for i, file in enumerate(files):
            print(f"파일 {i+1}/{len(files)} 처리 중: {file.filename}")
            
            segments, error = await transcribe_single_file(file)
            if error:
                return {"status": "error", "message": f"파일 {file.filename} 처리 중 오류: {error}"}
            
            all_segments.extend(segments)
        
        # 시간순으로 정렬 (start_time 기준)
        all_segments.sort(key=lambda x: x["start_time"])
        
        # 회의록 텍스트 생성
        meeting_transcript = []
        for segment in all_segments:
            # 시간 정보를 포함한 형태로 포맷
            timestamp = f"[{segment['start_time']:.1f}s]"
            line = f"{timestamp} {segment['username']}: {segment['text']}"
            meeting_transcript.append(line)
        
        # 최종 회의록 텍스트
        final_transcript = "\n".join(meeting_transcript)
        
        # 현재 시간으로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_filename = f"meeting_transcript_{timestamp}.txt"
        
        return {
            "status": "success", 
            "transcript": final_transcript,
            "total_segments": len(all_segments),
            "processed_files": len(files),
            "suggested_filename": transcript_filename
        }
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        return {
            "status": "error",
            "message": str(e),
            "traceback": error_traceback
        }