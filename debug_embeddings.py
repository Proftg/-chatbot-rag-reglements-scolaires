from langchain_community.embeddings import SentenceTransformerEmbeddings
import time

print("Init model...")
start = time.time()
ef = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
print(f"Model init done in {time.time() - start:.2f}s")

print("Embed query...")
res = ef.embed_query("Test")
print(f"Embed done. Vector length: {len(res)}")
