import arxiv
import pandas as pd
from datetime import datetime
import uuid
from pinecone_conection import index
def crawl_and_save_arxiv_papers(search_query, max_results=100):
    """
    지정된 검색어로 arXiv에서 최신 논문을 검색하고 CSV 파일로 저장합니다.

    Args:
        search_query (str): 검색할 쿼리.
        max_results (int): 가져올 논문의 최대 개수.
    """
    client = arxiv.Client()
    # arXiv API를 사용하여 최신 논문 검색
    search = arxiv.Search(
      query = search_query,
      max_results = max_results,
      sort_by = arxiv.SortCriterion.SubmittedDate
    )

    # 필요한 정보를 담을 리스트 초기화
    data = []

    # 검색 결과 반복
    for result in client.results(search):
        vector_id = str(uuid.uuid4())
        data.append({
            'id': vector_id,
            'text': result.summary,
            "link": result.pdf_url,
            "title": result.title,
          
        })

    upsert_response = index.upsert_records(
    namespace="arXiv",
    records=data
    )    

if __name__ == '__main__':
    # 'LLM'을 검색어로 사용하여 최신 논문 100개를 크롤링하고 저장
    crawl_and_save_arxiv_papers(search_query='Music', max_results=96)