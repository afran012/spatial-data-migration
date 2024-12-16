import os

# Estructura de archivos y carpetas
structure = {
    "spatial-data-migration": {
        ".env.example": """POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=spatial_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
S3_BUCKET=your_bucket
GLUE_DATABASE=your_database
""",
        ".gitignore": """__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
dist/
build/
*.egg-info/
.coverage
htmlcov/
.pytest_cache/
.idea/
.vscode/
*.log
*.parquet
.DS_Store
""",
        "README.md": "# Documentación principal del proyecto",
        "pyproject.toml": """[tool.poetry]
name = "spatial-data-migration"
version = "0.1.0"
description = "Herramienta para migrar datos espaciales de PostgreSQL a Amazon Athena"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
geopandas = "^0.12.0"
pandas = "^1.5.0"
sqlalchemy = "^2.0.0"
psycopg2-binary = "^2.9.5"
boto3 = "^1.26.0"
python-dotenv = "^0.21.0"
pyarrow = "^11.0.0"
loguru = "^0.7.0"

[tool.poetry.dev-dependencies]
pytest = "^7.3.1"
black = "^23.3.0"
flake8 = "^6.0.0"
mypy = "^1.3.0"
pytest-cov = "^4.0.0"
pre-commit = "^3.3.1"
""",
        "setup.cfg": "# Configuración para herramientas de desarrollo",
        "Makefile": """.PHONY: install test lint format clean

install:
\tpoetry install

test:
\tpoetry run pytest tests/ --cov=src/

lint:
\tpoetry run flake8 src/ tests/
\tpoetry run mypy src/ tests/

format:
\tpoetry run black src/ tests/

clean:
\trm -rf dist/
\trm -rf build/
\trm -rf *.egg-info
\tfind . -type d -name __pycache__ -exec rm -rf {} +
\tfind . -type d -name .pytest_cache -exec rm -rf {} +
\tfind . -type d -name .coverage -exec rm -rf {} +
""",
        "src": {
            "spatial_migration": {
                "__init__.py": "",
                "main.py": "# Punto de entrada principal",
                "config.py": "# Configuración y carga de variables de entorno",
                "logger.py": "# Configuración de logging",
                "core": {
                    "__init__.py": "",
                    "extractor.py": "# Extracción de datos de PostgreSQL",
                    "transformer.py": "# Transformación de datos espaciales",
                    "loader.py": "# Carga a S3 y configuración de Glue",
                },
                "models": {
                    "__init__.py": "",
                    "schemas.py": "# Definición de modelos de datos",
                },
                "utils": {
                    "__init__.py": "",
                    "aws.py": "# Utilidades para AWS",
                    "db.py": "# Utilidades para base de datos",
                    "validators.py": "# Validaciones",
                },
                "exceptions": {
                    "__init__.py": "",
                    "custom_exceptions.py": "# Excepciones personalizadas",
                },
            },
        },
        "tests": {
            "__init__.py": "",
            "conftest.py": "# Configuración de pruebas",
            "test_extractor.py": "",
            "test_transformer.py": "",
            "test_loader.py": "",
        },
        "scripts": {
            "setup_aws.sh": "# Script para configuración de AWS",
            "setup_database.sh": "# Script para configuración de la base de datos",
        },
        "docs": {
            "architecture.md": "# Documentación de arquitectura",
            "deployment.md": "# Guía de despliegue",
            "development.md": "# Guía de desarrollo",
        },
        "examples": {
            "basic_migration.py": "",
            "advanced_migration.py": "",
        },
    },
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content)

base_path = r"C:\Users\Steev\Documents\AiranFranco\sisc\athena"
create_structure(base_path, structure)