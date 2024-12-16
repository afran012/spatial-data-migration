# Configuraci�n de logging

import logging
import sys
from datetime import datetime

def setup_logger() -> logging.Logger:
    """Configura y retorna el logger principal"""
    logger = logging.getLogger('spatial_migration')
    logger.setLevel(logging.INFO)

    # Crear formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo
    file_handler = logging.FileHandler(
        f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
