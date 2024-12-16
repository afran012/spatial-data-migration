"""
Script para probar la conexión a Amazon Athena y realizar una consulta simple.
"""
import boto3
import os
from dotenv import load_dotenv
import time

def test_athena_connection():
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar cliente de Athena
    athena_client = boto3.client(
        'athena',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )
    
    try:
        # Consulta simple para probar la conexión
        query = "SHOW TABLES IN " + os.getenv('ATHENA_DATABASE')
        
        # Configurar la consulta
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': os.getenv('ATHENA_DATABASE')
            },
            ResultConfiguration={
                'OutputLocation': f"s3://{os.getenv('ATHENA_OUTPUT_BUCKET')}/{os.getenv('ATHENA_OUTPUT_PREFIX')}"
            }
        )
        
        # Obtener el ID de la consulta
        query_execution_id = response['QueryExecutionId']
        print(f"Ejecutando consulta (ID: {query_execution_id})...")
        
        # Esperar por los resultados
        while True:
            query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            state = query_status['QueryExecution']['Status']['State']
            
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                print(f"Estado final de la consulta: {state}")
                break
                
            print("Esperando resultados...")
            time.sleep(1)
        
        # Si la consulta fue exitosa, mostrar resultados
        if state == 'SUCCEEDED':
            results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
            
            print("\nTablas encontradas:")
            for row in results['ResultSet']['Rows'][1:]:  # Saltar el encabezado
                print(f"- {row['Data'][0]['VarCharValue']}")
                
            print("\n¡Conexión exitosa a Athena!")
            return True
            
        else:
            error_details = query_status['QueryExecution']['Status'].get('StateChangeReason', 'No details available')
            print(f"\nError en la consulta: {error_details}")
            return False
            
    except Exception as e:
        print(f"\nError conectando a Athena: {str(e)}")
        return False

if __name__ == "__main__":
    test_athena_connection()
