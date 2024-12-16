# Gu�a de desarrollo

# Guía de Desarrollo

## Configuración del Entorno

1. **Clonar Repositorio**
   ```bash
   git clone https://github.com/your-org/spatial-data-migration
   cd spatial-data-migration
   ```

2. **Instalar Dependencias**
   ```bash
   poetry install
   ```

3. **Configurar Pre-commit**
   ```bash
   pre-commit install
   ```

## Estructura del Proyecto

```
spatial-data-migration/
├── src/
│   └── spatial_migration/
│       ├── core/          # Componentes principales
│       ├── utils/         # Utilidades
│       └── exceptions/    # Excepciones personalizadas
├── tests/                 # Pruebas unitarias
└── examples/              # Ejemplos de uso
```

## Guías de Estilo

- Seguir PEP 8
- Docstrings en formato Google
- Type hints para todos los métodos públicos
- Tests para toda nueva funcionalidad

## Flujo de Trabajo

1. Crear rama feature: `git checkout -b feature/nombre`
2. Desarrollar y probar
3. Ejecutar pruebas: `poetry run pytest`
4. Commit y push
5. Crear Pull Request

## Mejores Prácticas

- Mantener clases y métodos pequeños y enfocados
- Escribir tests unitarios
- Documentar cambios importantes
- Mantener el changelog actualizado