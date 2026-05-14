import sys
sys.path.append(".")
import chromadb

client = chromadb.PersistentClient(path="data/vector_db")
client.delete_collection("msra_chunks")
print("Collection deleted.")
