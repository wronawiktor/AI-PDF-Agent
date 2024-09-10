from ollama import Client
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from uuid import uuid4
import logging
# import json
from pdfminer.high_level import extract_text
from textsplitter import TextSplitter

LLAMA_LLM_MODEL = "llama3.1:70b"
LLAMA_EMBEDDING_MODEL = "mxbai-embed-large:latest"
LLAMA_HOST = "192.168.0.96:11434"
QDRANT_HOST = "localhost:6333/"
COLECTION_NAME = "Llama_knowledge_BASE"

qdrant_client = QdrantClient(url=QDRANT_HOST)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# def extract_text_from_doc(path):
#     return extract_text(path)

from pathlib import Path
from pdfminer.pdfparser import PDFParser, PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines

def vectorize_pdf(file_name):
    with open(file_name, "rb") as fp:
        try:
            parser = PDFParser(fp)
            document = PDFDocument(parser)
            outlines = document.get_outlines()
            for (level, title, dest, a, se) in outlines:
                # https://pdfminersix.readthedocs.io/en/latest/howto/toc_target_page.html
                splitter = TextSplitter(max_token_size=500, end_sentence=True, preserve_formatting=True, 
                                        remove_urls=True, replace_entities=True, remove_stopwords=True, language='english')
                text_chunks = splitter.split(text)
                for i, chunk in enumerate(text_chunks):
                    print(f"Chunk {i}: {chunk}")
                    # embeded = llama_embedding(chunk)
                    # save_embedding_qdrant(embeded, chunk)

                ...  # do something
        except PDFNoOutlines:
            print("No outlines found.")
        except PDFSyntaxError:
            print("Corrupted PDF or non-PDF file.")
        finally:
            parser.close()

def llama_query(prompt: str):
    try:
        client = Client(host=LLAMA_HOST)
        messages = [
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        # Send the query and get the response
        response = client.chat(model=LLAMA_LLM_MODEL, messages=messages)
        
        # Extract and return the generated text
        return response['message']['content']
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def llama_embedding(prompt: str):
    client = Client(host=LLAMA_HOST)
    response = client.embeddings(model=LLAMA_EMBEDDING_MODEL, prompt=prompt)
    embedding = response["embedding"]
    return embedding

def create_collection():
    qdrant_client.create_collection(
    collection_name=COLECTION_NAME,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)

def save_embedding_qdrant(embedding, text):

    operation_info = qdrant_client.upsert(
        collection_name=COLECTION_NAME,
        wait=True,
        points=[
            PointStruct(id=str(uuid4()), 
                        vector=embedding,
                        payload={"Text": text}),
        ],
    )
    return operation_info.status

def search_text(prompt):
    embedding = llama_embedding(prompt)
    search_result = qdrant_client.search(
        collection_name=COLECTION_NAME, query_vector=embedding, 
        limit=3,
        # score_threshold=0.5
    )
    return search_result

def main():
    # save_all_texts()
    # prompr = input("Enter a prompt: ")
    # search_result = search_text(prompr)
    # print(search_result)
    # vectorize_pdf(extract_text_from_doc("test.pdf"))
    pass

if __name__ == "__main__":
    main()
