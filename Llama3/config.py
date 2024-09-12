# from pydantic import (
#     PostgresDsn,
#     computed_field,
# )
# from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    LLAMA_LLM_MODEL: str = "llama3.1:70b"
    LLAMA_EMBEDDING_MODEL: str = "mxbai-embed-large:latest"
    LLAMA_HOST: str = "192.168.0.96:11434"
    QDRANT_HOST: str = "localhost:6333/"
    COLECTION_NAME: str = "Llama_knowledge_BASE"

    # ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # POSTGRES_SERVER: str
    # POSTGRES_PORT: int = 5432
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str = ""
    # POSTGRES_DB: str = ""

    # @computed_field  # type: ignore[prop-decorator]
    # @property
    # def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
    #     return MultiHostUrl.build(
    #         scheme="postgresql+psycopg",
    #         username=self.POSTGRES_USER,
    #         password=self.POSTGRES_PASSWORD,
    #         host=self.POSTGRES_SERVER,
    #         port=self.POSTGRES_PORT,
    #         path=self.POSTGRES_DB,
    #     )

settings = Settings()
