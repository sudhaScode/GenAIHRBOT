from llama_index.core.schema import Document
from src.utility import chuck
import os
import re
import textwrap
from llama_index.core import  VectorStoreIndex,StorageContext, load_index_from_storage, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Settings
import chromadb
from src.utility import custom_sentence_splitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import  get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor


class ChromaDB:

  
  def __init__(self, gemini,gemini_embedding, vector_store, persist_dir):
    self.gemini = gemini
    self.gemini_embedding = gemini_embedding
    self.vector_store = vector_store
    self.persist_dir = persist_dir
    self.persist_context =None
    self.index = None
 


  def create_store(self):
    Settings.llm = self.gemini
    Settings.embed_model = self.gemini_embedding
    PERSIST_DIR = PERSIST_DIR + self.vector_store
    if not os.path.exists(PERSIST_DIR) or PERSIST_DIR is None:
          # Use a temporary directory if not specified
          os.mkdir(PERSIST_DIR)
    try:
      # build index
      persist_client = chromadb.PersistentClient(path=PERSIST_DIR)
      persist_collection = persist_client.get_or_create_collection(self.vector_store)

      persist_store = ChromaVectorStore(chroma_collection=persist_collection)
      persist_context = StorageContext.from_defaults(vector_store=persist_store)
      return persist_context
    except Exception as e:
      print(e)
      return None



  def create_index(self, persist_context, index_type="default",load_existing=False, **kwargs,  ):
    try:
      if load_existing:
              index = load_index_from_storage(storage_context=persist_context, index_type=index_type, **kwargs)
              if index:
                  return index
              else:
                  print("Existing index not found. Creating a new one.")
      index = VectorStoreIndex.from_documents(storage_context=persist_context, index_type=index_type, **kwargs)
      #index = load_index_from_storage(storage_context=persist_context,index_type=index_type, **kwargs) 
      return index
    except Exception as e:
      print(f"Error creating index: {type(e)} - {e}")
      return None

  def create_vector_index(self, document):
    Settings.llm = self.gemini
    Settings.embed_model = self.gemini_embedding
    try:
      persist_client = chromadb.PersistentClient(path=self.persist_dir)
      persist_collection = persist_client.get_or_create_collection(self.vector_store)

      persist_store = ChromaVectorStore(chroma_collection=persist_collection)
      persist_context = StorageContext.from_defaults(vector_store=persist_store)

      # load the data and create index
      index = VectorStoreIndex.from_documents(documents=document, storage_context=persist_context, embed_model=self.gemini_embedding, transformations=[custom_sentence_splitter])
      index.storage_context.persist(persist_dir= self.persist_dir)
      self.index = index
      self.persist_context =persist_context
      return True
    except Exception as e:
      print(e)
      return None

  def get_index(self, index_type="default", **kwargs):
    #persist_context
    # get index
    """
    if persist_context is None:
      raise Exception("vectore store is empty")
    """
    try:
      ind = load_index_from_storage(storage_context=self.persist_context, index_type=index_type, **kwargs)
      print(ind)
      return ind
    except Exception as e:
      print(f"Error getting index: {type(e)} - {e}")
      return None
  def update_index(self, file_path):
      print(f"Updating index with file: {self.index}")
      if not os.path.isfile(file_path):
          print(f"Error: File not found: {file_path}")
          return

      try:
          """
          # Assuming 'chuck' function splits the file into manageable chunks
          text_chunks = chuck(file_path)
          doc_chunks = []
          for i, text in enumerate(text_chunks):
              doc = Document(text=text, id_=f"doc_id_{i}")
              doc_chunks.append(doc)

          # Insert documents in batches for efficiency (optional)
          self.index.insert_documents(doc_chunks)

          print(f"Successfully updated index with {len(doc_chunks)} documents.")
          """
          document = SimpleDirectoryReader(input_files=[file_path]).load_data()[0]
          print(document)
          doc_id = None
          if doc_id is not None:
              document.doc_id = doc_id
          self.index.insert(document)
          self.index.storage_context.persist(persist_dir=self.persist_dir)
      except Exception as e:
        raise Exception(status_code=555, detail=str(e))
  def create_retriever(self):
    try:
        retriever = VectorIndexRetriever(
        index=self.index,
        similarity_top_k=8)
        # configure response synthesizer
        response_synthesizer = get_response_synthesizer()

        # assemble query engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.8)],
        )
        return query_engine
    except Exception as e:
        print(e)


"""
  def initialize_index(self, index_dir, documents):
    Settings.llm = self.gemini
    Settings.embed_model = self.gemini_embedding
  
    try:
      persist_client = chromadb.PersistentClient(path=index_dir)
      persist_collection = persist_client.get_or_create_collection(self.vector_store)

      persist_store = ChromaVectorStore(chroma_collection=persist_collection)
      persist_context = StorageContext.from_defaults(vector_store=persist_store)
      if os.path.exists(index_dir):
          index = load_index_from_storage(persist_context)
          return index
      else:
          #index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
          #storage_context.persist(index_dir)
          index = VectorStoreIndex.from_documents(documents=documents, storage_context=persist_context, embed_model=self.gemini_embedding, transformations=[custom_sentence_splitter])
          index.storage_context.persist(persist_dir=index_dir)
          print(f"creating new document index in {index_dir}")
          return index
    except Exception as e:
      print("index initilization failed")
      return None
"""