# src/spatial_migration/main.py
from typing import Optional, Dict, Any
from .core.extractor import PostgreSQLExtractor
from .core.transformer import SpatialTransformer
from .core.loader import AWSLoader
from .config import Config
from .logger import setup_logger

logger = setup_logger()

class SpatialDataMigration:
    def __init__(self, config: Config):
        self.config = config
        self.extractor = PostgreSQLExtractor(config.postgres)
        self.transformer = SpatialTransformer()
        self.loader = AWSLoader(config.aws)

    def run_migration(self, table_name: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """
        Ejecuta el proceso completo de migración.
        
        Args:
            table_name: Nombre de la tabla a migrar
            options: Opciones adicionales de migración
        
        Returns:
            bool: True si la migración fue exitosa
        """
        try:
            logger.info(f"Iniciando migración de tabla {table_name}")

            # Extracción
            gdf = self.extractor.extract_table(table_name)
            logger.info(f"Extraídos {len(gdf)} registros de {table_name}")

            # Transformación
            parquet_data = self.transformer.transform_to_parquet(gdf)
            logger.info("Datos transformados a formato Parquet")

            # Carga
            success = self.loader.load_to_aws(
                parquet_data,
                table_name,
                gdf.dtypes
            )

            if success:
                logger.info(f"Migración de {table_name} completada exitosamente")
            return success

        except Exception as e:
            logger.error(f"Error en la migración de {table_name}: {str(e)}")
            raise

# src/spatial_migration/config.py
from dataclasses import dataclass
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

# src/spatial_migration/logger.py
import logging
import sys
from datetime import datetime

def setup_logger() -> logging.Logger:
    """Configura y retorna el logger principal"""
    logger = logging.getLogger('spatial_migration')
    logger.setLevel(logging.INFO)

    # Crear formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo
    file_handler = logging.FileHandler(
        f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
