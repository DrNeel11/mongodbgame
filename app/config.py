from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "multiplayer_gaming"
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # Allow extra environment variables (so frontend .env entries don't break startup)
    model_config = {"env_file": ".env", "extra": "allow"}


@lru_cache()
def get_settings():
    return Settings()
