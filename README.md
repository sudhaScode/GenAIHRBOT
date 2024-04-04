# Advanced RAG Solution implementation
- Objectives of the advanced RAG solution
- -  Improving the upload docuements and summarizing
- -  Improving the vector store data management 
- -  Improving the summarization and query prompts

## Summarization 
## Aproach 1 to summarize -Refine method
- - read the uploaded docuemnts and store them in a variables with pages
- - recursively iterate though the multiple pages and send the context to llm 
- -  get summaries for each iteration
- - group the summaries and send to the user


# try to modify the venv\Lib\site-packages\llama_index\core\base\base_query_engine.py , the output must be in JSON format
- return {"response":query_result}