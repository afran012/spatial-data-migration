# examples/migrate_spatial_data.py
import os
import sys
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al path de Python
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from dotenv import load_dotenv
import geopandas as gpd
import pandas as pd
import boto3
from sqlalchemy import create_engine
import pyarrow as pa
import pyarrow.parquet as pq
from test_postgres_connection import get_rds_password

def create_athena_table(athena_client, database_name, table_name, s3_location):
    """Crea la tabla en Athena"""
    create_table_query = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {database_name}.{table_name} (
        id integer,
        wkt_geometry string,
        objectid_1 bigint,
        objectid bigint,
        nro_cuadra string,
        latitud double,
        longitud double,
        codigo_sie bigint,
        tel string,
        cuadrante bigint,
        estacion string,
        distrito string,
        shape_leng double,
        shape_area double
    )
    STORED AS PARQUET
    LOCATION '{s3_location}/'
    TBLPROPERTIES ('parquet.compression'='SNAPPY');
    """
    
    response = athena_client.start_query_execution(
        QueryString=create_table_query,
        QueryExecutionContext={'Database': database_name},
        ResultConfiguration={
            'OutputLocation': f"s3://{os.getenv('ATHENA_OUTPUT_BUCKET')}/{os.getenv('ATHENA_OUTPUT_PREFIX')}"
        }
    )
    return response['QueryExecutionId']

def migrate_spatial_data():
    """Función principal de migración"""
    try:
        print("Iniciando proceso de migración...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Extraer datos de PostgreSQL
        print("Extrayendo datos de PostgreSQL...")
        password = get_rds_password()
        connection_string = (
            f"postgresql://{os.getenv('PROD_POSTGRES_USER')}:{password}@"
            f"{os.getenv('PROD_POSTGRES_HOST')}:{os.getenv('PROD_POSTGRES_PORT')}/"
            f"{os.getenv('PROD_POSTGRES_DB')}"
        )
        
        engine = create_engine(connection_string)
        gdf = gpd.read_postgis(
            "SELECT * FROM shapes.cuadrantes",
            engine,
            geom_col='geom'
        )
        
        print(f"Datos extraídos: {len(gdf)} registros")
        
        # 2. Transformar geometrías a WKT
        print("Transformando geometrías...")
        gdf['wkt_geometry'] = gdf['geom'].apply(lambda x: x.wkt)
        gdf = gdf.drop(columns=['geom'])
        
        # 3. Preparar datos para Parquet
        print("Convirtiendo a Parquet...")
        table = pa.Table.from_pandas(gdf)
        
        # 4. Subir a S3
        print("Subiendo datos a S3...")
        s3_client = boto3.client('s3')
        s3_bucket = os.getenv('ATHENA_OUTPUT_BUCKET')
        s3_prefix = f"dwh/seguridad/spatial_data/cuadrantes/{timestamp}"
        
        # Guardar temporalmente y subir a S3
        local_path = f"temp_spatial_data_{timestamp}.parquet"
        pq.write_table(table, local_path)
        
        s3_client.upload_file(
            local_path,
            s3_bucket,
            f"{s3_prefix}/data.parquet"
        )
        
        # Limpiar archivo temporal
        os.remove(local_path)
        
        # 5. Crear tabla en Athena
        print("Creando tabla en Athena...")
        athena_client = boto3.client('athena')
        s3_location = f"s3://{s3_bucket}/{s3_prefix}"
        
        query_execution_id = create_athena_table(
            athena_client,
            os.getenv('ATHENA_DATABASE'),
            'cuadrantes',
            s3_location
        )
        
        # 6. Verificar resultados
        print("Verificando migración...")
        verification_query = f"SELECT COUNT(*) FROM {os.getenv('ATHENA_DATABASE')}.cuadrantes"
        response = athena_client.start_query_execution(
            QueryString=verification_query,
            QueryExecutionContext={'Database': os.getenv('ATHENA_DATABASE')},
            ResultConfiguration={
                'OutputLocation': f"s3://{s3_bucket}/{os.getenv('ATHENA_OUTPUT_PREFIX')}"
            }
        )
        
        print(f"""
        Migración completada:
        - Datos guardados en: {s3_location}
        - Tabla creada: {os.getenv('ATHENA_DATABASE')}.cuadrantes
        - Total registros migrados: {len(gdf)}
        """)
        
        return True
        
    except Exception as e:
        print(f"Error en la migración: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    migrate_spatial_data()
