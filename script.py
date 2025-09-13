# Crear la estructura básica del proyecto Nyx siguiendo las especificaciones del PDF

import os
import json
from pathlib import Path

# Crear la estructura de directorios
project_structure = {
    'nyx': {
        'server': {
            'src': {},
            'package.json': {},
            '.gitignore': {}
        },
        'bridge': {
            'src': {},
            'requirements.txt': {},
            'main.py': {},
            '__init__.py': {}
        },
        'skills': {
            'calendar': {
                'skill.json': {},
                'main.py': {},
                'config.schema.json': {},
                'requirements.txt': {}
            },
            'perplexity': {
                'skill.json': {},
                'main.py': {},
                'requirements.txt': {}
            }
        },
        'clients': {
            '__init__.py': {},
            'gemini_client.py': {},
            'perplexity_client.py': {},
            'calendar_client.py': {},
            'budget_governor.py': {}
        },
        'docs': {},
        'tests': {},
        'data': {},
        '.env.example': {},
        '.gitignore': {},
        'README.md': {},
        'docker-compose.yml': {},
        'Dockerfile': {}
    }
}

def create_directory_structure(base_path, structure):
    """Crea la estructura de directorios especificada"""
    for name, content in structure.items():
        path = base_path / name
        if isinstance(content, dict) and content:  # Es un directorio
            path.mkdir(exist_ok=True)
            print(f"Directorio creado: {path}")
            create_directory_structure(path, content)
        else:  # Es un archivo
            path.touch(exist_ok=True)
            print(f"Archivo creado: {path}")

# Crear estructura base
base_path = Path('.')
create_directory_structure(base_path, project_structure)

print("\n✅ Estructura básica de directorios creada exitosamente")