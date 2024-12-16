from typing import Optional
import geopandas as gpd
from sqlalchemy import create_engine, text
import warnings
from ..exceptions import ExtractionError
from ..logger import setup_logger

logger = setup_logger()

class PostgreSQLExtractor:
    def __init__(self, config: dict):
        self.config = config
        self._engine = None
        
    def extract_spatial_data(self, table_name: str) -> gpd.GeoDataFrame:
        """
        Extrae datos espaciales asegurando el manejo correcto de MultiPolygons y SRID 4326.
        
        Args:
            table_name: Nombre de la tabla a extraer
            
        Returns:
            GeoDataFrame con los datos espaciales
        """
        try:
            query = f"""
            SELECT 
                id,
                ST_AsText(geom) as geometry,
                objectid_1,
                objectid,
                nro_cuadra,
                latitud,
                longitud,
                codigo_sie,
                tel,
                cuadrante,
                estacion,
                distrito,
                shape_leng,
                shape_area
            FROM {table_name}
            """
            
            # Extraer datos asegurando el SRID correcto
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                gdf = gpd.read_postgis(
                    query,
                    self.engine,
                    geom_col='geometry',
                    crs='EPSG:4326'
                )
            
            # Validar que los datos se extrajeron correctamente
            self._validate_extraction(gdf)
            
            logger.info(f"Extraídos {len(gdf)} registros con éxito")
            return gdf
            
        except Exception as e:
            logger.error(f"Error en la extracción: {str(e)}")
            raise ExtractionError(f"Error extrayendo datos: {str(e)}")
    
    def _validate_extraction(self, gdf: gpd.GeoDataFrame) -> None:
        """Valida los datos extraídos."""
        if gdf.empty:
            raise ExtractionError("No se encontraron datos")
            
        # Verificar que todas las geometrías son válidas
        invalid_geoms = (~gdf.geometry.is_valid).sum()
        if invalid_geoms > 0:
            logger.warning(f"Se encontraron {invalid_geoms} geometrías inválidas")
            
        # Verificar el SRID
        if gdf.crs is None or gdf.crs.to_string() != 'EPSG:4326':
            raise ExtractionError("SRID incorrecto en los datos extraídos")