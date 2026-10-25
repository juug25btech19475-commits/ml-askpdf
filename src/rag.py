import os
from groq import Groq
from store import search

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"

def answer(question, k=4):
    chunks = search(question, k=k)
    context = "\n\n".join(
        f"[{c['source']} - page {c['page']}]\n{c['text']}" for c in chunks
    )
    prompt = (
        "Answer the question using ONLY the context below. "
        "After each fact, cite its source like (file, page N). "
        "If the answer is not in the context, say \"I could not find this in the document.\"\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION: {question}"
    )
    reply = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return reply.choices[0].message.content, chunks

if __name__ == "__main__":
    q = input("Ask a question: ")
    text, chunks = answer(q)
    print("\nANSWER:\n", text)
    print("\nSOURCES USED:")
    for c in chunks:
        print(f"- {c['source']}, page {c['page']}")
