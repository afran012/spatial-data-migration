# Script para configuraci�n de la base de datos
# scripts/setup_database.sh
#!/bin/bash

# Script para configurar la base de datos PostgreSQL

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Cargar variables de entorno
source .env

# Verificar si PostgreSQL está instalado
if ! command -v psql &>/dev/null; then
    echo -e "${RED}Error: PostgreSQL no está instalado${NC}"
    exit 1
fi

# Verificar si PostGIS está instalado
echo -e "${YELLOW}Verificando PostGIS...${NC}"
if ! psql -d "${POSTGRES_DB}" -c "SELECT PostGIS_version();" &>/dev/null; then
    echo "Instalando PostGIS..."
    psql -d "${POSTGRES_DB}" -c "CREATE EXTENSION postgis;"
fi

# Crear tablas necesarias
echo -e "${YELLOW}Creando tablas...${NC}"
psql -d "${POSTGRES_DB}" -f sql/create_tables.sql

# Crear índices espaciales
echo -e "${YELLOW}Creando índices espaciales...${NC}"
psql -d "${POSTGRES_DB}" -f sql/create_indexes.sql

# Verificar la instalación
echo -e "${YELLOW}Verificando la instalación...${NC}"
if psql -d "${POSTGRES_DB}" -c "\dt" | grep -q 'spatial'; then
    echo -e "${GREEN}Configuración de base de datos completada${NC}"
else
    echo -e "${RED}Error: La configuración de la base de datos falló${NC}"
    exit 1
fi