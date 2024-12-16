from spatial_migration.main import SpatialDataMigration
from spatial_migration.config import Config

def main():
    # Configuración
    config = {
        'postgres': {
            'host': 'tu-host',
            'port': 5432,
            'database': 'tu-database',
            'user': 'tu-usuario',
            'password': 'tu-password'
        },
        'aws': {
            'bucket': 'tu-bucket',
            'prefix': 'spatial-data',
            'region': 'tu-region',
            'database': 'tu-database-athena'
        }
    }
    
    # Iniciar migración
    try:
        migrator = SpatialDataMigration(config)
        success = migrator.migrate_table(
            table_name='tu_tabla',
            validate_data=True,
            generate_report=True
        )
        
        if success:
            print("Migración completada exitosamente")
        else:
            print("La migración falló")
            
    except Exception as e:
        print(f"Error en la migración: {str(e)}")

if __name__ == "__main__":
    main()