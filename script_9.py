# Crear Perplexity Skill y archivos de Docker

# 1. Perplexity Skill
perplexity_skill_json = {
    "name": "perplexity",
    "version": "0.1.0", 
    "description": "Búsqueda web en tiempo real usando Perplexity API - información actualizada con fuentes verificables",
    "author": "Nyx Team",
    "class": "PerplexitySkill",
    "triggers": [
        "buscar", "qué es", "quién es", "cuál es", "search", "what is", "who is",
        "noticias", "news", "información", "information", "datos", "data",
        "último", "latest", "reciente", "recent", "actual", "current"
    ],
    "required_apis": ["perplexity"],
    "config_schema": {
        "max_tokens": 1000,
        "temperature": 0.2,
        "model": "llama-3-sonar-small-32k-online"
    }
}

with open('nyx/skills/perplexity/skill.json', 'w') as f:
    json.dump(perplexity_skill_json, f, indent=2)

perplexity_skill_main = '''"""
Habilidad de búsqueda web usando Perplexity API
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import re

# Añadir clients al path
sys.path.append(str(Path(__file__).parent.parent.parent / 'clients'))

from skill_base import Skill
from perplexity_client import PerplexityClient
from budget_governor import BudgetGovernor

class PerplexitySkill(Skill):
    """
    Habilidad para búsqueda web en tiempo real con Perplexity
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.perplexity_client = PerplexityClient()
        self.budget_governor = BudgetGovernor()
        
        # Configuración por defecto
        self.max_tokens = self.config.get('config_schema', {}).get('max_tokens', 1000)
        self.temperature = self.config.get('config_schema', {}).get('temperature', 0.2)
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta búsqueda web usando Perplexity
        """
        if not self.validate_input(query, context):
            return {
                'success': False,
                'error': 'Consulta inválida'
            }
        
        # Verificar presupuesto antes de realizar la búsqueda
        if not self.budget_governor.can_spend():
            budget_status = self.budget_governor.get_budget_status()
            return {
                'success': False,
                'error': 'Presupuesto de búsqueda web agotado para este mes',
                'budget_status': budget_status,
                'type': 'budget_exceeded'
            }
        
        return self._perform_search(query, context)
    
    def _perform_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza la búsqueda web
        """
        try:
            # Optimizar la consulta para búsqueda
            optimized_query = self._optimize_query(query)
            
            # Realizar búsqueda
            result = await self.perplexity_client.search(
                optimized_query, 
                context.get('user_id', 'anonymous')
            )
            
            if not result.get('success'):
                return {
                    'success': False,
                    'error': f"Error en búsqueda: {result.get('error', 'Error desconocido')}"
                }
            
            # Registrar gasto en presupuesto
            estimated_cost = self.perplexity_client.estimate_cost(result)
            self.budget_governor.record_usage(
                estimated_cost, 
                {'query': query[:100], 'tokens': result.get('usage', {})}
            )
            
            # Formatear respuesta
            response = self._format_search_response(result, query)
            
            return self.format_response(response, 'search_result')
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error realizando búsqueda: {str(e)}"
            }
    
    def _optimize_query(self, query: str) -> str:
        """
        Optimiza la consulta para mejores resultados de búsqueda
        """
        # Limpiar consulta
        query = query.strip()
        
        # Añadir contexto temporal si es relevante
        temporal_keywords = ['último', 'reciente', 'actual', 'latest', 'recent', 'current']
        
        if any(keyword in query.lower() for keyword in temporal_keywords):
            if not any(year in query for year in ['2024', '2023', '2025']):
                query += " 2024"
        
        # Mejorar consultas muy cortas
        if len(query.split()) <= 2:
            if '?' not in query:
                query = f"¿Qué es {query}?"
        
        return query
    
    def _format_search_response(self, result: Dict[str, Any], original_query: str) -> str:
        """
        Formatea la respuesta de búsqueda
        """
        response = "🔍 **Búsqueda Web**\\n\\n"
        
        # Respuesta principal
        answer = result.get('answer', '')
        if answer:
            response += f"{answer}\\n\\n"
        
        # Fuentes
        sources = result.get('sources', [])
        if sources:
            response += "📚 **Fuentes:**\\n"
            for i, source in enumerate(sources[:5], 1):  # Máximo 5 fuentes
                title = source.get('title', f'Fuente {i}')
                url = source.get('url', '')
                
                if url:
                    response += f"{i}. [{title}]({url})\\n"
                else:
                    response += f"{i}. {title}\\n"
        
        # Información sobre el costo (solo para debug)
        usage = result.get('usage', {})
        if usage:
            tokens_used = usage.get('total_tokens', 0)
            response += f"\\n💡 *Tokens utilizados: {tokens_used}*"
        
        # Estado del presupuesto si está cerca del límite
        budget_status = self.budget_governor.get_budget_status()
        if budget_status['percentage_used'] >= 75:
            response += f"\\n⚠️ *Presupuesto de búsqueda: {budget_status['percentage_used']:.1f}% utilizado*"
        
        return response
    
    def _categorize_query_type(self, query: str) -> str:
        """
        Categoriza el tipo de consulta para optimización
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['noticias', 'news', 'último', 'latest']):
            return 'news'
        elif any(word in query_lower for word in ['precio', 'cotización', 'stock', 'price']):
            return 'financial'
        elif any(word in query_lower for word in ['clima', 'weather', 'temperatura']):
            return 'weather'
        elif any(word in query_lower for word in ['qué es', 'what is', 'definición', 'definition']):
            return 'definition'
        elif any(word in query_lower for word in ['quién es', 'who is', 'biografía']):
            return 'biography'
        else:
            return 'general'
    
    def get_budget_status(self) -> Dict[str, Any]:
        """
        Retorna el estado del presupuesto
        """
        return self.budget_governor.get_budget_status()
    
    def validate_input(self, query: str, context: Dict[str, Any]) -> bool:
        """
        Valida la entrada
        """
        if not super().validate_input(query, context):
            return False
        
        # Verificar que la consulta tenga al menos 3 caracteres
        if len(query.strip()) < 3:
            return False
        
        # Evitar consultas muy largas (pueden ser costosas)
        if len(query) > 500:
            return False
        
        return True
'''

with open('nyx/skills/perplexity/main.py', 'w') as f:
    f.write(perplexity_skill_main)

perplexity_requirements = '''aiohttp>=3.9.1
requests>=2.31.0
'''

with open('nyx/skills/perplexity/requirements.txt', 'w') as f:
    f.write(perplexity_requirements)

print("✅ Perplexity Skill creada")

# 2. Dockerfile multi-stage
dockerfile_content = '''# Dockerfile multi-stage para Nyx
# Construye tanto el servidor Node.js como el puente Python

# Etapa 1: Base de Node.js
FROM node:20-slim AS node-base
WORKDIR /app/server
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-venv \\
    && rm -rf /var/lib/apt/lists/*

# Etapa 2: Dependencias de Node.js
FROM node-base AS node-deps
COPY server/package*.json ./
RUN npm ci --only=production

# Etapa 3: Base de Python
FROM python:3.11-slim AS python-base
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip

# Etapa 4: Dependencias de Python
FROM python-base AS python-deps
COPY bridge/requirements.txt ./bridge/
COPY skills/*/requirements.txt ./skills-requirements/
RUN pip install --no-cache-dir -r bridge/requirements.txt
# Instalar dependencias de todas las skills
RUN find ./skills-requirements/ -name "requirements.txt" -exec pip install --no-cache-dir -r {} \\;

# Etapa 5: Aplicación final
FROM node:20-slim AS runtime

# Instalar Python en la imagen final
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-venv \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar Node.js y dependencias
COPY --from=node-deps /app/server/node_modules ./server/node_modules
COPY server/ ./server/

# Copiar Python y dependencias
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin
COPY bridge/ ./bridge/
COPY clients/ ./clients/
COPY skills/ ./skills/

# Crear directorios necesarios
RUN mkdir -p logs data

# Variables de entorno
ENV NODE_ENV=production
ENV PYTHONPATH=/app/clients:/app/bridge/src
ENV PORT=3000

# Exponer puerto
EXPOSE 3000

# Comando de inicio
CMD ["node", "server/src/index.js"]
'''

with open('nyx/Dockerfile', 'w') as f:
    f.write(dockerfile_content)

print("✅ Dockerfile creado")

# 3. docker-compose.yml
docker_compose = '''version: '3.8'

services:
  nyx:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
      - "8080:8080"  # WebSocket port
    environment:
      - NODE_ENV=production
      - PORT=3000
      - HOST=0.0.0.0
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Servicio opcional para desarrollo con hot-reload
  nyx-dev:
    build:
      context: .
      dockerfile: Dockerfile
      target: node-base
    ports:
      - "3001:3000"
      - "8081:8080"
    environment:
      - NODE_ENV=development
      - PORT=3000
      - HOST=0.0.0.0
    env_file:
      - .env
    volumes:
      - ./server:/app/server
      - ./bridge:/app/bridge
      - ./clients:/app/clients
      - ./skills:/app/skills
      - ./data:/app/data
      - ./logs:/app/logs
      - /app/server/node_modules  # Evitar sobreescribir node_modules
    command: ["npm", "run", "dev"]
    profiles:
      - dev

networks:
  default:
    name: nyx-network

volumes:
  nyx-data:
  nyx-logs:
'''

with open('nyx/docker-compose.yml', 'w') as f:
    f.write(docker_compose)

print("✅ docker-compose.yml creado")

# 4. Script de inicio
startup_script = '''#!/bin/bash

# Script de inicio para Nyx
echo "🚀 Iniciando Nyx Personal Assistant..."

# Verificar variables de entorno críticas
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY no está configurada"
    exit 1
fi

if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "❌ Error: PERPLEXITY_API_KEY no está configurada" 
    exit 1
fi

echo "✅ Variables de entorno verificadas"

# Crear directorios necesarios
mkdir -p logs data

echo "✅ Directorios creados"

# Verificar si existe el archivo de credenciales de Google
if [ ! -f "data/client_secrets.json" ]; then
    echo "⚠️  Advertencia: No se encontró client_secrets.json en data/"
    echo "   Las funciones de Calendar no estarán disponibles hasta que configures las credenciales"
fi

# Iniciar servidor Node.js
cd server
echo "🟢 Iniciando servidor Node.js..."
npm start
'''

with open('nyx/start.sh', 'w') as f:
    f.write(startup_script)

# Hacer ejecutable
import os
os.chmod('nyx/start.sh', 0o755)

print("✅ Script de inicio creado")

# 5. Actualizar package.json principal
main_package_json = {
    "name": "nyx-assistant",
    "version": "0.1.0",
    "description": "Nyx - Tu Asistente Personal de Código Abierto",
    "main": "server/src/index.js",
    "scripts": {
        "start": "./start.sh",
        "dev": "cd server && npm run dev",
        "install-deps": "cd server && npm install",
        "docker:build": "docker build -t nyx .",
        "docker:run": "docker-compose up -d",
        "docker:dev": "docker-compose --profile dev up",
        "docker:stop": "docker-compose down",
        "logs": "docker-compose logs -f",
        "health": "curl -f http://localhost:3000/health"
    },
    "repository": {
        "type": "git",
        "url": "https://github.com/yourusername/nyx.git"
    },
    "keywords": [
        "ai", "assistant", "nodejs", "python", "gemini", 
        "perplexity", "calendar", "automation", "open-source"
    ],
    "author": "Nyx Team",
    "license": "MIT",
    "engines": {
        "node": ">=18.0.0",
        "python": ">=3.9.0"
    }
}

with open('nyx/package.json', 'w') as f:
    json.dump(main_package_json, f, indent=2)

print("✅ package.json principal actualizado")

print("\n🐳 Configuración de Docker completada exitosamente")