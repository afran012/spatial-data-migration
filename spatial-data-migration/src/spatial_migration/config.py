# Configuraci�n y carga de variables de entornofrom dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

@dataclass
class PostgresConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class AWSConfig:
    access_key_id: str
    secret_access_key: str
    region: str
    bucket: str
    glue_database: str

@dataclass
class Config:
    postgres: PostgresConfig
    aws: AWSConfig

def load_config() -> Config:
    """Carga la configuración desde variables de entorno"""
    load_dotenv()
    
    return Config(
        postgres=PostgresConfig(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', ''),
            user=os.getenv('POSTGRES_USER', ''),
            password=os.getenv('POSTGRES_PASSWORD', '')
        ),
        aws=AWSConfig(
            access_key_id=os.getenv('AWS_ACCESS_KEY_ID', ''),
            secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', ''),
            region=os.getenv('AWS_REGION', ''),
            bucket=os.getenv('S3_BUCKET', ''),
            glue_database=os.getenv('GLUE_DATABASE', '')
        )
    )
