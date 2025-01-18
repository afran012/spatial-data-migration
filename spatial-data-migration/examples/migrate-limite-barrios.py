# examples/migrate_limite_barrios.py
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
from sqlalchemy import create_engine, text
import pyarrow as pa
import pyarrow.parquet as pq
from test_postgres_connection import get_rds_password
import time

def check_table_exists(athena_client, database_name, table_name):
    """Verifica si la tabla ya existe en Athena"""
    try:
        query = f"""
        SHOW TABLES IN {database_name} LIKE '{table_name}'
        """
        
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database_name},
            ResultConfiguration={
                'OutputLocation': f"s3://{os.getenv('ATHENA_OUTPUT_BUCKET')}/{os.getenv('ATHENA_OUTPUT_PREFIX')}"
            }
        )
        
        # Esperar resultado
        query_execution_id = response['QueryExecutionId']
        while True:
            response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            state = response['QueryExecution']['Status']['State']
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
                
        if state == 'SUCCEEDED':
            results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
            return len(results['ResultSet']['Rows']) > 1
            
        return False
    except Exception as e:
        print(f"Error verificando existencia de tabla: {str(e)}")
        return False

def validate_migration(athena_client, database_name, table_name, expected_count):
    """Valida que la migración se haya completado correctamente"""
    try:
        query = f"""
        SELECT COUNT(*) as total_records,
               COUNT(DISTINCT id) as unique_ids,
               COUNT(CASE WHEN wkt_geometry = 'MULTIPOLYGON EMPTY' THEN 1 END) as empty_geoms
        FROM {database_name}.{table_name}
        """
        
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database_name},
            ResultConfiguration={
                'OutputLocation': f"s3://{os.getenv('ATHENA_OUTPUT_BUCKET')}/{os.getenv('ATHENA_OUTPUT_PREFIX')}"
            }
        )
        
        # Esperar resultado
        query_execution_id = response['QueryExecutionId']
        while True:
            response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            state = response['QueryExecution']['Status']['State']
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
                
        if state == 'SUCCEEDED':
            results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
            total_records = int(results['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])
            unique_ids = int(results['ResultSet']['Rows'][1]['Data'][1]['VarCharValue'])
            empty_geoms = int(results['ResultSet']['Rows'][1]['Data'][2]['VarCharValue'])
            
            return {
                'success': total_records == expected_count,
                'total_records': total_records,
                'unique_ids': unique_ids,
                'empty_geoms': empty_geoms,
                'expected_count': expected_count
            }
            
        return None
    except Exception as e:
        print(f"Error en la validación: {str(e)}")
        return None

def create_athena_table(athena_client, database_name, table_name, s3_location):
    """Crea la tabla en Athena con la estructura de límites de barrios"""
    create_table_query = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {database_name}.{table_name} (
        id integer,
        wkt_geometry string,
        comuna string,
        barrio string,
        codigo string,
        nombre_bar string,
        indicador_ string,
        sector integer,
        nombre_com string,
        fecha_sinc string,
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
    return response

def migrate_limite_barrios(table_name='limite_barrio_vereda_cata'):
    """Migración de datos de límites de barrios"""
    try:
        print("\n=== Iniciando migración de límites de barrios y veredas ===")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Verificar si la tabla ya existe
        athena_client = boto3.client('athena')
        if check_table_exists(athena_client, os.getenv('ATHENA_DATABASE'), table_name):
            print(f"\n⚠️ La tabla {table_name} ya existe en Athena")
            user_input = input("¿Desea continuar y sobrescribir la tabla? (s/n): ")
            if user_input.lower() != 's':
                print("Operación cancelada por el usuario")
                return False
            print("\nContinuando con la migración...")
        
        # 1. Extraer datos de PostgreSQL y verificar conteos
        print("\nExtrayendo datos de PostgreSQL...")
        password = get_rds_password()
        connection_string = (
            f"postgresql://{os.getenv('PROD_POSTGRES_USER')}:{password}@"
            f"{os.getenv('PROD_POSTGRES_HOST')}:{os.getenv('PROD_POSTGRES_PORT')}/"
            f"{os.getenv('PROD_POSTGRES_DB')}"
        )
        
        engine = create_engine(connection_string)
        
        # Verificar conteo original
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM shapes.limite_barrio_vereda_cata'))
            original_count = result.scalar()
            
            result = conn.execute(text('SELECT COUNT(DISTINCT id) FROM shapes.limite_barrio_vereda_cata'))
            unique_count = result.scalar()
            
        print(f"Registros totales en PostgreSQL: {original_count}")
        print(f"IDs únicos en PostgreSQL: {unique_count}")
        
        if original_count != unique_count:
            print(f"⚠️ Se detectaron {original_count - unique_count} registros duplicados")
        
        # Query específica para seleccionar solo registros únicos
        query = """
        SELECT DISTINCT ON (id)
            id,
            geom,
            comuna,
            barrio,
            codigo,
            nombre_bar,
            indicador_,
            sector,
            nombre_com,
            fecha_sinc,
            shape_leng,
            shape_area
        FROM shapes.limite_barrio_vereda_cata
        ORDER BY id
        """
        
        gdf = gpd.read_postgis(query, engine, geom_col='geom')
        print(f"\nDatos únicos extraídos: {len(gdf)} registros")
        
        # Verificar sistema de coordenadas
        print(f"Sistema de coordenadas: {gdf.crs}")
        
        # 2. Validar geometrías
        print("\nValidando geometrías...")
        invalid_geoms = (~gdf.geom.is_valid).sum()
        if invalid_geoms > 0:
            print(f"⚠️ Se encontraron {invalid_geoms} geometrías inválidas")
            print("Intentando reparar geometrías inválidas...")
            gdf.geom = gdf.geom.buffer(0)
        else:
            print("✓ Todas las geometrías son válidas")
            
        # Verificar tipo de geometría
        geom_types = gdf.geom.geom_type.unique()
        print(f"Tipos de geometría encontrados: {geom_types}")
        
        # 3. Transformar geometrías a WKT y preparar DataFrame final
        print("\nPreparando datos para migración...")
        df_final = pd.DataFrame({
            'id': gdf.id,
            'wkt_geometry': gdf.geom.apply(lambda x: x.wkt if x is not None else 'MULTIPOLYGON EMPTY'),
            'comuna': gdf.comuna,
            'barrio': gdf.barrio,
            'codigo': gdf.codigo,
            'nombre_bar': gdf.nombre_bar,
            'indicador_': gdf.indicador_,
            'sector': gdf.sector,
            'nombre_com': gdf.nombre_com,
            'fecha_sinc': gdf.fecha_sinc.astype(str),
            'shape_leng': gdf.shape_leng,
            'shape_area': gdf.shape_area
        })
        
        # Verificación final de duplicados
        final_duplicates = df_final.id.duplicated().sum()
        if final_duplicates > 0:
            print(f"⚠️ Advertencia: Aún hay {final_duplicates} IDs duplicados")
            df_final = df_final.drop_duplicates(subset='id', keep='first')
        
        # 4. Convertir a Parquet
        print("\nConvirtiendo a formato Parquet...")
        table = pa.Table.from_pandas(df_final)
        
        # 5. Subir a S3
        print("\nSubiendo datos a S3...")
        s3_client = boto3.client('s3')
        s3_bucket = os.getenv('ATHENA_OUTPUT_BUCKET')
        s3_prefix = os.getenv('S3_PREFIX', 'spatial_data/barrios_veredas')
        s3_full_path = f"{s3_prefix}/{timestamp}"
        
        local_path = f"temp_limite_barrios_{timestamp}.parquet"
        pq.write_table(table, local_path)
        
        s3_client.upload_file(
            local_path,
            s3_bucket,
            f"{s3_full_path}/data.parquet"
        )
        
        if os.path.exists(local_path):
            os.remove(local_path)
            print("✓ Archivo temporal eliminado")
        
        # 6. Crear tabla en Athena
        print("\nCreando tabla en Athena...")
        s3_location = f"s3://{s3_bucket}/{s3_full_path}"
        
        response = create_athena_table(
            athena_client,
            os.getenv('ATHENA_DATABASE'),
            table_name,
            s3_location
        )
        
        # 7. Validar la migración
        print("\nValidando migración...")
        validation_results = validate_migration(
            athena_client,
            os.getenv('ATHENA_DATABASE'),
            table_name,
            len(df_final)
        )
        
        if validation_results:
            print("\n=== Resultados de la Validación ===")
            print(f"✓ Registros esperados: {validation_results['expected_count']}")
            print(f"✓ Registros encontrados: {validation_results['total_records']}")
            print(f"✓ IDs únicos: {validation_results['unique_ids']}")
            print(f"ℹ Geometrías vacías: {validation_results['empty_geoms']}")
            
            if validation_results['success']:
                print("\n✅ Migración completada y validada exitosamente")
            else:
                print("\n⚠️ La migración se completó pero el conteo no coincide")
        else:
            print("\n⚠️ No se pudo validar la migración")
        
        print(f"""
=== Resumen Final de Migración ===
Origen (PostgreSQL):
- Registros totales: {original_count}
- IDs únicos: {unique_count}

Datos Migrados:
- Tabla creada: {os.getenv('ATHENA_DATABASE')}.{table_name}
- Ubicación S3: {s3_location}
- Registros migrados: {len(df_final)}
- Columnas: {', '.join(df_final.columns)}
        """)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en la migración: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    
    import argparse
    parser = argparse.ArgumentParser(description='Migrar datos de límites de barrios a Athena')
    parser.add_argument('--table-name', type=str, default='limite_barrio_vereda_cata',
                      help='Nombre de la tabla en Athena')
    args = parser.parse_args()
    
    migrate_limite_barrios(args.table_name)