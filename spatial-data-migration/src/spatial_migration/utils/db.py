# Utilidades para base de datos
# # src/spatial_migration/utils/db.py
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from ..exceptions import ConfigurationError
from ..logger import setup_logger

logger = setup_logger()

class DatabaseConnection:
    """Clase para manejar conexiones a PostgreSQL."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            config: Diccionario con la configuración de conexión
        """
        self.config = config
        self._conn = None
        self._cur = None

    def connect(self):
        """Establece la conexión a la base de datos."""
        try:
            self._conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self._cur = self._conn.cursor(cursor_factory=RealDictCursor)
            logger.info("Conexión a base de datos establecida")
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {str(e)}")
            raise ConfigurationError(f"Error de conexión: {str(e)}")

    def disconnect(self):
        """Cierra la conexión a la base de datos."""
        if self._cur:
            self._cur.close()
        if self._conn:
            self._conn.close()
            logger.info("Conexión a base de datos cerrada")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """
        Ejecuta una consulta SQL.
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
        
        Returns:
            Lista de resultados
        """
        try:
            self._cur.execute(query, params)
            return self._cur.fetchall()
        except Exception as e:
            self._conn.rollback()
            logger.error(f"Error ejecutando consulta: {str(e)}")
            raise

    def execute_batch(self, query: str, params_list: list):
        """
        Ejecuta una consulta SQL en modo batch.
        
        Args:
            query: Consulta SQL
            params_list: Lista de parámetros
        """
        try:
            psycopg2.extras.execute_batch(self._cur, query, params_list)
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            logger.error(f"Error ejecutando batch: {str(e)}")
            raise

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Obtiene el schema de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Diccionario con el schema de la tabla
        """
        query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        """
        try:
            results = self.execute_query(query, (table_name,))
            return {row['column_name']: row['data_type'] for row in results}
        except Exception as e:
            logger.error(f"Error obteniendo schema: {str(e)}")
            raise