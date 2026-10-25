from pypdf import PdfReader

def load_pdf(path):
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((i, text))
    return pages

def chunk_text(pages, source, chunk_size=800, overlap=150):
    chunks = []
    for page_num, text in pages:
        start = 0
        while start < len(text):
            piece = text[start:start + chunk_size].strip()
            if piece:
                chunks.append({"text": piece, "source": source, "page": page_num})
            start += chunk_size - overlap
    return chunks

if __name__ == "__main__":
    pages = load_pdf("data/sample.pdf")
    chunks = chunk_text(pages, source="sample.pdf")
    print(f"Pages: {len(pages)}, Chunks: {len(chunks)}")
    print(chunks[0])
