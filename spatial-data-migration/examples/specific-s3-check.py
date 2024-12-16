# examples/check_specific_bucket.py
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

def check_specific_bucket(bucket_name=None):
    """
    Verifica permisos para un bucket específico
    Args:
        bucket_name: Nombre del bucket a verificar (opcional)
    """
    load_dotenv()
    
    # Si no se proporciona un bucket, intentar obtenerlo del .env
    bucket_name = bucket_name or os.getenv('ATHENA_OUTPUT_BUCKET')
    
    if not bucket_name:
        print("\nPor favor, especifica el nombre del bucket a verificar:")
        print("1. Añade ATHENA_OUTPUT_BUCKET en tu archivo .env, o")
        print("2. Pasa el nombre del bucket como argumento al script")
        return False
    
    try:
        # Crear cliente S3
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        
        print(f"\nVerificando permisos para bucket: {bucket_name}")
        
        # Verificar permisos uno por uno
        permissions = {
            'read': False,
            'write': False,
            'list': False
        }
        
        # 1. Verificar permiso de listado
        try:
            s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            permissions['list'] = True
            print("✓ Tienes permiso para listar objetos")
        except ClientError as e:
            print("✗ No tienes permiso para listar objetos")
            print(f"  Error: {e.response['Error']['Message']}")
        
        # 2. Verificar permiso de escritura
        try:
            test_key = 'test_permissions.txt'
            s3.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body='test'
            )
            permissions['write'] = True
            print("✓ Tienes permiso para escribir objetos")
            
            # Intentar eliminar el archivo de prueba
            try:
                s3.delete_object(Bucket=bucket_name, Key=test_key)
                print("✓ Tienes permiso para eliminar objetos")
            except:
                print("✗ No tienes permiso para eliminar objetos")
                
        except ClientError as e:
            print("✗ No tienes permiso para escribir objetos")
            print(f"  Error: {e.response['Error']['Message']}")
        
        # 3. Verificar permiso de lectura
        try:
            s3.get_object(Bucket=bucket_name, Key='any_existing_file.txt')
            permissions['read'] = True
            print("✓ Tienes permiso para leer objetos")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                permissions['read'] = True
                print("✓ Tienes permiso para leer objetos")
            else:
                print("✗ No tienes permiso para leer objetos")
                print(f"  Error: {e.response['Error']['Message']}")
        
        print("\nResumen de permisos:")
        print(f"Listar objetos: {'✓' if permissions['list'] else '✗'}")
        print(f"Escribir objetos: {'✓' if permissions['write'] else '✗'}")
        print(f"Leer objetos: {'✓' if permissions['read'] else '✗'}")
        
        return any(permissions.values())
        
    except Exception as e:
        print(f"\nError verificando bucket: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Verificar permisos de un bucket S3 específico')
    parser.add_argument('--bucket', type=str, help='Nombre del bucket a verificar')
    args = parser.parse_args()
    
    check_specific_bucket(args.bucket)
