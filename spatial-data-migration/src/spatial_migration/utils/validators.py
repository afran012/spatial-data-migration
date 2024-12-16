# Validaciones

from typing import Any, Dict, Optional
import geopandas as gpd
from ..logger import setup_logger

logger = setup_logger()

class DataValidator:
    @staticmethod
    def validate_spatial_data(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Valida un GeoDataFrame con datos espaciales
        
        Args:
            gdf: GeoDataFrame a validar
        
        Returns:
            Dict con resultados de validación
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar geometrías nulas
        null_geoms = gdf.geometry.isna().sum()
        if null_geoms > 0:
            results['warnings'].append(f"Encontradas {null_geoms} geometrías nulas")
        
        # Verificar geometrías inválidas
        invalid_geoms = (~gdf.geometry.is_valid).sum()
        if invalid_geoms > 0:
            results['errors'].append(f"Encontradas {invalid_geoms} geometrías inválidas")
            results['is_valid'] = False
        