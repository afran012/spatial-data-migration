# examples/check_aws_credentials.py
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def check_aws_credentials():
    """Verifica si las credenciales AWS están configuradas correctamente"""
    
    # 1. Cargar variables de entorno
    load_dotenv()
    
    # 2. Verificar existencia de credenciales
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION')
    
    print("\nVerificando credenciales AWS...")
    
    # Verificar si existen las variables
    if not all([aws_access_key, aws_secret_key, aws_region]):
        print("\nFaltan credenciales AWS en el archivo .env:")
        print(f"AWS_ACCESS_KEY_ID: {'✓' if aws_access_key else '✗'}")
        print(f"AWS_SECRET_ACCESS_KEY: {'✓' if aws_secret_key else '✗'}")
        print(f"AWS_DEFAULT_REGION: {'✓' if aws_region else '✗'}")
        return False
    
    # 3. Intentar usar las credenciales
    try:
        # Crear cliente AWS con las credenciales explícitas
        sts = boto3.client(
            'sts',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Intentar obtener la identidad
        identity = sts.get_caller_identity()
        
        print("\nCredenciales verificadas correctamente:")
        print(f"Account ID: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")
        print(f"Region: {aws_region}")
        return True
        
    except NoCredentialsError:
        print("\nError: No se encontraron credenciales AWS")
        return False
    except ClientError as e:
        print(f"\nError: Las credenciales no son válidas: {str(e)}")
        return False
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    check_aws_credentials()