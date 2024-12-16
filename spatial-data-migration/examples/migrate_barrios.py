# examples/migrate_barrios.py
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

def migrate_barrios_veredas(table_name='barrios_veredas'):
    """
    Función principal de migración para barrios y veredas
    
    Args:
        table_name: Nombre de la tabla en Athena (default: barrios_veredas)
    """
    try:
        print("Iniciando proceso de migración de barrios y veredas...")
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
            "SELECT * FROM shapes.barrios_veredas",
            engine,
            geom_col='geom'
        )
        
        print(f"Datos extraídos: {len(gdf)} registros")
        
        # Verificar sistema de coordenadas
        if gdf.crs:
            print(f"Sistema de coordenadas original: {gdf.crs}")
        else:
            print("Advertencia: No se detectó sistema de coordenadas")
        
        # Validar la integridad de las geometrías
        print("\nValidando geometrías...")
        invalid_geoms = (~gdf.geom.is_valid).sum()
        if invalid_geoms > 0:
            print(f"⚠️ Se encontraron {invalid_geoms} geometrías inválidas")
            # Opcionalmente, intentar reparar geometrías inválidas
            gdf.geom = gdf.geom.buffer(0)
        else:
            print("✓ Todas las geometrías son válidas")
        
        # 2. Transformar geometrías a WKT
        print("Transformando geometrías...")
        # Crear una copia del DataFrame y añadir la columna WKT
        df_final = gdf.copy()
        df_final['wkt_geometry'] = gdf['geom'].apply(lambda x: x.wkt)
        # Eliminar solo la columna 'geom'
        df_final = df_final.drop(columns=['geom'])
        
        # 3. Preparar datos para Parquet
        print("Convirtiendo a Parquet...")
        table = pa.Table.from_pandas(df_final)
        
        # 4. Subir a S3
        print("Subiendo datos a S3...")
        s3_client = boto3.client('s3')
        s3_bucket = os.getenv('ATHENA_OUTPUT_BUCKET')
        s3_prefix = f"spatial_data/barrios_veredas/{timestamp}"
        
        # Guardar temporalmente y subir a S3
        local_path = f"temp_barrios_veredas_{timestamp}.parquet"
        pq.write_table(table, local_path)
        
        s3_client.upload_file(
            local_path,
            s3_bucket,
            f"{s3_prefix}/data.parquet"
        )
        
        # Limpiar archivo temporal
        if os.path.exists(local_path):
            os.remove(local_path)
            print("Archivo temporal eliminado")
        
        # 5. Crear tabla en Athena
        print("Creando tabla en Athena...")
        athena_client = boto3.client('athena')
        s3_location = f"s3://{s3_bucket}/{s3_prefix}"
        
        create_table_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {os.getenv('ATHENA_DATABASE')}.{table_name} (
            id integer,
            wkt_geometry string,
            codigo string,
            nombre string,
            identifica string,
            limitecomu string,
            limitemuni string,
            subtipo_ba bigint,
            shape_leng double,
            shape_area double
        )
        STORED AS PARQUET
        LOCATION '{s3_location}/'
        TBLPROPERTIES ('parquet.compression'='SNAPPY');
        """
        
        response = athena_client.start_query_execution(
            QueryString=create_table_query,
            QueryExecutionContext={'Database': os.getenv('ATHENA_DATABASE')},
            ResultConfiguration={
                'OutputLocation': f"s3://{s3_bucket}/{os.getenv('ATHENA_OUTPUT_PREFIX')}"
            }
        )
        
        print(f"""
        Migración completada:
        - Datos guardados en: {s3_location}
        - Tabla creada: {os.getenv('ATHENA_DATABASE')}.{table_name}
        - Total registros migrados: {len(df_final)}
        - Columnas migradas: {', '.join(df_final.columns)}
        """)
        
        return True
        
    except Exception as e:
        print(f"Error en la migración: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    
    import argparse
    parser = argparse.ArgumentParser(description='Migrar datos de barrios y veredas a Athena')
    parser.add_argument('--table-name', type=str, default='barrios_veredas',
                      help='Nombre de la tabla en Athena')
    args = parser.parse_args()
    
    migrate_barrios_veredas(args.table_name)