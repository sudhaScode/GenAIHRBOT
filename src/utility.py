from llama_index.core.node_parser import SentenceSplitter
import os
import re
import pdfplumber
from IPython.display import Markdown,display
import textwrap
from llama_index.core import  SimpleDirectoryReader, VectorStoreIndex,StorageContext, load_index_from_storage
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Settings
import chromadb
import tempfile



## doc Reader

def read_file(folder_path):
  try:
    document = SimpleDirectoryReader(folder_path).load_data()
    return document
  except Exception as e:
    print(f"Error reading folder: {type(e)} - {e}")
    return

#text splitter
custom_separator = '\n'
custom_chunk_size = 1000
custom_chunk_overlap = 50
custom_paragraph_separator = '\n\n\n'
custom_regex = '[^,.;。？！]+[,.;。？！]?'
custom_sentence_splitter = SentenceSplitter(
    separator=custom_separator,
    chunk_size=custom_chunk_size,
    chunk_overlap=custom_chunk_overlap,
    paragraph_separator=custom_paragraph_separator,    
)
#Safety settings
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
]

def create_store(gemini, gemini_embedding, documents, PERSIST_DIR):
  Settings.llm = gemini
  Settings.embed_model = gemini_embedding
  if not os.path.exists(PERSIST_DIR) or PERSIST_DIR is None:
        # Use a temporary directory if not specified
        os.mkdir(PERSIST_DIR)
  try:
    # build index
    persist_client = chromadb.PersistentClient(path=PERSIST_DIR)
    persist_collection = persist_client.get_or_create_collection("persist")

    persist_store = ChromaVectorStore(chroma_collection=persist_collection)
    persist_context = StorageContext.from_defaults(vector_store=persist_store)
    return persist_context
  except Exception as e:
    print(e)
    return None


def create_index(persist_context, index_type="default",load_existing=False, **kwargs,  ):
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


def get_index(persist_context, index_type="default", **kwargs):

  # get index
  try:
    index = load_index_from_storage(storage_context=persist_context, index_type=index_type, **kwargs)
    print(index)
    return index
  except Exception as e:
    print(f"Error getting index: {type(e)} - {e}")
    return None




from llama_index.core import  Document
def update_index(file_path, index):
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        return

    try:
        # Assuming 'chuck' function splits the file into manageable chunks
        text_chunks = chuck(file_path)
        doc_chunks = []
        for i, text in enumerate(text_chunks):
            doc = Document(text=text, id_=f"doc_id_{i}")
            doc_chunks.append(doc)

        # Insert documents in batches for efficiency (optional)
        index.insert_documents(doc_chunks)

        print(f"Successfully updated index with {len(doc_chunks)} documents.")

    except Exception as e:
        print(f"Error updating index: {type(e)} - {e}")


def chuck(file_path):
  document = pdf_folder_reader(file_path)

  cleaned_text = preprocess_text(document)

  cleaned_text = remove_special_characters(cleaned_text)
  custom_chunks = custom_sentence_splitter.split_text(cleaned_text)

  return custom_chunks


def pdf_folder_reader(file_path):

    pdf_text =""

    file_name = os.path.basename(file_path)
    if file_name.endswith(".pdf"):
        #read the pdf
        with pdfplumber.open(file_path) as file:
            for page in file.pages:
                pdf_text += page.extract_text()
    else:
        #read the pdf
        with open(file_path) as file:
            for page in file.pages:
                pdf_text += page.extract_text()
            
    return pdf_text

def preprocess_text(raw_text):
    # Remove dots
    text_without_dots = raw_text.replace('.', '.')
    
    # Normalize whitespace
    text_normalized = ' '.join(text_without_dots.split())

    return text_normalized


def remove_special_characters(text):
    # Define a regular expression to match any non-alphanumeric character
    pattern = re.compile(r'[^a-zA-Z0-9\s]')
    
    # Use the sub method to replace matched characters with an empty string
    cleaned_text = re.sub(pattern, '', text)
    
    return cleaned_text



def to_markdown(text):
  if isinstance(text, str):
    text = text.replace(".", "*")
    return Markdown(textwrap.indent(text,'> ', predicate=lambda _:True))
  else:
    text = str(text)
    text = text.replace(".", "*")
    return Markdown(textwrap.indent(text,'> ', predicate=lambda _:True))

