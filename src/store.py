import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_pdf, chunk_text

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("docs")

def add_pdf(path, source):
    pages = load_pdf(path)
    chunks = chunk_text(pages, source=source)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts).tolist()
    ids = [f"{source}-{i}" for i in range(len(chunks))]
    metadatas = [{"source": c["source"], "page": c["page"]} for c in chunks]
    collection.upsert(ids=ids, documents=texts,
                      embeddings=embeddings, metadatas=metadatas)
    return len(chunks)

def search(question, k=4):
    q = model.encode([question]).tolist()
    res = collection.query(query_embeddings=q, n_results=k)
    results = []
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        results.append({"text": doc, "source": meta["source"], "page": meta["page"]})
    return results

if __name__ == "__main__":
    n = add_pdf("data/sample.pdf", "sample.pdf")
    print(f"Stored {n} chunks")
    for r in search("What is an operating system?"):
        print(f"\n[{r['source']} - page {r['page']}]")
        print(r["text"][:200])
