# 📄 AskMyDocs

A Retrieval-Augmented Generation (RAG) app that lets you upload PDFs and ask questions in plain language. Every answer is grounded in your document and includes **citations** (file name and page number), so you can verify it.

Built with free tools only: Streamlit, ChromaDB, sentence-transformers and the Groq API.

---

## What it does

- Upload a PDF in the browser
- Ask questions about it in a chat box
- Get an answer written only from the document, with citations like `(sample.pdf, page 16)`
- See which pages were used as sources under every answer
- If the answer is not in the document, the app says so instead of guessing

## How it works

```
PDF -> extract text per page -> split into overlapping chunks
    -> embed each chunk (sentence-transformers) -> store in ChromaDB

Question -> embed -> retrieve top 4 similar chunks
         -> send chunks + question to the LLM (Groq)
         -> answer with citations + list of source pages
```

1. **Ingestion (`ingest.py`)**: `pypdf` reads each page. Text is split into chunks of 800 characters with 150 characters of overlap, so sentences cut at a boundary are not lost. Each chunk keeps its file name and page number.
2. **Storage (`store.py`)**: each chunk is turned into an embedding (a list of numbers that represents its meaning) with `all-MiniLM-L6-v2` and saved in a local ChromaDB database.
3. **Retrieval (`store.py`)**: the question is embedded the same way, and the most similar chunks are returned.
4. **Generation (`rag.py`)**: the retrieved chunks are placed in a prompt that tells the LLM to answer using only that context and to cite the source after each fact.
5. **UI (`app.py`)**: a Streamlit page with a file uploader, chat history and a sources line.

## Tech stack

| Part | Tool |
|---|---|
| UI | Streamlit |
| PDF parsing | pypdf |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, runs locally) |
| Vector database | ChromaDB (local, persistent) |
| LLM | Groq API (free tier) |
| Packaging | Docker |

## Project structure

```
askmydocs/
├── src/
│   ├── app.py        # Streamlit web interface
│   ├── ingest.py     # PDF loading and chunking
│   ├── store.py      # embeddings, ChromaDB storage and search
│   ├── rag.py        # prompt building and LLM call
│   └── test_llm.py   # quick check that your Groq key works
├── data/             # uploaded PDFs (not committed to git)
├── chroma_db/        # vector database (not committed to git)
├── Dockerfile
├── requirements.txt
├── .gitignore
├── .dockerignore
└── README.md
```

## Run it locally

You need Linux (or macOS/WSL), Python 3.10+ and a free Groq API key from [console.groq.com](https://console.groq.com).

```bash
git clone https://github.com/YOUR-USERNAME/askmydocs.git
cd askmydocs

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GROQ_API_KEY="your-key-here"
streamlit run src/app.py
```

Open http://localhost:8501, upload a PDF and start asking questions.

> Never put your API key in the code or commit it to GitHub. It is read from the `GROQ_API_KEY` environment variable.

## Run with Docker

```bash
docker build -t askmydocs .
docker run -d --name askmydocs -p 8501:8501 -e GROQ_API_KEY="$GROQ_API_KEY" askmydocs
```

Open http://localhost:8501. To stop it:

```bash
docker stop askmydocs && docker rm askmydocs
```

The Dockerfile installs the CPU-only version of PyTorch, which keeps the image much smaller and needs no GPU.

## Model note

The LLM is set in `src/rag.py` as `MODEL = "openai/gpt-oss-20b"`. Groq changes its available models over time. To see what your key can use:

```bash
python -c "
import os
from groq import Groq
c = Groq(api_key=os.environ['GROQ_API_KEY'])
for m in c.models.list().data:
    print(m.id)
"
```

Pick a chat model (not `whisper` or `guard` models) and update `MODEL`.

## Known limitations

- **Broad questions give partial answers.** The app retrieves only the 4 most similar chunks, so "summarize the whole PDF" covers just a few pages. Specific questions work best.
- **Scanned PDFs are not supported.** Pages that are images with no real text need OCR first.
- **All uploaded PDFs share one index.** Answers can mix sources if several PDFs are uploaded. Delete `chroma_db/` to reset.
- **No evaluation yet.** Answer quality has only been checked by hand.

## Roadmap

- [ ] Evaluation set of 20-30 questions with answer-quality scoring
- [ ] Re-ranking of retrieved chunks
- [ ] Hybrid search (keyword + semantic)
- [ ] "Search only this file" filter
- [ ] Whole-document summarization mode
- [ ] GitHub Actions CI to build the Docker image on every push
- [ ] Deployment on Hugging Face Spaces

## Privacy

Uploaded PDFs are stored only in the local `data/` folder and are excluded from git. Do not use documents with personal information in public demos or screenshots.

## What I learned

Chunking with overlap, embeddings and semantic search, grounding an LLM with retrieved context, citing sources, building a Streamlit UI, and packaging an ML app with Docker.
