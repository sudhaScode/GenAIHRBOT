import os
import scripts
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,load_index_from_storage
)

from multiprocessing import Lock
from multiprocessing.managers import BaseManager

# NOTE: for local testing only, do NOT deploy with your key hardcoded

scripts.init()
index = None
index_dir = f"/store"
lock = Lock()

def initialize_index():
    global index
    with lock:
        storage_context = StorageContext.from_defaults()
        if os.path.exists(index_dir):
            index = load_index_from_storage(storage_context)
        else:
            documents = SimpleDirectoryReader("./resources/documents").load_data()
            index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context
            )
            storage_context.persist(index_dir)
        pass

def query_index(query_text):
    global index
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    return response

def insert_into_index(doc_text, doc_id=None):
    global index
    document = SimpleDirectoryReader(input_files=[doc_text]).load_data()[0]
    if doc_id is not None:
        document.doc_id = doc_id

    with lock:
        index.insert(document)
        index.storage_context.persist()

if __name__ == "__main__":
    # init the global index
    print("initializing index...")
    initialize_index()

    # setup server
    # NOTE: you might want to handle the password in a less hardcoded way
    manager = BaseManager(("", 5602), b"password")
    manager.register("query_index", query_index)
    manager.register("insert_into_index", insert_into_index)
    server = manager.get_server()

    print("starting server...")
    server.serve_forever()


