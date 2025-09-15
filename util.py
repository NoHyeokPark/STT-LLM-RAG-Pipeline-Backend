import datetime

def format_timestamp(seconds: float) -> str:
    """초 단위를 HH:MM:SS,ms 형식의 문자열로 변환합니다."""
    # datetime.timedelta를 사용하면 시간 계산이 더 정확하고 간편합니다.
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"