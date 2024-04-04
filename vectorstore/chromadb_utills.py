
from llama_index.core import SimpleDirectoryReader
from src.utility import chuck
from llama_index.core import  Document
import os





def create_query_engine(index):
    try:
        query_engine =  index.as_query_engine()
        return query_engine
    except Exception as e:
        print(e)

def update_index( file_path, index):
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
          index.insert_documents(doc_chunks)

          print(f"Successfully updated index with {len(doc_chunks)} documents.")
          """
        document = SimpleDirectoryReader(input_files=[file_path]).load_data()[0]
        print(document.text[0:1000])
        doc_id = None
        if doc_id is not None:
            document.doc_id = doc_id
        index.insert(document)
        index.storage_context.persist()
      except Exception as e:
          print(f"Error updating index: {type(e)} - {e}")