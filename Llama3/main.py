import logging
from pathlib import Path
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import TokenTextSplitter
from qdrant_client.models import ScoredPoint
from typing import List, Optional

from llama_utils import llama_embedding, llama_one_response
from db_utils import qdrant_client, save_embedding_qdrant
from config import settings
from models import ChunkMeta


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def vectorize_resources(resources_dir: str = "resources"):
    reader = SimpleDirectoryReader(input_dir=resources_dir,recursive=True)
    documents = reader.load_data()

    splitter = TokenTextSplitter(
        chunk_size=512,
        chunk_overlap=128,
        separator=" ",
    )

    token_nodes = splitter.get_nodes_from_documents(
        documents, show_progress=[True if logger.level == "debug".lower() else False]
    )

    for i, chunk in enumerate(token_nodes):
        if chunk.metadata["file_size"] != 0:
            logger.debug(f"Chunk {i+1}: \n")
            meta = ChunkMeta(file_name=chunk.metadata['file_name'], 
                             page=chunk.metadata['page_label'],
                             text_content=chunk.text,
                             hash=chunk.hash)
            save_embedding_qdrant(meta)
            logger.debug(f"Saved chunk {i+1} to Qdrant")


def search_text(prompt) -> Optional[List[ChunkMeta]]:
    embedding = llama_embedding(prompt)
    search_result = qdrant_client.search(
        collection_name=settings.COLECTION_NAME, query_vector=embedding, 
        limit=3,
        score_threshold=0.5
    )
    if search_result:
        for i, point in enumerate(search_result):
            search_result[i] = ChunkMeta(file_name=point.payload["file_name"], 
                                         page=point.payload["page"],
                                         text_content=point.payload["text_content"],
                                         hash=point.payload["hash"])
        return search_result
    else:
        logger.info("No search results found")
        return None


def generate_response_with_rag() -> str:
    query = input("Enter a search query: ")
    search_results = search_text(query)
    retrieved_document = [chunk.text_content for chunk in search_results]

    if retrieved_document:
        logger.debug("Search results: \n" + "\n".join(retrieved_document))
        prompt = f"Using this information: {retrieved_document}, respond to the query: {query}"
        RAG_info = [f"File: {chunk.file_name} - page {chunk.page}" for chunk in search_results]    
    
    response = llama_one_response(prompt)
    print(f"Generated Response: \n{response}")
    if RAG_info:
        print("You can find this informations here:")
        print(*[source for source in set(RAG_info)], sep="\n")


def main():

    # To vectorize the resources in the resources directory:

    # RES_DIR = Path(__file__).resolve().parent / "resources"
    # print(f"PDF resource directory: {RES_DIR}")
    # vectorize_resources(RES_DIR)

    # To ask a question and get a response using RAG:
    generate_response_with_rag()


if __name__ == "__main__":
    main()
