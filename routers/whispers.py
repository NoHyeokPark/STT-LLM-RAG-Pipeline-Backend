from fastapi import APIRouter
from fastapi import File, UploadFile
from typing import List, Dict, Tuple
from datetime import datetime
import whisper as whisper_model
import torch
import tempfile
import traceback
import os
import httpx
import imageio_ffmpeg as iio_ffmpeg
from pinecone_conection import RAG_search
import asyncio

router = APIRouter()
LLM_URL = "https://172.31.57.143:8010"
device = "cuda" if torch.cuda.is_available() else "cpu"

model = whisper_model.load_model("large-v3-turbo", device=device)

@router.get("/")
async def hello():
    return "STT 서비스용 API입니다."

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
        async with httpx.AsyncClient(verify=False) as client:
            try:
                # 비동기 GET 요청 보내기
                response = await client.post(f"{LLM_URL}/process_llm", json={'text': transcribed_text}, timeout=300.0)
                response.raise_for_status()
                print('✅ LLM 서버 응답 성공:')
                data = response.json()
                print(data)
                report = await asyncio.to_thread(RAG_search, data['final'], 3, "arXiv")
                pdf_link = [hit['_id'] for hit in report['result']['hits']]
                print("🔍 RAG 검색 결과:"
                      , pdf_link)
                await client.post(f"{LLM_URL}/process_llm2", json={'text': data['final'], 'pdf':pdf_link}, timeout=300.0)
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
        if not filename.endswith((".mp4", ".webm")):
            raise ValueError(f"mp4 또는 webm 파일만 지원합니다: {filename}")
        
        ext = ".webm" if filename.endswith(".webm") else ".mp4"
        
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