# tests/conftest.py
import pytest
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from spatial_migration.config import Config, PostgresConfig, AWSConfig

@pytest.fixture
def sample_config():
    """Fixture que proporciona una configuración de prueba"""
    return Config(
        postgres=PostgresConfig(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass"
        ),
        aws=AWSConfig(
            access_key_id="test_key",
            secret_access_key="test_secret",
            region="us-east-1",
            bucket="test-bucket",
            glue_database="test_database"
        )
    )

@pytest.fixture
def sample_geodataframe():
    """Fixture que proporciona un GeoDataFrame de prueba"""
    data = {
        'id': [1, 2, 3],
        'name': ['Point A', 'Point B', 'Point C'],
        'geometry': [
            Point(0, 0),
            Point(1, 1),
            Point(2, 2)
        ]
    }
    return gpd.GeoDataFrame(data, geometry='geometry')

# tests/test_extractor.py
import pytest
from unittest.mock import Mock, patch
from spatial_migration.core.extractor import PostgreSQLExtractor

def test_extract_table(sample_config, sample_geodataframe):
    """Prueba la extracción de datos desde PostgreSQL"""
    with patch('geopandas.read_postgis') as mock_read_postgis:
        mock_read_postgis.return_value = sample_geodataframe
        
        extractor = PostgreSQLExtractor(sample_config.postgres)
        result = extractor.extract_table('test_table')
        
        assert len(result) == len(sample_geodataframe)
        assert all(result.columns == sample_geodataframe.columns)

def test_extract_table_with_where_clause(sample_config):
    """Prueba la extracción con cláusula WHERE"""
    with patch('geopandas.read_postgis') as mock_read_postgis:
        extractor = PostgreSQLExtractor(sample_config.postgres)
        extractor.extract_table('test_table', where_clause="id = 1")
        
        # Verificar que la consulta incluye la cláusula WHERE
        call_args = mock_read_postgis.call_args[0]
        assert "WHERE id = 1" in call_args[0]

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

# tests/test_loader.py
import pytest
from unittest.mock import Mock, patch
from spatial_migration.core.loader import AWSLoader

def test_load_to_aws(sample_config):
    """Prueba la carga de datos a AWS"""
    with patch('boto3.client') as mock_boto3:
        mock_s3 = Mock()
        mock_glue = Mock()
        mock_boto3.side_effect = [mock_s3, mock_glue]
        
        loader = AWSLoader(sample_config.aws)
        result = loader.load_to_aws(
            Mock(),  # mock parquet_data
            'test_table',
            {'id': 'int64', 'name': 'object', 'geometry': 'object'}
        )
        
        assert result is True
        mock_s3.upload_fileobj.assert_called_once()
        mock_glue.create_table.assert_called_once()

def test_load_to_aws_s3_error(sample_config):
    """Prueba el manejo de errores de S3"""
    with patch('boto3.client') as mock_boto3:
        mock_s3 = Mock()
        mock_s3.upload_fileobj.side_effect = Exception("S3 Error")
        mock_boto3.return_value = mock_s3
        
        loader = AWSLoader(sample_config.aws)
        
        with pytest.raises(Exception) as exc_info:
            loader.load_to_aws(Mock(), 'test_table', {})
        
        assert "S3 Error" in str(exc_info.value)
