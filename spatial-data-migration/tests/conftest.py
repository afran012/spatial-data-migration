# Configuraci�n de pruebas

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