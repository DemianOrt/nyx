# Crear el puente Python y los clientes de API

# 1. Archivo principal del puente Python
bridge_main = """#!/usr/bin/env python3
\"\"\"
Nyx Python Bridge - Puente de comunicación entre Node.js y Python
Maneja la lógica de IA y la ejecución de habilidades
\"\"\"

import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Añadir el directorio clients al path
sys.path.append(str(Path(__file__).parent.parent / 'clients'))

from src.skill_manager import SkillManager
from src.intent_classifier import IntentClassifier
from src.query_router import QueryRouter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/bridge.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NyxBridge:
    \"\"\"
    Puente principal de Nyx que maneja la comunicación con Node.js
    y ejecuta las habilidades correspondientes
    \"\"\"
    
    def __init__(self):
        self.skill_manager = SkillManager()
        self.intent_classifier = IntentClassifier()
        self.query_router = QueryRouter()
        
        logger.info("🐍 Nyx Python Bridge iniciado")
        
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Procesa una request del servidor Node.js
        \"\"\"
        try:
            request_type = request.get('type')
            request_id = request.get('requestId')
            
            logger.info(f"Procesando request: {request_type}")
            
            if request_type == 'query':
                response = await self.handle_query(request)
            elif request_type == 'list_skills':
                response = await self.handle_list_skills()
            else:
                response = {
                    'error': f'Tipo de request desconocido: {request_type}',
                    'success': False
                }
                
            response['requestId'] = request_id
            return response
            
        except Exception as e:
            logger.error(f"Error procesando request: {e}")
            return {
                'error': str(e),
                'success': False,
                'requestId': request.get('requestId')
            }
    
    async def handle_query(self, request: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Maneja una consulta del usuario
        \"\"\"
        message = request.get('message', '')
        user_id = request.get('userId', 'anonymous')
        
        # Enrutar la consulta a través del sistema de 3 niveles
        result = await self.query_router.route_query(message, user_id)
        
        return {
            'success': True,
            'data': result,
            'timestamp': request.get('timestamp')
        }
    
    async def handle_list_skills(self) -> Dict[str, Any]:
        \"\"\"
        Retorna la lista de habilidades disponibles
        \"\"\"
        skills = self.skill_manager.get_available_skills()
        
        return {
            'success': True,
            'data': {
                'skills': skills,
                'count': len(skills)
            }
        }
    
    async def run(self):
        \"\"\"
        Loop principal del puente
        \"\"\"
        logger.info("Bridge listo para recibir requests")
        
        while True:
            try:
                # Leer línea de stdin
                line = sys.stdin.readline()
                
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                # Parsear JSON
                request = json.loads(line)
                
                # Procesar request
                response = await self.process_request(request)
                
                # Enviar respuesta a stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON: {e}")
                error_response = {
                    'error': 'JSON malformado',
                    'success': False
                }
                print(json.dumps(error_response), flush=True)
                
            except KeyboardInterrupt:
                logger.info("Cerrando bridge...")
                break
                
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
                error_response = {
                    'error': str(e),
                    'success': False
                }
                print(json.dumps(error_response), flush=True)

if __name__ == '__main__':
    bridge = NyxBridge()
    asyncio.run(bridge.run())
"""

with open('nyx/bridge/main.py', 'w') as f:
    f.write(bridge_main)

print("✅ Puente Python principal creado")

# 2. Skill Manager
skill_manager = """\"\"\"
Gestor de habilidades de Nyx
\"\"\"

import json
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SkillManager:
    \"\"\"
    Maneja la carga, descubrimiento y ejecución de habilidades
    \"\"\"
    
    def __init__(self):
        self.skills = {}
        self.skills_path = Path(__file__).parent.parent.parent / 'skills'
        self.load_skills()
    
    def load_skills(self):
        \"\"\"
        Descubre y carga todas las habilidades disponibles
        \"\"\"
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
        \"\"\"
        Carga una habilidad específica
        \"\"\"
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
        \"\"\"
        Retorna la lista de habilidades disponibles
        \"\"\"
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
        \"\"\"
        Ejecuta una habilidad específica
        \"\"\"
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
        \"\"\"
        Encuentra una skill basada en triggers de palabras clave
        \"\"\"
        query_lower = query.lower()
        
        for skill_name, skill_data in self.skills.items():
            triggers = skill_data['config'].get('triggers', [])
            
            for trigger in triggers:
                if trigger.lower() in query_lower:
                    return skill_name
        
        return None
"""

with open('nyx/bridge/src/skill_manager.py', 'w') as f:
    f.write(skill_manager)

print("✅ Skill Manager creado")

# 3. Intent Classifier
intent_classifier = """\"\"\"
Clasificador de intenciones de nivel 1 (local)
\"\"\"

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
    \"\"\"
    Clasificador simple basado en palabras clave y patrones
    \"\"\"
    
    def __init__(self):
        self.patterns = {
            'calendar': [
                r'\\b(calendario|evento|reunión|cita|agenda|meeting)\\b',
                r'\\b(programar|agendar|crear evento)\\b',
                r'\\b(mañana|hoy|semana|mes)\\b.*\\b(libre|ocupado)\\b'
            ],
            'search': [
                r'\\b(buscar|qué es|quién es|cuál es)\\b',
                r'\\b(noticias|información|datos)\\b.*\\bsobre\\b',
                r'^(qué|quién|cuál|cuándo|dónde|cómo|por qué)'
            ],
            'weather': [
                r'\\b(clima|tiempo|temperatura)\\b',
                r'\\b(lluvia|sol|nublado|frío|calor)\\b'
            ],
            'general': [
                r'\\b(hola|hi|hello|buenos días|buenas tardes)\\b',
                r'\\b(ayuda|help|commands|comandos)\\b'
            ]
        }
        
        self.confidence_weights = {
            'exact_match': 1.0,
            'partial_match': 0.7,
            'context_match': 0.5
        }
    
    def classify(self, query: str) -> Tuple[Optional[str], float]:
        \"\"\"
        Clasifica una consulta y retorna la intención más probable con confianza
        \"\"\"
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
        \"\"\"
        Calcula la confianza de un intent basado en patrones
        \"\"\"
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
        \"\"\"
        Añade un nuevo patrón para un intent
        \"\"\"
        if intent not in self.patterns:
            self.patterns[intent] = []
        
        self.patterns[intent].append(pattern)
        logger.info(f"Patrón añadido para {intent}: {pattern}")
    
    def get_supported_intents(self) -> List[str]:
        \"\"\"
        Retorna la lista de intenciones soportadas
        \"\"\"
        return list(self.patterns.keys())
"""

with open('nyx/bridge/src/intent_classifier.py', 'w') as f:
    f.write(intent_classifier)

print("✅ Intent Classifier creado")

# 4. Query Router (sistema de 3 niveles)
query_router = """\"\"\"
Router de consultas - Sistema de enrutamiento de 3 niveles
\"\"\"

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
    \"\"\"
    Enrutador de consultas que implementa el sistema de 3 niveles:
    1. Clasificación local de intenciones
    2. Razonamiento avanzado (Gemini)
    3. Búsqueda web en tiempo real (Perplexity)
    \"\"\"
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.skill_manager = SkillManager()
        self.gemini_client = GeminiClient()
        self.perplexity_client = PerplexityClient()
        self.budget_governor = BudgetGovernor()
        
        logger.info("Query Router inicializado")
    
    async def route_query(self, query: str, user_id: str = 'anonymous') -> Dict[str, Any]:
        \"\"\"
        Enruta una consulta a través del sistema de 3 niveles
        \"\"\"
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
        \"\"\"
        Maneja consultas del Nivel 1 (clasificación local)
        \"\"\"
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
        \"\"\"
        Maneja consultas del Nivel 2 (Gemini para razonamiento)
        \"\"\"
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
        \"\"\"
        Maneja consultas del Nivel 3 (Perplexity para búsqueda web)
        \"\"\"
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
        \"\"\"
        Determina si una consulta necesita búsqueda web
        \"\"\"
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
        \"\"\"
        Mapea una intención a una skill específica
        \"\"\"
        mapping = {
            'calendar': 'calendar',
            'search': None,  # Se maneja en nivel 3
            'weather': None,  # Se maneja en nivel 3
            'general': None   # Se maneja en nivel 2
        }
        
        return mapping.get(intent)
"""

with open('nyx/bridge/src/query_router.py', 'w') as f:
    f.write(query_router)

print("✅ Query Router creado")

# 5. requirements.txt del bridge
bridge_requirements = """# APIs de IA
google-generativeai>=0.3.2
google-auth>=2.23.4
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.108.0

# HTTP y requests
aiohttp>=3.9.1
requests>=2.31.0

# Utilidades
python-dotenv>=1.0.0
asyncio>=3.4.3
typing>=3.7.4

# Logging y desarrollo
colorlog>=6.8.0
"""

with open('nyx/bridge/requirements.txt', 'w') as f:
    f.write(bridge_requirements)

print("✅ requirements.txt del bridge creado")

print("\n🐍 Puente Python y componentes principales creados exitosamente")