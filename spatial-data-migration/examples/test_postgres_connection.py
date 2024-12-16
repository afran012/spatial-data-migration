# examples/test_postgres_connection.py
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path de Python
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from dotenv import load_dotenv
import geopandas as gpd
import boto3
from sqlalchemy import create_engine, text

def get_rds_password():
    """Obtiene el token de autenticación de AWS RDS"""
    client = boto3.client('rds',
                         region_name=os.getenv('AWS_DEFAULT_REGION'),
                         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    try:
        token = client.generate_db_auth_token(
            DBHostname=os.getenv('PROD_POSTGRES_HOST'),
            Port=int(os.getenv('PROD_POSTGRES_PORT', '5432')),
            DBUsername=os.getenv('PROD_POSTGRES_USER'),
            Region=os.getenv('AWS_DEFAULT_REGION')
        )
        return token
    except Exception as e:
        print(f"Error generando token de autenticación: {e}")
        return None

def test_postgres_connection():
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener el token de autenticación
    password = get_rds_password()
    if not password:
        print("Error: No se pudo obtener el token de autenticación")
        return False
    
    # Crear string de conexión
    connection_string = (
        f"postgresql://{os.getenv('PROD_POSTGRES_USER')}:{password}@"
        f"{os.getenv('PROD_POSTGRES_HOST')}:{os.getenv('PROD_POSTGRES_PORT')}/"
        f"{os.getenv('PROD_POSTGRES_DB')}"
    )
    
    try:
        print("Intentando conectar a PostgreSQL...")
        engine = create_engine(connection_string)
        
        # Probar la conexión
        with engine.connect() as connection:
            print("¡Conexión exitosa!")
            
            # Consultar estructura de la tabla
            print("\nConsultando estructura de la tabla...")
            query = text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'shapes' 
                AND table_name = 'cuadrantes'
                ORDER BY ordinal_position;
            """)
            
            result = connection.execute(query)
            print("\nEstructura de la tabla:")
            for row in result:
                print(f"Columna: {row[0]}, Tipo: {row[1]}")
            
            # Consultar datos espaciales
            print("\nConsultando datos espaciales...")
            gdf = gpd.read_postgis(
                """
                SELECT *
                FROM shapes.cuadrantes
                LIMIT 5;
                """,
                engine,
                geom_col='geom'
            )
            
            print("\nPrimeros registros encontrados:")
            print(f"Total de columnas: {len(gdf.columns)}")
            print(f"Columnas disponibles: {', '.join(gdf.columns)}")
            
        return True
        
    except Exception as e:
        print(f"\nError en la conexión: {str(e)}")
        return False

if __name__ == "__main__":
    test_postgres_connection()