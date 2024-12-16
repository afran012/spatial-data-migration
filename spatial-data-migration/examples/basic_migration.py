# examples/basic_migration.py
from spatial_migration.main import SpatialDataMigration
from spatial_migration.config import load_config

def main():
    """Ejemplo básico de migración de datos espaciales"""
    
    # Cargar configuración
    config = load_config()
    
    # Inicializar migrador
    migrator = SpatialDataMigration(config)
    
    # Ejecutar migración
    table_name = "spatial_table"
    success = migrator.run_migration(table_name)
    
    if success:
        print(f"Migración de {table_name} completada exitosamente")
    else:
        print(f"Error en la migración de {table_name}")

if __name__ == "__main__":
    main()