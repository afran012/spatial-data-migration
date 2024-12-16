# Script para configuraci�n de AWS
# scripts/setup_aws.sh
#!/bin/bash

# Script para configurar recursos de AWS necesarios

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Cargar variables de entorno
source .env

# Verificar credenciales de AWS
echo -e "${YELLOW}Verificando credenciales de AWS...${NC}"
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}Error: Credenciales de AWS no configuradas${NC}"
    exit 1
fi

# Crear bucket S3 si no existe
echo -e "${YELLOW}Configurando bucket S3...${NC}"
if ! aws s3 ls "s3://${S3_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Bucket ${S3_BUCKET} ya existe"
else
    aws s3api create-bucket \
        --bucket "${S3_BUCKET}" \
        --region "${AWS_REGION}" \
        --create-bucket-configuration LocationConstraint="${AWS_REGION}"
    
    # Configurar lifecycle policy
    aws s3api put-bucket-lifecycle-configuration \
        --bucket "${S3_BUCKET}" \
        --lifecycle-configuration file://configs/s3-lifecycle.json
fi

# Crear base de datos en Glue si no existe
echo -e "${YELLOW}Configurando base de datos en Glue...${NC}"
if ! aws glue get-database --name "${GLUE_DATABASE}" &>/dev/null; then
    aws glue create-database \
        --database-input "{\"Name\":\"${GLUE_DATABASE}\",\"Description\":\"Database for spatial data\"}"
fi

# Configurar permisos IAM
echo -e "${YELLOW}Configurando permisos IAM...${NC}"
aws iam create-role \
    --role-name spatial-migration-role \
    --assume-role-policy-document file://configs/trust-policy.json

aws iam put-role-policy \
    --role-name spatial-migration-role \
    --policy-name spatial-migration-policy \
    --policy-document file://configs/policy.json

echo -e "${GREEN}Configuración de AWS completada${NC}"
