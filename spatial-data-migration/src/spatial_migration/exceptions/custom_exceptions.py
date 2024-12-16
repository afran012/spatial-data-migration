# src/spatial_migration/exceptions/custom_exceptions.py
class ExtractionError(Exception):
    """Raised when hay un error durante la extracción de datos."""
    pass

class TransformationError(Exception):
    """Raised when hay un error durante la transformación de datos."""
    pass

class LoadError(Exception):
    """Raised when hay un error durante la carga de datos."""
    pass

class ValidationError(Exception):
    """Raised when los datos no pasan la validación."""
    pass

class ConfigurationError(Exception):
    """Raised when hay un error en la configuración."""
    pass
