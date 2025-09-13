"""
Gestor de habilidades de Nyx
"""

import json
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SkillManager:
    """
    Maneja la carga, descubrimiento y ejecución de habilidades
    """

    def __init__(self):
        self.skills = {}
        self.skills_path = Path(__file__).parent.parent.parent / 'skills'
        self.load_skills()

    def load_skills(self):
        """
        Descubre y carga todas las habilidades disponibles
        """
        logger.info("Cargando habilidades...")

        if not self.skills_path.exists():
            logger.warning(f"Directorio de skills no encontrado: {self.skills_path}")
            return

        for skill_dir in self.skills_path.iterdir():
            if skill_dir.is_dir() and (skill_dir / 'skill.json').exists():
                try:
                    self.load_skill(skill_dir)
                except Exception as e:
                    logger.error(f"Error cargando skill {skill_dir.name}: {e}")

    def load_skill(self, skill_dir: Path):
        """
        Carga una habilidad específica
        """
        skill_json_path = skill_dir / 'skill.json'

        with open(skill_json_path, 'r') as f:
            skill_config = json.load(f)

        skill_name = skill_config['name']

        # Añadir el directorio de la skill al path
        if str(skill_dir) not in sys.path:
            sys.path.append(str(skill_dir))

        # Importar el módulo principal
        module = importlib.import_module('main')

        # Obtener la clase principal
        skill_class_name = skill_config.get('class', f"{skill_name.title()}Skill")
        skill_class = getattr(module, skill_class_name)

        # Instanciar la skill
        skill_instance = skill_class(skill_config)

        self.skills[skill_name] = {
            'instance': skill_instance,
            'config': skill_config,
            'path': skill_dir
        }

        logger.info(f"Skill cargada: {skill_name}")

    def get_available_skills(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de habilidades disponibles
        """
        skills_list = []

        for skill_name, skill_data in self.skills.items():
            config = skill_data['config']
            skills_list.append({
                'name': skill_name,
                'description': config.get('description', ''),
                'version': config.get('version', '0.1.0'),
                'triggers': config.get('triggers', []),
                'author': config.get('author', 'Unknown')
            })

        return skills_list

    def execute_skill(self, skill_name: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una habilidad específica
        """
        if skill_name not in self.skills:
            return {
                'error': f'Skill no encontrada: {skill_name}',
                'success': False
            }

        try:
            skill = self.skills[skill_name]['instance']
            result = skill.execute(query, context)

            return {
                'success': True,
                'skill': skill_name,
                'result': result
            }

        except Exception as e:
            logger.error(f"Error ejecutando skill {skill_name}: {e}")
            return {
                'error': str(e),
                'success': False,
                'skill': skill_name
            }

    def get_skill_by_trigger(self, query: str) -> Optional[str]:
        """
        Encuentra una skill basada en triggers de palabras clave
        """
        query_lower = query.lower()

        for skill_name, skill_data in self.skills.items():
            triggers = skill_data['config'].get('triggers', [])

            for trigger in triggers:
                if trigger.lower() in query_lower:
                    return skill_name

        return None
