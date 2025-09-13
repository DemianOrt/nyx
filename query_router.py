"""
Router de consultas - Sistema de enrutamiento de 3 niveles
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Añadir clients al path
sys.path.append(str(Path(__file__).parent.parent.parent / 'clients'))

from intent_classifier import IntentClassifier
from skill_manager import SkillManager
from gemini_client import GeminiClient
from perplexity_client import PerplexityClient
from budget_governor import BudgetGovernor

logger = logging.getLogger(__name__)

class QueryRouter:
    """
    Enrutador de consultas que implementa el sistema de 3 niveles:
    1. Clasificación local de intenciones
    2. Razonamiento avanzado (Gemini)
    3. Búsqueda web en tiempo real (Perplexity)
    """

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.skill_manager = SkillManager()
        self.gemini_client = GeminiClient()
        self.perplexity_client = PerplexityClient()
        self.budget_governor = BudgetGovernor()

        logger.info("Query Router inicializado")

    async def route_query(self, query: str, user_id: str = 'anonymous') -> Dict[str, Any]:
        """
        Enruta una consulta a través del sistema de 3 niveles
        """
        try:
            # Nivel 1: Clasificación local de intenciones
            intent, confidence = self.intent_classifier.classify(query)

            if intent and confidence >= 0.8:
                logger.info(f"Nivel 1: Intent {intent} detectado con alta confianza")
                return await self._handle_level1(query, intent, user_id)

            # Nivel 2: Determinar si necesita razonamiento o búsqueda web
            needs_web_search = self._needs_web_search(query)

            if needs_web_search:
                logger.info("Nivel 3: Consulta requiere búsqueda web")
                return await self._handle_level3(query, user_id)
            else:
                logger.info("Nivel 2: Consulta requiere razonamiento avanzado")
                return await self._handle_level2(query, user_id)

        except Exception as e:
            logger.error(f"Error en routing: {e}")
            return {
                'error': str(e),
                'success': False,
                'level': 'error'
            }

    async def _handle_level1(self, query: str, intent: str, user_id: str) -> Dict[str, Any]:
        """
        Maneja consultas del Nivel 1 (clasificación local)
        """
        # Buscar skill que maneje este intent
        skill_name = self._map_intent_to_skill(intent)

        if skill_name:
            context = {
                'user_id': user_id,
                'intent': intent,
                'level': 1
            }

            result = self.skill_manager.execute_skill(skill_name, query, context)
            result['level'] = 1
            result['method'] = 'local_classification'

            return result

        # Si no hay skill disponible, pasar al nivel 2
        return await self._handle_level2(query, user_id)

    async def _handle_level2(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Maneja consultas del Nivel 2 (Gemini para razonamiento)
        """
        try:
            response = await self.gemini_client.analyze_query(query, user_id)

            # Si Gemini identifica que necesita ejecutar una skill
            if response.get('skill_required'):
                skill_name = response.get('skill_name')
                structured_data = response.get('structured_data', {})

                if skill_name:
                    context = {
                        'user_id': user_id,
                        'level': 2,
                        'gemini_analysis': response,
                        'structured_data': structured_data
                    }

                    result = self.skill_manager.execute_skill(skill_name, query, context)
                    result['level'] = 2
                    result['method'] = 'gemini_reasoning'
                    result['analysis'] = response

                    return result

            # Respuesta directa de Gemini
            return {
                'success': True,
                'level': 2,
                'method': 'gemini_direct',
                'result': {
                    'response': response.get('response', ''),
                    'type': 'text',
                    'analysis': response
                }
            }

        except Exception as e:
            logger.error(f"Error en Nivel 2: {e}")
            return {
                'error': str(e),
                'success': False,
                'level': 2
            }

    async def _handle_level3(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Maneja consultas del Nivel 3 (Perplexity para búsqueda web)
        """
        try:
            # Verificar presupuesto
            if not self.budget_governor.can_spend():
                return {
                    'error': 'Presupuesto de búsqueda web agotado',
                    'success': False,
                    'level': 3,
                    'budget_exceeded': True
                }

            response = await self.perplexity_client.search(query, user_id)

            # Registrar gasto en el presupuesto
            estimated_cost = self.perplexity_client.estimate_cost(response)
            self.budget_governor.record_usage(estimated_cost)

            return {
                'success': True,
                'level': 3,
                'method': 'perplexity_search',
                'result': {
                    'response': response.get('answer', ''),
                    'sources': response.get('sources', []),
                    'type': 'search_result',
                    'cost': estimated_cost
                }
            }

        except Exception as e:
            logger.error(f"Error en Nivel 3: {e}")
            return {
                'error': str(e),
                'success': False,
                'level': 3
            }

    def _needs_web_search(self, query: str) -> bool:
        """
        Determina si una consulta necesita búsqueda web
        """
        web_indicators = [
            'qué es', 'quién es', 'cuál es',
            'noticias', 'último', 'reciente',
            'información sobre', 'datos de',
            'precio de', 'cotización',
            'weather in', 'clima en',
            'latest', 'news about'
        ]

        query_lower = query.lower()

        return any(indicator in query_lower for indicator in web_indicators)

    def _map_intent_to_skill(self, intent: str) -> Optional[str]:
        """
        Mapea una intención a una skill específica
        """
        mapping = {
            'calendar': 'calendar',
            'search': None,  # Se maneja en nivel 3
            'weather': None,  # Se maneja en nivel 3
            'general': None   # Se maneja en nivel 2
        }

        return mapping.get(intent)
