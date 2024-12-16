# Documentaci�n principal del proyecto# Spatial Data Migration Tool

Herramienta para migrar datos espaciales desde PostgreSQL/PostGIS hacia Amazon Athena, facilitando el análisis de big data geoespacial.

## Características

- Extracción eficiente de datos espaciales desde PostgreSQL/PostGIS
- Transformación a formato Parquet optimizado para consultas
- Carga automática a Amazon S3
- Configuración de AWS Glue para catalogación de datos
- Validación automática de la migración
- Sistema de logging robusto
- Manejo de errores comprehensivo

## Requisitos

- Python 3.9+
- PostgreSQL con extensión PostGIS
- Cuenta de AWS con acceso a S3, Glue y Athena
- Poetry para gestión de dependencias

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/your-username/spatial-data-migration.git
cd spatial-data-migration