"""
Clase base para todas las habilidades de Nyx
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class Skill(ABC):
    """
    Clase base abstracta para todas las habilidades
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unnamed_skill')
        self.version = config.get('version', '0.1.0')
        self.description = config.get('description', '')
        self.triggers = config.get('triggers', [])

        logger.info(f"Skill {self.name} v{self.version} inicializada")

    @abstractmethod
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la habilidad con la consulta dada

        Args:
            query: La consulta del usuario
            context: Contexto adicional (user_id, datos estructurados, etc.)

        Returns:
            Dict con el resultado de la ejecución
        """
        pass

    def validate_input(self, query: str, context: Dict[str, Any]) -> bool:
        """
        Valida la entrada antes de ejecutar
        """
        return len(query.strip()) > 0

    def format_response(self, result: Any, response_type: str = 'text') -> Dict[str, Any]:
        """
        Formatea la respuesta en un formato estándar
        """
        return {
            'content': result,
            'type': response_type,
            'skill': self.name,
            'timestamp': None  # Se añadirá en el router
        }

    def get_help(self) -> str:
        """
        Retorna información de ayuda para esta habilidad
        """
        return f"""
Skill: {self.name} v{self.version}
Descripción: {self.description}
Triggers: {', '.join(self.triggers)}
"""
