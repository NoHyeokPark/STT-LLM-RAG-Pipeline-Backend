import os
from langchain_community.document_loaders import WikipediaLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 1. 위키피디아 데이터 로드
# '대한민국' 페이지의 콘텐츠를 로드합니다.
def wiki_data_load( query: str, search: str):
    print(f"📜 {search} 위키피디아 페이지를 로딩합니다...")
    loader = WikipediaLoader(search, lang='ko', load_max_docs=1)
    documents = loader.load()
    print(f"✅ 총 {len(documents)}개의 문서를 로드했습니다.")
    print("\n✂️ 텍스트를 청크 단위로 분할합니다...")
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print(f"✅ 텍스트를 총 {len(docs)}개의 청크로 분할했습니다.")
    # 3. 로컬 임베딩 모델 준비
    # sentence-transformers를 사용하여 로컬에서 텍스트를 벡터로 변환합니다.
    # 'jhgan/ko-sroberta-multitask'는 한국어 문장 임베딩에 특화된 모델입니다.
    print("\n🧠 로컬 임베딩 모델을 로드합니다 (최초 실행 시 시간이 소요될 수 있습니다)...")
    model_name = "jhgan/ko-sroberta-multitask"
    model_kwargs = {'device': 'cuda'}  # GPU 사용 시 'cuda'로 변경
    encode_kwargs = {'normalize_embeddings': True}  # 벡터 정규화
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    print(f"✅ '{model_name}' 모델 로드 완료.")
    # 4. 벡터 DB 생성 및 저장
    # 준비된 임베딩 모델을 사용하여 텍스트 청크를 벡터로 변환하고 FAISS DB에 저장합니다.
    print("\n💿 텍스트를 벡터로 임베딩하고 FAISS DB에 저장합니다...")
    db = FAISS.from_documents(docs, embeddings)
    print("✅ FAISS 벡터 DB 생성 및 저장이 완료되었습니다.")

    # 5. 벡터 DB 유사도 검색 테스트
    # 저장된 벡터 DB를 활용하여 특정 질문과 가장 유사한 내용을 검색합니다.
    print("\n🔍 저장된 벡터 DB에서 유사도 검색을 테스트합니다...")
    retrieved_docs = db.similarity_search(query, k=1)

    print(f"\n[질문]: {query}")
    ans = []
    for i, doc in enumerate(retrieved_docs):
        ans.append(doc.page_content)
    return ans    