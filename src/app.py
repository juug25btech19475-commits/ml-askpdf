import os
import streamlit as st
from store import add_pdf
from rag import answer

st.set_page_config(page_title="AskMyDocs", page_icon="📄")
st.title("📄 AskMyDocs")
st.caption("Upload a PDF and ask questions. Answers include citations.")

os.makedirs("data", exist_ok=True)

uploaded = st.file_uploader("Upload a PDF", type="pdf")
if uploaded and st.session_state.get("last_file") != uploaded.name:
    path = os.path.join("data", uploaded.name)
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    with st.spinner("Reading and indexing your PDF..."):
        n = add_pdf(path, uploaded.name)
    st.session_state["last_file"] = uploaded.name
    st.success(f"Indexed {n} chunks from {uploaded.name}")

if "history" not in st.session_state:
    st.session_state["history"] = []

for role, text in st.session_state["history"]:
    with st.chat_message(role):
        st.write(text)

question = st.chat_input("Ask a question about your document")
if question:
    st.session_state["history"].append(("user", question))
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            text, chunks = answer(question)
        st.write(text)
        pages = sorted({(c["source"], c["page"]) for c in chunks})
        st.caption("Sources: " + ", ".join(f"{s} p.{p}" for s, p in pages))
    st.session_state["history"].append(("assistant", text))
