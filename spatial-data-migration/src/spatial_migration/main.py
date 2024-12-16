# Punto de entrada principal

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
