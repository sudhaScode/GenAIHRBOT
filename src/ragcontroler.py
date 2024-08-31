import scripts
import os
from vectorstore.chromadb import ChromaDB
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from src.utility import safety_settings, read_file, chuck
from vectorstore.chromadb_utills import create_query_engine
from multiprocessing import Lock




# Load environment
scripts.init()
index = None
lock = Lock()
query_engine = None

#LLM and Embedding model setup
gemini = Gemini(model_name="models/gemini-pro", temperature=0.5, max_tokens=2048, safety_settings=safety_settings)
gemini_embedding = GeminiEmbedding(model_name="models/embedding-001", api_key=os.getenv("GOOGLE_API_KEY"))

folder_path = f"./resources/documents/"
persist_dir = "./vectorstore/persist/"

document = read_file(folder_path)

#Vector store  Setup
ChromaDB = ChromaDB(gemini=gemini, gemini_embedding=gemini_embedding, vector_store="persist", persist_dir=persist_dir)

"""
#Index Setup
path = f"/vectorstore"
storage_context = ChromaDB.create_store(path)
## create index
index = ChromaDB.create_index(storage_context)

## update index
#file_path = f"/resources/uploads/{file_path}"
#ChromaDB.update_index(file_path, index)
"""
#lock = multiprocessing.Lock()
##create vector index
ChromaDB.create_vector_index(document= document)
#lock.acquire()
##get index
index = ChromaDB.get_index()
#lock.release()
#index= ChromaDB.get_index(storage_context)
#index = ChromaDB.initialize_index(persist_dir, document)
query_engine =  index.as_query_engine()


def update_context(file_path):
    ChromaDB.update_index(file_path=file_path)

def retrieval_query():
    return ChromaDB.create_retriever()

"""
if __name__ == "__main__":
    # init the global index
    print("initializing index...")
    initialize_index()

    # setup server
    # NOTE: you might want to handle the password in a less hardcoded way
    manager = BaseManager(("", 5602), b"password")
    manager.register("query_index", query_index)
    server = manager.get_server()

    print("starting server...")
    server.serve_forever()
"""