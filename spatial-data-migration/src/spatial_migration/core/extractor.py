# Extracci�n de datos de PostgreSQL

# src/spatial_migration/core/extractor.py
from typing import Optional
import geopandas as gpd
from sqlalchemy import create_engine
from ..config import PostgresConfig
from ..logger import setup_logger

logger = setup_logger()

class PostgreSQLExtractor:
    def __init__(self, config: PostgresConfig):
        self.config = config
        self._engine = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(self.config.connection_string)
        return self._engine

    def extract_table(self, table_name: str, where_clause: Optional[str] = None) -> gpd.GeoDataFrame:
        """
        Extrae datos espaciales de PostgreSQL
        
        Args:
            table_name: Nombre de la tabla
            where_clause: Cláusula WHERE opcional
        
        Returns:
            GeoDataFrame con los datos extraídos
        """
        try:
            query = f"""
            SELECT *,
                   ST_AsText(geometry) as geometry_wkt,
                   ST_SRID(geometry) as srid
            FROM {table_name}
            """
            
            if where_clause:
                query += f" WHERE {where_clause}"

            gdf = gpd.read_postgis(
                query,
                self.engine,
                geom_col='geometry'
            )

            logger.info(f"Extraídos {len(gdf)} registros de {table_name}")
            return gdf

        except Exception as e:
            logger.error(f"Error extrayendo datos de {table_name}: {str(e)}")
            raise

# src/spatial_migration/core/transformer.py
from typing import Union, BinaryIO
import geopandas as gpd
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from ..logger import setup_logger

logger = setup_logger()

class SpatialTransformer:
    def transform_to_parquet(self, gdf: gpd.GeoDataFrame) -> Union[bytes, BinaryIO]:
        """
        Transforma GeoDataFrame a formato Parquet
        
        Args:
            gdf: GeoDataFrame a transformar
        
        Returns:
            Datos en formato Parquet
        """
        try:
            # Convertir geometrías a WKT
            df = pd.DataFrame(gdf)
            if 'geometry' in df.columns:
                df['geometry'] = df['geometry'].apply(lambda x: x.wkt)

            # Convertir a Parquet
            table = pa.Table.from_pandas(df)
            
            buffer = BytesIO()
            pq.write_table(table, buffer)
            buffer.seek(0)
            
            logger.info(f"Datos transformados a Parquet: {len(df)} registros")
            return buffer

        except Exception as e:
            logger.error(f"Error en transformación a Parquet: {str(e)}")
            raise

# src/spatial_migration/core/loader.py
from typing import Union, BinaryIO, Dict, Any
import boto3
from botocore.exceptions import ClientError
from ..config import AWSConfig
from ..logger import setup_logger

logger = setup_logger()

class AWSLoader:
    def __init__(self, config: AWSConfig):
        self.config = config
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            region_name=config.region
        )
        self.glue_client = boto3.client(
            'glue',
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            region_name=config.region
        )

    def load_to_aws(
        self,
        parquet_data: Union[bytes, BinaryIO],
        table_name: str,
        dtypes: Dict[str, Any]
    ) -> bool:
        """
        Carga datos a AWS (S3 + Glue)
        
        Args:
            parquet_data: Datos en formato Parquet
            table_name: Nombre de la tabla
            dtypes: Tipos de datos de las columnas
        
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            # Subir a S3
            s3_key = f"spatial_data/{table_name}/{table_name}.parquet"
            self.s3_client.upload_fileobj(
                parquet_data,
                self.config.bucket,
                s3_key
            )
            logger.info(f"Datos cargados a S3: s3://{self.config.bucket}/{s3_key}")

            # Crear tabla en Glue
            self._create_glue_table(table_name, dtypes, s3_key)
            
            return True

        except Exception as e:
            logger.error(f"Error en carga a AWS: {str(e)}")
            raise

    def _create_glue_table(self, table_name: str, dtypes: Dict[str, Any], s3_key: str):
        """Crea tabla en el catálogo de Glue"""
        try:
            columns = self._get_glue_columns(dtypes)
            
            self.glue_client.create_table(
                DatabaseName=self.config.glue_database,
                TableInput={
                    'Name': table_name,
                    'StorageDescriptor': {
                        'Columns': columns,
                        'Location': f"s3://{self.config.bucket}/{s3_key}",
                        'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
                        'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
                        'SerdeInfo': {
                            'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
                        }
                    },
                    'TableType': 'EXTERNAL_TABLE'
                }
            )
            logger.info(f"Tabla {table_name} creada en Glue")

        except ClientError as e:
            if e.response['Error']['Code'] == 'AlreadyExistsException':
                logger.warning(f"La tabla {table_name} ya existe en Glue, actualizando...")
                # Aquí podrías implementar la lógica para actualizar la tabla
            else:
                raise

    def _get_glue_columns(self, dtypes: Dict[str, Any]) -> list:
        """Convierte tipos de pandas a tipos de Glue"""
        type_mapping = {
            'int64': 'bigint',
            'float64': 'double',
            'object': 'string',
            'bool': 'boolean',
            'datetime64[ns]': 'timestamp'
        }
        
        columns = []
        for column, dtype in dtypes.items():
            columns.append({
                'Name': column,
                'Type': type_mapping.get(str(dtype), 'string')
            })
        
        return columns