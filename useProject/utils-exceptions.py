# src/spatial_migration/utils/aws.py
import boto3
from typing import Optional
from ..logger import setup_logger

logger = setup_logger()

def get_athena_query_results(
    query: str,
    database: str,
    s3_output: str,
    region: str,
    max_execution_time: int = 300
) -> Optional[list]:
    """
    Ejecuta una consulta en Athena y espera los resultados
    
    Args:
        query: Consulta SQL
        database: Base de datos de Athena
        s3_output: Ubicación en S3 para resultados
        region: Región de AWS
        max_execution_time: Tiempo máximo de espera en segundos
    
    Returns:
        Lista de resultados o None si hay error
    """
    try:
        athena_client = boto3.client('athena', region_name=region)
        
        # Iniciar consulta
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': s3_output
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # Esperar resultados
        state = 'RUNNING'
        while max_execution_time > 0 and state in ['RUNNING', 'QUEUED']:
            response = athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            state = response['QueryExecution']['Status']['State']
            
            if state == 'FAILED':
                reason = response['QueryExecution']['Status']['StateChangeReason']
                logger.error(f"Query failed: {reason}")
                return None
                
            if state == 'SUCCEEDED':
                results = athena_client.get_query_results(
                    QueryExecutionId=query_execution_id
                )
                return results['ResultSet']['Rows']
            
            max_execution_time -= 1
            
        return None
        
    except Exception as e:
        logger.error(f"Error en consulta Athena: {str(e)}")
        return None

# src/spatial_migration/utils/validators.py
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
        