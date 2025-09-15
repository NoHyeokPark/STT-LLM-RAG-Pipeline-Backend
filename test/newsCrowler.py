import os
import sys
import urllib.request
import json
import uuid
from pinecone_conection import index
client_id = "biWt2qcmWp5yHuy1DMOC"
client_secret = "3W6gJ_9Y_o"
query = "LLM"
display_count = 50
start = 1
sort = "date"
params = urllib.parse.urlencode({
    "query": query,
    "display": display_count,
    "start": start,
    "sort": sort
})
encText = urllib.parse.quote("LLM")
url = f"https://openapi.naver.com/v1/search/news.json?{params}" # JSON 결과
# url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)

response = urllib.request.urlopen(request)
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
        # 1. JSON 문자열을 파이썬 딕셔너리로 변환합니다.
    data = json.loads(response_body.decode('utf-8'))
    
    # 2. 'items' 키를 통해 뉴스 기사 리스트에 접근합니다.
    items = data['items']
    struct = []
    
    # 3. 반복문을 사용해 각 기사의 정보를 추출하고 출력합니다.
    for item in items:
        title = item['title']
        link = item['originallink']
        description = item['description']
        
        # <b> 태그 등 간단한 HTML 태그를 제거하여 더 깔끔하게 만듭니다.
        title = title.replace('<b>', '').replace('</b>', '')
        description = description.replace('<b>', '').replace('</b>', '')

        print(f"제목: {title}")
        print(f"원본 링크: {link}")
        print("-" * 20) # 기사별로 구분선을 추가합니다.
        vector_id = str(uuid.uuid4())
        struct.append({
            "id": vector_id,
            'link': link,
            'text': description,
            'title': title,
        })

    upsert_response = index.upsert_records(
    namespace="news",
    records=struct
    )
else:
    print("Error Code:" + rescode)