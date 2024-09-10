from ollama import Client
from config import settings

client = Client(host=settings.LLAMA_HOST)

def llama_embedding(prompt: str):
    response = client.embeddings(model=settings.LLAMA_EMBEDDING_MODEL, prompt=prompt)
    embedding = response["embedding"]
    return embedding


def llama_query(prompt: str):
    try:
        messages = [
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        # Send the query and get the response
        response = client.chat(model=settings.LLAMA_LLM_MODEL, 
                                messages=messages)
        
        # Extract and return the generated text
        return response['message']['content']
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def llama_one_response(prompt: str):
    try:
        # Send the query and get the response
        response = client.generate(model=settings.LLAMA_LLM_MODEL, 
                                   prompt=prompt)
        
        # Extract and return the generated text
        return response['response']
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
    
