# Definici�n de modelos de datos# src/spatial_migration/models/schemas.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class PostgresTableSchema:
    """Schema para una tabla de PostgreSQL."""
    table_name: str
    columns: Dict[str, str]
    geometry_column: str
    srid: int
    indexes: Optional[List[str]] = None

@dataclass
class GlueTableSchema:
    """Schema para una tabla de AWS Glue."""
    table_name: str
    columns: Dict[str, str]
    location: str
    format: str = 'parquet'
    partition_keys: Optional[List[str]] = None

@dataclass
class MigrationConfig:
    """Configuración para una migración."""
    source_table: PostgresTableSchema
    target_table: GlueTableSchema
    batch_size: int = 1000
    validate_data: bool = True
    create_backup: bool = False

@dataclass
class ValidationResults:
    """Resultados de validación de datos."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validation_date: datetime = datetime.now()
    details: Optional[Dict[str, Any]] = None