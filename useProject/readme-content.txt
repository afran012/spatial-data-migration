# Spatial Data Migration Tool

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
```

2. Instalar dependencias:
```bash
poetry install
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

## Uso

### Migración Básica

```python
from spatial_migration.main import SpatialDataMigration
from spatial_migration.config import load_config

config = load_config()
migrator = SpatialDataMigration(config)
migrator.run_migration('nombre_tabla')
```

### Migración Avanzada

Ver ejemplos en el directorio `examples/` para casos de uso más avanzados.

## Desarrollo

1. Configurar entorno de desarrollo:
```bash
make install
```

2. Ejecutar pruebas:
```bash
make test
```

3. Verificar estilo de código:
```bash
make lint
```

4. Formatear código:
```bash
make format
```

## Arquitectura

La herramienta sigue una arquitectura modular con tres componentes principales:

1. **Extractor**: Maneja la conexión y extracción de datos de PostgreSQL
2. **Transformer**: Procesa y transforma los datos espaciales
3. **Loader**: Gestiona la carga a S3 y la configuración de Glue

Para más detalles, ver `docs/architecture.md`.

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## Contacto

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/your-username/spatial-data-migration](https://github.com/your-username/spatial-data-migration)
