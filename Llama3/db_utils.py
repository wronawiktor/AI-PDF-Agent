from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from uuid import uuid4
from models import ChunkMeta
from config import settings

qdrant_client = QdrantClient(url=settings.QDRANT_HOST)

def save_embedding_qdrant(chunk: ChunkMeta):

    operation_info = qdrant_client.upsert(
        collection_name=settings.COLECTION_NAME,
        wait=True,
        points=[
            PointStruct(id=str(uuid4()), 
                        vector=chunk.vector,
                        payload={
                            "file_name": chunk.file_name,
                            "page": chunk.page,
                            "text_content": chunk.text_content.strip(),
                            "hash": chunk.hash
                        }),
        ],
    )
    return operation_info.status

def create_collection():
    qdrant_client.create_collection(
    collection_name=settings.COLECTION_NAME,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)