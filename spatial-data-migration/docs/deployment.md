# Guía de Despliegue

## Requisitos Previos

### Software
- Python 3.9+
- PostgreSQL con PostGIS
- AWS CLI configurado
- Poetry

### Credenciales
- Acceso a PostgreSQL
- Credenciales de AWS con permisos para:
  - S3
  - Glue
  - Athena

## Pasos de Instalación

1. **Preparación del Entorno**
   ```bash
   git clone https://github.com/your-org/spatial-data-migration
   cd spatial-data-migration
   poetry install
   ```

2. **Configuración**
   ```bash
   cp .env.example .env
   # Editar .env con las credenciales correspondientes
   ```

3. **Configuración de AWS**
   ```bash
   ./scripts/setup_aws.sh
   ```

4. **Configuración de Base de Datos**
   ```bash
   ./scripts/setup_database.sh
   ```

## Verificación del Despliegue

1. **Pruebas Básicas**
   ```bash
   poetry run pytest
   ```

2. **Migración de Prueba**
   ```bash
   poetry run python examples/basic_migration.py
   ```