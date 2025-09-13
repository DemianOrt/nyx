# Crear las habilidades (skills) 

# 1. Skill base para todas las habilidades
skill_base = '''"""
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
'''

with open('nyx/clients/skill_base.py', 'w') as f:
    f.write(skill_base)

print("✅ Skill base creada")

# 2. Calendar Skill
calendar_skill_json = {
    "name": "calendar",
    "version": "0.1.0",
    "description": "Gestión de calendario de Google - crear eventos, listar eventos, encontrar huecos libres",
    "author": "Nyx Team",
    "class": "CalendarSkill",
    "triggers": [
        "calendario", "evento", "reunión", "cita", "agenda", "meeting",
        "programar", "agendar", "crear evento", "schedule",
        "libre", "ocupado", "disponible", "available", "busy"
    ],
    "required_apis": ["google_calendar"],
    "config_schema": {
        "timezone": "UTC",
        "default_duration_minutes": 60,
        "working_hours": {
            "start": "09:00",
            "end": "17:00"
        }
    }
}

with open('nyx/skills/calendar/skill.json', 'w') as f:
    json.dump(calendar_skill_json, f, indent=2)

calendar_skill_main = '''"""
Habilidad de gestión de calendario
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import re

# Añadir clients al path
sys.path.append(str(Path(__file__).parent.parent.parent / 'clients'))

from skill_base import Skill
from calendar_client import CalendarClient

class CalendarSkill(Skill):
    """
    Habilidad para gestionar el calendario de Google
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.calendar_client = CalendarClient()
        
        # Configuración por defecto
        self.default_duration = self.config.get('config_schema', {}).get('default_duration_minutes', 60)
        self.timezone = self.config.get('config_schema', {}).get('timezone', 'UTC')
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la habilidad de calendario
        """
        if not self.validate_input(query, context):
            return {
                'success': False,
                'error': 'Consulta inválida'
            }
        
        # Determinar acción basada en la consulta
        action = self._determine_action(query, context)
        
        if action == 'list_events':
            return self._list_events(query, context)
        elif action == 'create_event':
            return self._create_event(query, context)
        elif action == 'find_free_slots':
            return self._find_free_slots(query, context)
        else:
            return self._general_calendar_help()
    
    def _determine_action(self, query: str, context: Dict[str, Any]) -> str:
        """
        Determina qué acción realizar basada en la consulta
        """
        query_lower = query.lower()
        
        # Si viene del nivel 2 (Gemini), usar datos estructurados
        if context.get('level') == 2 and context.get('structured_data'):
            structured_data = context['structured_data']
            if 'intent' in structured_data:
                return structured_data['intent']
        
        # Clasificación simple basada en palabras clave
        if any(word in query_lower for word in ['crear', 'programar', 'agendar', 'schedule', 'create']):
            return 'create_event'
        elif any(word in query_lower for word in ['libre', 'disponible', 'hueco', 'free', 'available']):
            return 'find_free_slots'
        elif any(word in query_lower for word in ['listar', 'mostrar', 'próximos', 'eventos', 'list', 'show']):
            return 'list_events'
        else:
            return 'list_events'  # Por defecto
    
    def _list_events(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lista eventos del calendario
        """
        try:
            # Extraer rango de tiempo de la consulta
            time_range = self._extract_time_range(query)
            
            result = self.calendar_client.list_events(
                time_min=time_range.get('start'),
                time_max=time_range.get('end'),
                max_results=10
            )
            
            if not result['success']:
                return {
                    'success': False,
                    'error': f"Error accediendo al calendario: {result['error']}"
                }
            
            events = result['events']
            
            if not events:
                response = "No tienes eventos programados en el período consultado."
            else:
                response = self._format_events_list(events)
            
            return self.format_response(response, 'calendar_events')
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error listando eventos: {str(e)}"
            }
    
    def _create_event(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo evento
        """
        try:
            # Extraer detalles del evento
            event_details = self._extract_event_details(query, context)
            
            if not event_details.get('title'):
                return {
                    'success': False,
                    'error': 'No se pudo extraer el título del evento'
                }
            
            if not event_details.get('start_time'):
                return {
                    'success': False,
                    'error': 'No se pudo determinar la fecha/hora del evento'
                }
            
            result = self.calendar_client.create_event(
                title=event_details['title'],
                start_time=event_details['start_time'],
                end_time=event_details.get('end_time') or 
                         event_details['start_time'] + timedelta(minutes=self.default_duration),
                description=event_details.get('description', ''),
                attendees=event_details.get('attendees', [])
            )
            
            if not result['success']:
                return {
                    'success': False,
                    'error': f"Error creando evento: {result['error']}"
                }
            
            response = f"✅ Evento creado: {result['event']['title']}\\n"
            response += f"📅 Fecha: {result['event']['start']}\\n"
            if result.get('html_link'):
                response += f"🔗 Link: {result['html_link']}"
            
            return self.format_response(response, 'event_created')
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error creando evento: {str(e)}"
            }
    
    def _find_free_slots(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encuentra huecos libres en el calendario
        """
        try:
            # Extraer duración y rango de tiempo
            duration = self._extract_duration(query) or self.default_duration
            time_range = self._extract_time_range(query)
            
            result = self.calendar_client.find_free_slots(
                duration_minutes=duration,
                time_min=time_range.get('start'),
                time_max=time_range.get('end')
            )
            
            if not result['success']:
                return {
                    'success': False,
                    'error': f"Error buscando huecos libres: {result['error']}"
                }
            
            free_slots = result['free_slots']
            
            if not free_slots:
                response = f"No encontré huecos libres de {duration} minutos en el período consultado."
            else:
                response = self._format_free_slots(free_slots, duration)
            
            return self.format_response(response, 'free_slots')
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error buscando huecos libres: {str(e)}"
            }
    
    def _extract_time_range(self, query: str) -> Dict[str, Optional[datetime]]:
        """
        Extrae rango de tiempo de la consulta
        """
        now = datetime.utcnow()
        
        # Patrones simples
        if 'hoy' in query.lower() or 'today' in query.lower():
            return {
                'start': now,
                'end': now.replace(hour=23, minute=59)
            }
        elif 'mañana' in query.lower() or 'tomorrow' in query.lower():
            tomorrow = now + timedelta(days=1)
            return {
                'start': tomorrow.replace(hour=0, minute=0),
                'end': tomorrow.replace(hour=23, minute=59)
            }
        elif 'semana' in query.lower() or 'week' in query.lower():
            return {
                'start': now,
                'end': now + timedelta(days=7)
            }
        else:
            # Por defecto: próximos 7 días
            return {
                'start': now,
                'end': now + timedelta(days=7)
            }
    
    def _extract_duration(self, query: str) -> Optional[int]:
        """
        Extrae duración en minutos de la consulta
        """
        # Buscar patrones como "30 minutos", "1 hora", etc.
        duration_patterns = [
            r'(\\d+)\\s*(?:minuto|minutos|min)',
            r'(\\d+)\\s*(?:hora|horas|hr|h)',
            r'(\\d+)\\s*(?:minutes?)',
            r'(\\d+)\\s*(?:hours?)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, query.lower())
            if match:
                number = int(match.group(1))
                if 'hora' in pattern or 'hour' in pattern:
                    return number * 60
                else:
                    return number
        
        return None
    
    def _extract_event_details(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae detalles del evento de la consulta
        """
        details = {}
        
        # Si viene del nivel 2 con datos estructurados
        if context.get('level') == 2 and context.get('structured_data'):
            structured_data = context['structured_data']
            details.update(structured_data)
        
        # Extracción simple basada en patrones
        # Esto sería mucho más sofisticado en una implementación completa
        
        # Título (simplificado)
        if not details.get('title'):
            # Intentar extraer después de palabras como "reunión", "evento"
            title_patterns = [
                r'(?:reunión|evento|meeting|cita)\\s+(?:con|para|de|about)\\s+(.+?)(?:\\s+(?:mañana|hoy|el|at|on)|$)',
                r'"([^"]+)"',
                r'llamada\\s+(.+?)(?:\\s+(?:mañana|hoy|el|at|on)|$)'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    details['title'] = match.group(1).strip()
                    break
            
            if not details.get('title'):
                details['title'] = "Evento sin título"
        
        # Tiempo (simplificado - solo mañana por ahora)
        if not details.get('start_time'):
            now = datetime.utcnow()
            
            if 'mañana' in query.lower() or 'tomorrow' in query.lower():
                # Buscar hora específica
                time_match = re.search(r'(\\d{1,2})(?::(\\d{2}))?\\s*(?:am|pm|h)?', query.lower())
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2) or 0)
                    
                    tomorrow = now + timedelta(days=1)
                    details['start_time'] = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    # Hora por defecto: 10:00 AM
                    tomorrow = now + timedelta(days=1)
                    details['start_time'] = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        return details
    
    def _format_events_list(self, events: List[Dict[str, Any]]) -> str:
        """
        Formatea una lista de eventos
        """
        response = f"📅 Tienes {len(events)} evento(s) programado(s):\\n\\n"
        
        for i, event in enumerate(events, 1):
            start_time = event['start']
            title = event['title']
            
            response += f"{i}. **{title}**\\n"
            response += f"   🕒 {start_time}\\n"
            
            if event.get('location'):
                response += f"   📍 {event['location']}\\n"
            
            response += "\\n"
        
        return response
    
    def _format_free_slots(self, slots: List[Dict[str, Any]], duration: int) -> str:
        """
        Formatea huecos libres
        """
        response = f"🆓 Encontré {len(slots)} hueco(s) libre(s) de {duration} minutos:\\n\\n"
        
        for i, slot in enumerate(slots, 1):
            start = slot['start']
            end = slot['end']
            duration_available = slot['duration_minutes']
            
            response += f"{i}. {start} - {end}\\n"
            response += f"   ⏱️ Duración disponible: {duration_available} minutos\\n\\n"
        
        return response
    
    def _general_calendar_help(self) -> Dict[str, Any]:
        """
        Ayuda general sobre la habilidad de calendario
        """
        help_text = """
📅 **Habilidad de Calendario**

Puedes pedirme:
• **Listar eventos**: "Muestra mis próximos eventos", "¿Qué tengo hoy?"
• **Crear eventos**: "Programa una reunión mañana a las 3pm", "Crear evento llamada con cliente"
• **Encontrar huecos libres**: "¿Cuándo tengo libre?", "Busca un hueco de 1 hora esta semana"

Ejemplos:
- "¿Qué eventos tengo mañana?"
- "Programa una reunión con Ana el viernes a las 2pm"
- "¿Tengo algún hueco libre de 30 minutos hoy?"
"""
        
        return self.format_response(help_text, 'help')
'''

with open('nyx/skills/calendar/main.py', 'w') as f:
    f.write(calendar_skill_main)

calendar_requirements = '''google-auth>=2.23.4
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.108.0
'''

with open('nyx/skills/calendar/requirements.txt', 'w') as f:
    f.write(calendar_requirements)

print("✅ Calendar Skill creada")

print("\n📋 Habilidades (Skills) creadas exitosamente")