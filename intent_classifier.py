"""
Clasificador de intenciones de nivel 1 (local)
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
    """
    Clasificador simple basado en palabras clave y patrones
    """

    def __init__(self):
        self.patterns = {
            'calendar': [
                r'\b(calendario|evento|reunión|cita|agenda|meeting)\b',
                r'\b(programar|agendar|crear evento)\b',
                r'\b(mañana|hoy|semana|mes)\b.*\b(libre|ocupado)\b'
            ],
            'search': [
                r'\b(buscar|qué es|quién es|cuál es)\b',
                r'\b(noticias|información|datos)\b.*\bsobre\b',
                r'^(qué|quién|cuál|cuándo|dónde|cómo|por qué)'
            ],
            'weather': [
                r'\b(clima|tiempo|temperatura)\b',
                r'\b(lluvia|sol|nublado|frío|calor)\b'
            ],
            'general': [
                r'\b(hola|hi|hello|buenos días|buenas tardes)\b',
                r'\b(ayuda|help|commands|comandos)\b'
            ]
        }

        self.confidence_weights = {
            'exact_match': 1.0,
            'partial_match': 0.7,
            'context_match': 0.5
        }

    def classify(self, query: str) -> Tuple[Optional[str], float]:
        """
        Clasifica una consulta y retorna la intención más probable con confianza
        """
        query_clean = query.lower().strip()

        if not query_clean:
            return None, 0.0

        best_intent = None
        best_confidence = 0.0

        for intent, patterns in self.patterns.items():
            confidence = self._calculate_confidence(query_clean, patterns)

            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent

        # Solo retornar si la confianza es suficientemente alta
        if best_confidence >= 0.5:
            logger.info(f"Intent clasificado: {best_intent} (confianza: {best_confidence:.2f})")
            return best_intent, best_confidence

        logger.info(f"No se pudo clasificar con confianza: {query[:50]}...")
        return None, best_confidence

    def _calculate_confidence(self, query: str, patterns: List[str]) -> float:
        """
        Calcula la confianza de un intent basado en patrones
        """
        total_confidence = 0.0
        matches = 0

        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                matches += 1
                # Diferentes pesos según el tipo de match
                if len(re.findall(pattern, query, re.IGNORECASE)) > 1:
                    total_confidence += self.confidence_weights['exact_match']
                else:
                    total_confidence += self.confidence_weights['partial_match']

        # Normalizar por el número de patrones
        if matches > 0:
            normalized_confidence = total_confidence / len(patterns)
            return min(normalized_confidence, 1.0)

        return 0.0

    def add_pattern(self, intent: str, pattern: str):
        """
        Añade un nuevo patrón para un intent
        """
        if intent not in self.patterns:
            self.patterns[intent] = []

        self.patterns[intent].append(pattern)
        logger.info(f"Patrón añadido para {intent}: {pattern}")

    def get_supported_intents(self) -> List[str]:
        """
        Retorna la lista de intenciones soportadas
        """
        return list(self.patterns.keys())
