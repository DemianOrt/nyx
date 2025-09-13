# Crear los clientes de API

# 1. Gemini Client
gemini_client = """\"\"\"
Cliente para Google Gemini API
\"\"\"

import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    \"\"\"
    Cliente para interactuar con Google Gemini API
    \"\"\"
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        logger.info("Gemini Client inicializado")
    
    async def analyze_query(self, query: str, user_id: str = 'anonymous') -> Dict[str, Any]:
        \"\"\"
        Analiza una consulta y determina qué acción tomar
        \"\"\"
        try:
            prompt = self._build_analysis_prompt(query)
            
            response = self.model.generate_content(prompt)
            
            # Intentar parsear como JSON estructurado
            try:
                structured_response = json.loads(response.text)
                return structured_response
            except json.JSONDecodeError:
                # Si no es JSON válido, tratar como respuesta de texto
                return {
                    'response': response.text,
                    'skill_required': False,
                    'type': 'text_response'
                }
                
        except Exception as e:
            logger.error(f"Error en Gemini API: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _build_analysis_prompt(self, query: str) -> str:
        \"\"\"
        Construye el prompt para análisis de consulta
        \"\"\"
        return f\"\"\"
Eres Nyx, un asistente personal inteligente. Analiza la siguiente consulta del usuario y determina qué acción tomar.

Consulta del usuario: "{query}"

Habilidades disponibles:
- calendar: Gestión de calendario (crear eventos, listar eventos, encontrar huecos libres)
- perplexity: Búsqueda web en tiempo real (para información actualizada)

Responde en formato JSON con la siguiente estructura:
{{
    "skill_required": boolean,
    "skill_name": "nombre_de_la_skill" o null,
    "structured_data": {{
        // Datos estructurados para la skill si es necesario
    }},
    "response": "respuesta directa si no se necesita skill",
    "type": "analysis_type",
    "confidence": float entre 0 y 1
}}

Si la consulta requiere información en tiempo real, datos actualizados, noticias, o facts verificables, usa skill "perplexity".
Si la consulta es sobre calendario, eventos, reuniones, o scheduling, usa skill "calendar".
Si es una conversación general, pregunta conceptual, o solicitud creativa, responde directamente sin usar skills.

Ejemplos:
- "¿Cuál es la capital de Francia?" -> respuesta directa (información básica)
- "¿Cuáles son las últimas noticias sobre AI?" -> skill: perplexity
- "Programa una reunión mañana a las 3pm" -> skill: calendar
- "Explícame qué es la programación" -> respuesta directa
\"\"\"
    
    async def generate_creative_content(self, prompt: str, context: Dict[str, Any] = None) -> str:
        \"\"\"
        Genera contenido creativo usando Gemini
        \"\"\"
        try:
            full_prompt = f\"\"\"
Eres Nyx, un asistente personal inteligente y creativo. 

Contexto: {json.dumps(context) if context else 'Sin contexto adicional'}

Solicitud: {prompt}

Responde de manera útil, creativa y personalizada.
\"\"\"
            
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generando contenido creativo: {e}")
            return f"Error generando respuesta: {str(e)}"
    
    async def structure_natural_language(self, text: str, target_format: str) -> Dict[str, Any]:
        \"\"\"
        Estructura lenguaje natural en formato específico
        \"\"\"
        try:
            prompt = f\"\"\"
Convierte el siguiente texto en lenguaje natural a {target_format}:

Texto: "{text}"

Responde solo con el JSON estructurado, sin explicaciones adicionales.
\"\"\"
            
            response = self.model.generate_content(prompt)
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {
                    'error': 'No se pudo estructurar la respuesta',
                    'raw_response': response.text
                }
                
        except Exception as e:
            logger.error(f"Error estructurando lenguaje natural: {e}")
            return {
                'error': str(e)
            }
"""

with open('nyx/clients/gemini_client.py', 'w') as f:
    f.write(gemini_client)

print("✅ Gemini Client creado")

# 2. Perplexity Client
perplexity_client = """\"\"\"
Cliente para Perplexity API
\"\"\"

import os
import json
import aiohttp
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class PerplexityClient:
    \"\"\"
    Cliente para interactuar con Perplexity API
    \"\"\"
    
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY no encontrada en variables de entorno")
        
        self.base_url = "https://api.perplexity.ai"
        self.model = "llama-3-sonar-small-32k-online"  # Modelo económico
        
        logger.info("Perplexity Client inicializado")
    
    async def search(self, query: str, user_id: str = 'anonymous') -> Dict[str, Any]:
        \"\"\"
        Realiza una búsqueda usando Perplexity API
        \"\"\"
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Eres un asistente de investigación. Proporciona respuestas precisas basadas en fuentes verificables y actualizadas.'
                    },
                    {
                        'role': 'user',
                        'content': query
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.2,
                'top_p': 0.9,
                'search_domain_filter': ["perplexity.ai"],
                'return_citations': True,
                'search_recency_filter': "month"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data)
                    
                    elif response.status == 429:
                        error_data = await response.json()
                        return {
                            'error': 'Rate limit exceeded',
                            'success': False,
                            'retry_after': response.headers.get('Retry-After'),
                            'details': error_data
                        }
                    
                    else:
                        error_text = await response.text()
                        return {
                            'error': f'API Error {response.status}: {error_text}',
                            'success': False
                        }
                        
        except Exception as e:
            logger.error(f"Error en Perplexity API: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Parsea la respuesta de Perplexity API
        \"\"\"
        try:
            message = data['choices'][0]['message']
            content = message.get('content', '')
            
            # Extraer citas si están disponibles
            citations = []
            if 'citations' in data:
                citations = data['citations']
            
            # Extraer fuentes del contenido si están marcadas
            sources = self._extract_sources(content)
            
            return {
                'answer': content,
                'sources': sources,
                'citations': citations,
                'usage': data.get('usage', {}),
                'success': True
            }
            
        except KeyError as e:
            logger.error(f"Error parseando respuesta de Perplexity: {e}")
            return {
                'error': f'Respuesta malformada: {str(e)}',
                'success': False,
                'raw_data': data
            }
    
    def _extract_sources(self, content: str) -> List[Dict[str, str]]:
        \"\"\"
        Extrae fuentes del contenido de la respuesta
        \"\"\"
        sources = []
        
        # Buscar patrones de URLs en el texto
        import re
        url_pattern = r'\\[(\\d+)\\]\\s*([^\\n]+)'
        matches = re.findall(url_pattern, content)
        
        for match in matches:
            sources.append({
                'id': match[0],
                'title': match[1].strip(),
                'url': ''  # Perplexity no siempre incluye URLs directas
            })
        
        return sources
    
    def estimate_cost(self, response: Dict[str, Any]) -> float:
        \"\"\"
        Estima el costo de una request basado en tokens usados
        \"\"\"
        if not response.get('success'):
            return 0.0
        
        usage = response.get('usage', {})
        
        # Precios aproximados de Perplexity (pueden cambiar)
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        # Precio por 1K tokens (aproximado)
        input_cost_per_1k = 0.002  # $0.002 por 1K input tokens
        output_cost_per_1k = 0.002  # $0.002 por 1K output tokens
        
        total_cost = (
            (input_tokens / 1000) * input_cost_per_1k +
            (output_tokens / 1000) * output_cost_per_1k
        )
        
        return round(total_cost, 6)
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        \"\"\"
        Obtiene estadísticas de uso de la API (si está disponible)
        \"\"\"
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/usage",  # Endpoint hipotético
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            'error': f'No se pudieron obtener estadísticas: {response.status}',
                            'success': False
                        }
                        
        except Exception:
            # Si el endpoint no existe, retornar datos vacíos
            return {
                'message': 'Estadísticas de uso no disponibles',
                'success': False
            }
"""

with open('nyx/clients/perplexity_client.py', 'w') as f:
    f.write(perplexity_client)

print("✅ Perplexity Client creado")

# 3. Budget Governor
budget_governor = """\"\"\"
Gobernador de presupuesto para Perplexity API
\"\"\"

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BudgetGovernor:
    \"\"\"
    Controla el gasto en la API de Perplexity con un límite estricto de $5/mes
    \"\"\"
    
    def __init__(self):
        self.budget_limit = float(os.getenv('PERPLEXITY_BUDGET_LIMIT', '5.00'))
        self.budget_file = Path(__file__).parent.parent / 'data' / 'budget.json'
        self.budget_file.parent.mkdir(exist_ok=True)
        
        self.current_usage = self._load_usage()
        
        logger.info(f"Budget Governor inicializado - Límite: ${self.budget_limit}")
    
    def _load_usage(self) -> Dict[str, Any]:
        \"\"\"
        Carga el uso actual desde el archivo
        \"\"\"
        if not self.budget_file.exists():
            return self._create_empty_usage()
        
        try:
            with open(self.budget_file, 'r') as f:
                data = json.load(f)
            
            # Verificar si es un nuevo mes
            last_reset = datetime.fromisoformat(data.get('last_reset', '2000-01-01'))
            if self._should_reset_budget(last_reset):
                logger.info("Nuevo período de facturación - reseteando presupuesto")
                return self._create_empty_usage()
            
            return data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error cargando presupuesto: {e}")
            return self._create_empty_usage()
    
    def _create_empty_usage(self) -> Dict[str, Any]:
        \"\"\"
        Crea un registro de uso vacío
        \"\"\"
        return {
            'total_spent': 0.0,
            'requests_count': 0,
            'last_reset': datetime.now().isoformat(),
            'transactions': []
        }
    
    def _should_reset_budget(self, last_reset: datetime) -> bool:
        \"\"\"
        Determina si se debe resetear el presupuesto (nuevo mes)
        \"\"\"
        now = datetime.now()
        
        # Si el último reset fue en un mes diferente
        return (
            last_reset.year != now.year or 
            last_reset.month != now.month
        )
    
    def _save_usage(self):
        \"\"\"
        Guarda el uso actual al archivo
        \"\"\"
        try:
            with open(self.budget_file, 'w') as f:
                json.dump(self.current_usage, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando presupuesto: {e}")
    
    def can_spend(self, estimated_cost: float = 0.01) -> bool:
        \"\"\"
        Verifica si se puede gastar una cantidad estimada
        \"\"\"
        current_spent = self.current_usage.get('total_spent', 0.0)
        projected_total = current_spent + estimated_cost
        
        # Dejar un margen de seguridad del 10%
        safety_limit = self.budget_limit * 0.9
        
        can_afford = projected_total <= safety_limit
        
        if not can_afford:
            logger.warning(
                f"Presupuesto insuficiente: ${current_spent:.4f} gastado, "
                f"${estimated_cost:.4f} requerido, límite: ${safety_limit:.4f}"
            )
        
        return can_afford
    
    def record_usage(self, cost: float, details: Optional[Dict[str, Any]] = None):
        \"\"\"
        Registra un gasto en la API
        \"\"\"
        if cost <= 0:
            return
        
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'cost': cost,
            'details': details or {}
        }
        
        self.current_usage['total_spent'] = round(
            self.current_usage.get('total_spent', 0.0) + cost, 6
        )
        self.current_usage['requests_count'] += 1
        self.current_usage['transactions'].append(transaction)
        
        # Mantener solo las últimas 100 transacciones
        if len(self.current_usage['transactions']) > 100:
            self.current_usage['transactions'] = self.current_usage['transactions'][-100:]
        
        self._save_usage()
        
        logger.info(f"Gasto registrado: ${cost:.4f} - Total: ${self.current_usage['total_spent']:.4f}")
        
        # Alertas de presupuesto
        self._check_budget_alerts()
    
    def _check_budget_alerts(self):
        \"\"\"
        Verifica y emite alertas de presupuesto
        \"\"\"
        spent = self.current_usage.get('total_spent', 0.0)
        percentage = (spent / self.budget_limit) * 100
        
        if percentage >= 90:
            logger.warning(f"⚠️  ALERTA: {percentage:.1f}% del presupuesto usado (${spent:.4f}/${self.budget_limit})")
        elif percentage >= 75:
            logger.info(f"📊 {percentage:.1f}% del presupuesto usado (${spent:.4f}/${self.budget_limit})")
    
    def get_budget_status(self) -> Dict[str, Any]:
        \"\"\"
        Retorna el estado actual del presupuesto
        \"\"\"
        spent = self.current_usage.get('total_spent', 0.0)
        remaining = max(0, self.budget_limit - spent)
        percentage_used = (spent / self.budget_limit) * 100
        
        return {
            'limit': self.budget_limit,
            'spent': spent,
            'remaining': remaining,
            'percentage_used': round(percentage_used, 2),
            'requests_count': self.current_usage.get('requests_count', 0),
            'last_reset': self.current_usage.get('last_reset'),
            'can_spend': self.can_spend(),
            'status': self._get_status_message(percentage_used)
        }
    
    def _get_status_message(self, percentage: float) -> str:
        \"\"\"
        Retorna un mensaje de estado basado en el porcentaje usado
        \"\"\"
        if percentage >= 100:
            return "PRESUPUESTO AGOTADO"
        elif percentage >= 90:
            return "CRÍTICO - Cerca del límite"
        elif percentage >= 75:
            return "ADVERTENCIA - Usar con precaución"
        elif percentage >= 50:
            return "MODERADO - Monitorear uso"
        else:
            return "SALUDABLE - Dentro del presupuesto"
    
    def reset_budget(self):
        \"\"\"
        Resetea manualmente el presupuesto (para testing)
        \"\"\"
        logger.info("Reseteando presupuesto manualmente")
        self.current_usage = self._create_empty_usage()
        self._save_usage()
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        \"\"\"
        Retorna las transacciones más recientes
        \"\"\"
        transactions = self.current_usage.get('transactions', [])
        return transactions[-limit:] if transactions else []
"""

with open('nyx/clients/budget_governor.py', 'w') as f:
    f.write(budget_governor)

print("✅ Budget Governor creado")

# 4. Calendar Client
calendar_client = """\"\"\"
Cliente para Google Calendar API
\"\"\"

import os
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class CalendarClient:
    \"\"\"
    Cliente para interactuar con Google Calendar API
    \"\"\"
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.credentials_file = Path(__file__).parent.parent / 'data' / 'credentials.json'
        self.token_file = Path(__file__).parent.parent / 'data' / 'token.pickle'
        self.service = None
        
        self._authenticate()
        
        logger.info("Calendar Client inicializado")
    
    def _authenticate(self):
        \"\"\"
        Maneja la autenticación OAuth 2.0
        \"\"\"
        creds = None
        
        # Cargar credenciales existentes
        if self.token_file.exists():
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales válidas, obtener nuevas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_file.exists():
                    raise FileNotFoundError(
                        f"Archivo de credenciales no encontrado: {self.credentials_file}\\n"
                        "Descarga el archivo client_secrets.json desde Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Guardar credenciales para futuros usos
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # Construir el servicio
        self.service = build('calendar', 'v3', credentials=creds)
    </f</CONTINUE_QUERY/>