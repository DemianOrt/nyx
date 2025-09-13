# Completar el Calendar Client

calendar_client = '''"""
Cliente para Google Calendar API
"""

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
    """
    Cliente para interactuar con Google Calendar API
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.credentials_file = Path(__file__).parent.parent / 'data' / 'client_secrets.json'
        self.token_file = Path(__file__).parent.parent / 'data' / 'token.pickle'
        self.service = None
        
        self._authenticate()
        
        logger.info("Calendar Client inicializado")
    
    def _authenticate(self):
        """
        Maneja la autenticación OAuth 2.0
        """
        creds = None
        
        # Cargar credenciales existentes
        if self.token_file.exists():
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales válidas, obtener nuevas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refrescando token: {e}")
                    creds = None
            
            if not creds:
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
    
    def list_events(self, time_min: Optional[datetime] = None, 
                   time_max: Optional[datetime] = None, 
                   max_results: int = 10) -> Dict[str, Any]:
        """
        Lista eventos del calendario
        """
        try:
            if not time_min:
                time_min = datetime.utcnow()
            
            if not time_max:
                time_max = time_min + timedelta(days=7)
            
            # Convertir a formato ISO
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min_str,
                timeMax=time_max_str,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                formatted_events.append(self._format_event(event))
            
            return {
                'success': True,
                'events': formatted_events,
                'count': len(formatted_events)
            }
            
        except HttpError as e:
            logger.error(f"Error listando eventos: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_event(self, title: str, start_time: datetime, 
                    end_time: datetime, description: str = '',
                    attendees: List[str] = None) -> Dict[str, Any]:
        """
        Crea un nuevo evento en el calendario
        """
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                }
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'success': True,
                'event': self._format_event(created_event),
                'event_id': created_event['id'],
                'html_link': created_event.get('htmlLink')
            }
            
        except HttpError as e:
            logger.error(f"Error creando evento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def find_free_slots(self, duration_minutes: int, 
                       time_min: Optional[datetime] = None,
                       time_max: Optional[datetime] = None,
                       attendees: List[str] = None) -> Dict[str, Any]:
        """
        Encuentra huecos libres en el calendario
        """
        try:
            if not time_min:
                time_min = datetime.utcnow()
            
            if not time_max:
                time_max = time_min + timedelta(days=7)
            
            # Obtener eventos existentes
            events_response = self.list_events(time_min, time_max, max_results=100)
            
            if not events_response['success']:
                return events_response
            
            events = events_response['events']
            
            # Encontrar huecos libres
            free_slots = self._calculate_free_slots(
                events, time_min, time_max, duration_minutes
            )
            
            return {
                'success': True,
                'free_slots': free_slots,
                'count': len(free_slots),
                'duration_minutes': duration_minutes
            }
            
        except Exception as e:
            logger.error(f"Error encontrando huecos libres: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea un evento de Google Calendar
        """
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        return {
            'id': event['id'],
            'title': event.get('summary', 'Sin título'),
            'description': event.get('description', ''),
            'start': start,
            'end': end,
            'location': event.get('location', ''),
            'attendees': [
                attendee.get('email') 
                for attendee in event.get('attendees', [])
            ],
            'html_link': event.get('htmlLink'),
            'status': event.get('status')
        }
    
    def _calculate_free_slots(self, events: List[Dict[str, Any]], 
                             time_min: datetime, time_max: datetime,
                             duration_minutes: int) -> List[Dict[str, Any]]:
        """
        Calcula los huecos libres entre eventos
        """
        # Convertir eventos a lista de intervalos ocupados
        busy_intervals = []
        
        for event in events:
            try:
                start_str = event['start']
                end_str = event['end']
                
                # Manejar diferentes formatos de fecha/hora
                if 'T' in start_str:
                    start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                else:
                    # Evento de todo el día
                    start = datetime.fromisoformat(start_str)
                    end = datetime.fromisoformat(end_str)
                
                busy_intervals.append((start, end))
                
            except Exception as e:
                logger.warning(f"Error procesando evento: {e}")
                continue
        
        # Ordenar intervalos por hora de inicio
        busy_intervals.sort(key=lambda x: x[0])
        
        # Encontrar huecos libres
        free_slots = []
        current_time = time_min
        
        for start, end in busy_intervals:
            # Si hay un hueco antes del próximo evento
            if current_time < start:
                gap_duration = (start - current_time).total_seconds() / 60
                
                if gap_duration >= duration_minutes:
                    free_slots.append({
                        'start': current_time.isoformat(),
                        'end': start.isoformat(),
                        'duration_minutes': int(gap_duration)
                    })
            
            current_time = max(current_time, end)
        
        # Verificar hueco al final
        if current_time < time_max:
            final_gap = (time_max - current_time).total_seconds() / 60
            
            if final_gap >= duration_minutes:
                free_slots.append({
                    'start': current_time.isoformat(),
                    'end': time_max.isoformat(),
                    'duration_minutes': int(final_gap)
                })
        
        return free_slots
'''

with open('nyx/clients/calendar_client.py', 'w') as f:
    f.write(calendar_client)

print("✅ Calendar Client creado")

# 5. __init__.py para clients
clients_init = '''"""
Clientes de API para Nyx
"""

from .gemini_client import GeminiClient
from .perplexity_client import PerplexityClient
from .calendar_client import CalendarClient
from .budget_governor import BudgetGovernor

__all__ = [
    'GeminiClient',
    'PerplexityClient', 
    'CalendarClient',
    'BudgetGovernor'
]
'''

with open('nyx/clients/__init__.py', 'w') as f:
    f.write(clients_init)

print("✅ __init__.py de clients creado")

print("\n🔌 Clientes de API creados exitosamente")