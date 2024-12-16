# examples/advanced_migration.py
from spatial_migration.main import SpatialDataMigration
from spatial_migration.config import load_config
from spatial_migration.utils.validators import DataValidator
import logging

def setup_logging():
    """Configura logging avanzado"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='advanced_migration.log'
    )

def migrate_with_validation(config, table_name, validation_options=None):
    """
    Ejecuta migración con validaciones adicionales
    
    Args:
        config: Configuración del sistema
        table_name: Nombre de la tabla a migrar
        validation_options: Opciones adicionales de validación
    """
    migrator = SpatialDataMigration(config)
    validator = DataValidator()
    
    # Extraer datos para validación previa
    logging.info(f"Iniciando validación previa de {table_name}")
    data = migrator.extractor.extract_table(table_name)
    
    # Validar datos
    validation_results = validator.validate_spatial_data(data)
    if not validation_results['is_valid']:
        logging.error(f"Validación fallida: {validation_results['errors']}")
        return False
    
    # Ejecutar migración si la validación es exitosa
    logging.info("Validación exitosa, procediendo con la migración")
    return migrator.run_migration(
        table_name,
        options={'validation_results': validation_results}
    )

def main():
    """Ejemplo avanzado de migración con validaciones"""
    setup_logging()
    
    try:
        config = load_config()
        table_name = "complex_spatial_table"
        
        validation_options = {
            'check_geometry': True,
            'validate_crs': True,
            'check_attributes': True
        }
        
        success = migrate_with_validation(
            config,
            table_name,
            validation_options
        )
        
        if success:
            logging.info(f"Migración avanzada de {table_name} completada")
        else:
            logging.error(f"Error en la migración avanzada de {table_name}")
            
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        raise

if __name__ == "__main__":
    main()
