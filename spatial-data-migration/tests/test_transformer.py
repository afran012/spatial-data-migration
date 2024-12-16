# tests/test_transformer.py
import pytest
from spatial_migration.core.transformer import SpatialTransformer

def test_transform_to_parquet(sample_geodataframe):
    """Prueba la transformación a formato Parquet"""
    transformer = SpatialTransformer()
    result = transformer.transform_to_parquet(sample_geodataframe)
    
    assert result is not None
    assert hasattr(result, 'read')  # Verifica que es un objeto tipo file-like

def test_transform_empty_dataframe():
    """Prueba la transformación de un DataFrame vacío"""
    transformer = SpatialTransformer()
    empty_gdf = gpd.GeoDataFrame()
    
    with pytest.raises(ValueError):
        transformer.transform_to_parquet(empty_gdf)
