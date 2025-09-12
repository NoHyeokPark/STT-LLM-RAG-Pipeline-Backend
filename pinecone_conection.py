from pinecone import Pinecone

pc = Pinecone(api_key="pcsk_6ez6FA_4UEaaQ8CaBkX4vDy3oFVqt6gzp7Fr6MCeEJuk3qRv7CHhpeM96ZFYhZSCAj8mM4")
index = pc.Index("rag")

def RAG_search(keyword: str, top_k: int, space: str = "arXiv"):
    results = index.search(
        namespace=space, 
        query={
            "inputs": {"text": keyword}, 
            "top_k": top_k
        },
        fields=["link", "title"]
    )
    return results