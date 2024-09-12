from pydantic import BaseModel, computed_field
from llama_utils import llama_embedding

class ChunkMeta(BaseModel):
    file_name: str
    page: int
    text_content: str
    hash: str
    #vector: str
    
    @computed_field
    @property
    def vector(self) -> str:
        return llama_embedding(self.text_content)