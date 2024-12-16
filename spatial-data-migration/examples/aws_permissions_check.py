# examples/check_s3_permissions.py
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

def check_s3_permissions():
    """Verifica permisos específicos de S3"""
    load_dotenv()
    
    try:
        # Crear cliente S3
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        
        print("\n=== Verificación de Acceso a S3 ===")
        
        # 1. Listar buckets disponibles
        print("\nListando buckets disponibles:")
        buckets = s3.list_buckets()['Buckets']
        
        if not buckets:
            print("No se encontraron buckets accesibles")
            return
            
        for bucket in buckets:
            bucket_name = bucket['Name']
            print(f"\nBucket: {bucket_name}")
            
            # 2. Verificar permisos específicos para cada bucket
            permissions = {
                'read': False,
                'write': False,
                'list': False
            }
            
            try:
                # Verificar permiso de listado
                s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                permissions['list'] = True
                
                # Verificar permiso de escritura
                test_key = 'test_permissions.txt'
                s3.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body='test'
                )
                permissions['write'] = True
                
                # Verificar permiso de lectura
                s3.get_object(Bucket=bucket_name, Key=test_key)
                permissions['read'] = True
                
                # Limpiar archivo de prueba
                s3.delete_object(Bucket=bucket_name, Key=test_key)
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code in ['AccessDenied', 'AllAccessDisabled']:
                    pass  # Los permisos ya están marcados como False
            
            # Mostrar permisos
            print("Permisos:")
            print(f"  ├─ Listar: {'✓' if permissions['list'] else '✗'}")
            print(f"  ├─ Leer: {'✓' if permissions['read'] else '✗'}")
            print(f"  └─ Escribir: {'✓' if permissions['write'] else '✗'}")
            
            # 3. Verificar permisos de Athena si existe el prefijo queries/
            try:
                athena_prefix = 'queries/'
                s3.list_objects_v2(Bucket=bucket_name, Prefix=athena_prefix, MaxKeys=1)
                print(f"\nPrefijo Athena ({athena_prefix}):")
                print("  └─ Accesible: ✓")
            except ClientError:
                print(f"\nPrefijo Athena ({athena_prefix}):")
                print("  └─ Accesible: ✗")
        
        return True
        
    except Exception as e:
        print(f"\nError verificando permisos: {str(e)}")
        return False

if __name__ == "__main__":
    check_s3_permissions()