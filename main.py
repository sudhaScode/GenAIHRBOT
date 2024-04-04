import json
#import the finetuned modal 
from vectorstore.chromadb_utills import update_index, create_query_engine
from src.ragcontroler import index, query_engine 
import time

#import the fastapi
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import  JSONResponse,ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.utility import to_markdown
from pydantic import BaseModel
from typing import Union

#query_engine = create_query_engine(index)
print(index)

# create an instance of FastAPI
app = FastAPI()
# Allow only the specified origin (replace with your frontend's actual origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Query(BaseModel):
    prompt: str#what to keep here 
# implement the HTTP request using the decorators 
@app.get("/")
async def root():
    return {"LLM": "Chat with customized llm"}


# Create an instance without providing a default value
#item_instance = Item(query="Please conclude the IPO details of the company?")

@app.post("/query")
async def context_chat(query: Query) :#-> ORJSONResponse
    #send the query to llm
    #message = payload.get("message")
    prompt = query.prompt
    response_dict = query_engine.query(prompt)
    response_text = response_dict['response'].response
    return JSONResponse({"prompt_response": response_text})


@app.post("/upload")
async def upload_context(file: UploadFile = File(...)):
    
    try:  
        print("Invoked")
        file_path =f"C:/Users/SUBOMMAS/LLM_Projects/HRBOT/resources/uploads/{file.filename}"
        print(file_path)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Call the method to update the vector store index
        update_index(file_path=file_path, index=index)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Upload successful"}



"""   
@app.post("/query")
async def context_chat(item: Item):
    #send the query to llm
    #message = payload.get("message")
    message = item.query
    response = query_engine.query(message)
    
    response = {"bot_reply": response}
    return response

"""


#uvicorn main:app --reload
