# Transformaci�n de datos espaciales

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