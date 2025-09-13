# Crear archivos de documentación y configuración final

# 1. Guía de instalación detallada
installation_guide = '''# Guía de Instalación de Nyx

Esta guía te llevará paso a paso para instalar y configurar Nyx en tu sistema.

## 📋 Prerrequisitos

### Software Requerido
- **Node.js** >= 18.0.0 ([Descargar](https://nodejs.org/))
- **Python** >= 3.9 ([Descargar](https://python.org/))
- **Git** ([Descargar](https://git-scm.com/))

### Cuentas Necesarias
- **Cuenta de Google** (para Calendar API y Gemini)
- **Cuenta de Perplexity Pro** (para búsqueda web)

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd nyx
```

### 2. Instalar Dependencias de Node.js
```bash
cd server
npm install
cd ..
```

### 3. Configurar Entorno Virtual de Python
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\\Scripts\\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r bridge/requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o tu editor preferido
```

## 🔧 Configuración de APIs

### Google Cloud Setup

#### 1. Crear Proyecto en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Anota el Project ID

#### 2. Habilitar APIs
En la consola de Google Cloud, habilita estas APIs:
- **Google Calendar API**
- **Google Drive API** (opcional)
- **Generative AI API** (Gemini)

#### 3. Configurar OAuth 2.0
1. Ve a "APIs y servicios" > "Credenciales"
2. Clic en "Crear credenciales" > "ID de cliente OAuth"
3. Selecciona "Aplicación web"
4. Añade URIs de redirección:
   - `http://localhost:3000/auth/callback`
5. Descarga el archivo JSON como `client_secrets.json`
6. Colócalo en `nyx/data/client_secrets.json`

#### 4. Generar Clave de API para Gemini
1. En "Credenciales", clic en "Crear credenciales" > "Clave de API"
2. Copia la clave generada
3. Añádela a tu archivo `.env` como `GEMINI_API_KEY`

### Perplexity API Setup

#### 1. Obtener Clave de API
1. Ve a [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Crea una nueva clave de API
3. Copia la clave

#### 2. Configurar en .env
```bash
PERPLEXITY_API_KEY=tu_clave_aqui
PERPLEXITY_BUDGET_LIMIT=5.00
```

## ▶️ Ejecución

### Método 1: Ejecución Normal
```bash
# Desde el directorio raíz de nyx
./start.sh

# O manualmente:
cd server
npm start
```

### Método 2: Docker
```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Para desarrollo con hot-reload
docker-compose --profile dev up
```

### Método 3: Desarrollo
```bash
# Terminal 1: Servidor Node.js
cd server
npm run dev

# Terminal 2: Puente Python (si lo ejecutas por separado)
cd bridge
python main.py
```

## ✅ Verificación

### Verificar que Nyx está funcionando:
1. Abre tu navegador en `http://localhost:3000/health`
2. Deberías ver un JSON con `"status": "healthy"`

### Probar API:
```bash
curl -X POST http://localhost:3000/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hola Nyx"}'
```

## 🔧 Configuración Avanzada

### Configurar Timezone
Edita `skills/calendar/skill.json`:
```json
{
  "config_schema": {
    "timezone": "America/Mexico_City"
  }
}
```

### Configurar Horario de Trabajo
```json
{
  "config_schema": {
    "working_hours": {
      "start": "08:00",
      "end": "18:00"
    }
  }
}
```

### Logs
Los logs se guardan en:
- `logs/error.log` - Solo errores
- `logs/combined.log` - Todos los logs
- `logs/bridge.log` - Logs del puente Python

## 🚨 Solución de Problemas

### Problema: "Python bridge no disponible"
**Solución:**
1. Verifica que Python esté instalado: `python --version`
2. Verifica que las dependencias estén instaladas
3. Revisa los logs en `logs/bridge.log`

### Problema: "GEMINI_API_KEY no encontrada"
**Solución:**
1. Verifica que el archivo `.env` existe
2. Verifica que `GEMINI_API_KEY=tu_clave` está configurado
3. Reinicia el servidor

### Problema: "Archivo de credenciales no encontrado"
**Solución:**
1. Descarga `client_secrets.json` de Google Cloud Console
2. Colócalo en `nyx/data/client_secrets.json`
3. Asegúrate que el archivo tiene los permisos correctos

### Problema: "Presupuesto de Perplexity agotado"
**Solución:**
1. Revisa tu uso en Perplexity
2. Espera al próximo ciclo de facturación
3. O resetea manualmente: elimina `data/budget.json`

## 📚 Próximos Pasos

Una vez que Nyx esté funcionando:

1. **Prueba las habilidades básicas:**
   - "¿Qué eventos tengo hoy?"
   - "Busca noticias sobre inteligencia artificial"
   - "Programa una reunión mañana a las 3pm"

2. **Explora la documentación de desarrollo** si quieres crear nuevas habilidades

3. **Únete a la comunidad** para compartir habilidades y obtener ayuda

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs en `logs/`
2. Verifica la configuración en `.env`
3. Consulta la documentación completa
4. Abre un issue en GitHub
'''

with open('nyx/docs/INSTALLATION.md', 'w') as f:
    f.write(installation_guide)

print("✅ Guía de instalación creada")

# 2. Guía para crear habilidades
skill_development_guide = '''# Guía de Desarrollo de Habilidades

Esta guía explica cómo crear nuevas habilidades (skills) para Nyx.

## 🏗️ Arquitectura de Habilidades

Cada habilidad es un módulo autocontenido que:
- Reside en su propio directorio en `skills/`
- Tiene un archivo `skill.json` con metadatos
- Implementa la clase principal en `main.py`
- Declara sus dependencias en `requirements.txt`

## 📁 Estructura de una Habilidad

```
skills/
└── mi_habilidad/
    ├── skill.json          # Configuración y metadatos
    ├── main.py            # Lógica principal
    ├── requirements.txt   # Dependencias Python
    └── config.schema.json # Schema de configuración (opcional)
```

## 🔧 Crear una Nueva Habilidad

### 1. Crear el Directorio
```bash
mkdir skills/mi_habilidad
cd skills/mi_habilidad
```

### 2. Crear skill.json
```json
{
  "name": "mi_habilidad",
  "version": "0.1.0",
  "description": "Descripción de tu habilidad",
  "author": "Tu Nombre",
  "class": "MiHabilidadSkill",
  "triggers": [
    "palabra_clave_1",
    "palabra_clave_2",
    "frase que activa"
  ],
  "required_apis": ["api_necesaria"],
  "config_schema": {
    "parametro1": "valor_por_defecto",
    "parametro2": 42
  }
}
```

### 3. Implementar main.py
```python
"""
Mi nueva habilidad para Nyx
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Añadir clients al path
sys.path.append(str(Path(__file__).parent.parent.parent / 'clients'))

from skill_base import Skill

class MiHabilidadSkill(Skill):
    """
    Descripción de tu habilidad
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Inicialización específica de tu habilidad
        self.parametro1 = self.config.get('config_schema', {}).get('parametro1', 'default')
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lógica principal de la habilidad
        """
        if not self.validate_input(query, context):
            return {
                'success': False,
                'error': 'Entrada inválida'
            }
        
        try:
            # Tu lógica aquí
            result = self._procesar_consulta(query, context)
            
            return self.format_response(result, 'text')
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error en habilidad: {str(e)}"
            }
    
    def _procesar_consulta(self, query: str, context: Dict[str, Any]) -> str:
        """
        Método privado para procesar la consulta
        """
        # Implementa tu lógica específica
        return f"Procesé: {query}"
    
    def validate_input(self, query: str, context: Dict[str, Any]) -> bool:
        """
        Validación específica de tu habilidad
        """
        if not super().validate_input(query, context):
            return False
        
        # Validaciones adicionales específicas
        return True
```

### 4. Definir Dependencias
```txt
# requirements.txt
requests>=2.31.0
beautifulsoup4>=4.12.0
# otras dependencias específicas
```

## 🎯 Tipos de Habilidades

### Habilidad de API Externa
Para integrar con APIs externas:

```python
class ApiSkill(Skill):
    def __init__(self, config):
        super().__init__(config)
        self.api_key = os.getenv('MI_API_KEY')
        self.base_url = "https://api.ejemplo.com"
    
    async def execute(self, query, context):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/endpoint") as response:
                data = await response.json()
                return self.format_response(data['resultado'])
```

### Habilidad de Procesamiento Local
Para procesamiento que no requiere APIs:

```python
class ProcessingSkill(Skill):
    def execute(self, query, context):
        # Procesamiento local
        resultado = self._analizar_texto(query)
        return self.format_response(resultado)
    
    def _analizar_texto(self, texto):
        # Tu lógica de procesamiento
        return texto.upper()
```

### Habilidad de Archivo/Base de Datos
Para trabajar con datos persistentes:

```python
class DataSkill(Skill):
    def __init__(self, config):
        super().__init__(config)
        self.data_file = Path(__file__).parent.parent.parent / 'data' / 'mi_data.json'
    
    def execute(self, query, context):
        data = self._load_data()
        resultado = self._search_data(data, query)
        return self.format_response(resultado)
```

## 🔄 Interacción con el Sistema de Enrutamiento

### Nivel 1: Clasificación Local
Tu habilidad puede ser activada directamente si:
- Los triggers en `skill.json` coinciden con la consulta
- La confianza del clasificador es >= 0.8

### Nivel 2: A través de Gemini
Tu habilidad puede recibir datos estructurados de Gemini:

```python
def execute(self, query, context):
    if context.get('level') == 2 and context.get('structured_data'):
        # Datos estructurados desde Gemini
        structured = context['structured_data']
        return self._handle_structured_input(structured)
    else:
        # Procesamiento normal
        return self._handle_natural_input(query)
```

### Nivel 3: Búsqueda Web
Normalmente las habilidades no son llamadas en Nivel 3, pero pueden usar Perplexity:

```python
from perplexity_client import PerplexityClient

class MiSkill(Skill):
    def __init__(self, config):
        super().__init__(config)
        self.perplexity = PerplexityClient()
    
    async def execute(self, query, context):
        # Usar Perplexity para información adicional
        web_info = await self.perplexity.search(f"información sobre {query}")
        # Procesar con tu lógica
        return self.format_response(resultado)
```

## 📊 Tipos de Respuesta

### Respuesta de Texto Simple
```python
return self.format_response("Mi respuesta en texto", 'text')
```

### Respuesta Estructurada
```python
return self.format_response({
    'titulo': 'Mi Resultado',
    'datos': [1, 2, 3],
    'metadata': {'procesado': True}
}, 'structured')
```

### Respuesta con Enlaces
```python
resultado = {
    'mensaje': 'Aquí tienes los resultados',
    'enlaces': [
        {'titulo': 'Enlace 1', 'url': 'https://ejemplo.com'},
        {'titulo': 'Enlace 2', 'url': 'https://otro.com'}
    ]
}
return self.format_response(resultado, 'links')
```

## 🧪 Testing de Habilidades

### Test Básico
```python
# test_mi_habilidad.py
import unittest
from main import MiHabilidadSkill

class TestMiHabilidad(unittest.TestCase):
    def setUp(self):
        config = {
            'name': 'mi_habilidad',
            'triggers': ['test']
        }
        self.skill = MiHabilidadSkill(config)
    
    def test_execute(self):
        result = self.skill.execute("test query", {'user_id': 'test'})
        self.assertTrue(result['success'])
        self.assertIn('content', result)
```

### Ejecutar Tests
```bash
cd skills/mi_habilidad
python -m pytest test_mi_habilidad.py
```

## 📝 Mejores Prácticas

### 1. Manejo de Errores
```python
def execute(self, query, context):
    try:
        resultado = self._procesar()
        return self.format_response(resultado)
    except SpecificError as e:
        logger.error(f"Error específico: {e}")
        return {'success': False, 'error': 'Mensaje amigable para usuario'}
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return {'success': False, 'error': 'Error interno'}
```

### 2. Logging
```python
import logging
logger = logging.getLogger(__name__)

def execute(self, query, context):
    logger.info(f"Ejecutando habilidad con query: {query[:50]}...")
    # tu lógica
    logger.debug(f"Resultado generado: {resultado}")
```

### 3. Configuración
```python
def __init__(self, config):
    super().__init__(config)
    # Usar valores por defecto seguros
    self.timeout = self.config.get('config_schema', {}).get('timeout', 30)
    self.max_items = self.config.get('config_schema', {}).get('max_items', 10)
```

### 4. Validación Robusta
```python
def validate_input(self, query, context):
    if not super().validate_input(query, context):
        return False
    
    # Validaciones específicas
    if len(query) > 1000:
        return False
    
    required_context = ['user_id']
    if not all(key in context for key in required_context):
        return False
    
    return True
```

## 🚀 Publicar tu Habilidad

### 1. Documentar
Crea un `README.md` en el directorio de tu habilidad:

```markdown
# Mi Habilidad

Descripción detallada de tu habilidad.

## Instalación
Instrucciones específicas de instalación.

## Uso
Ejemplos de uso y comandos.

## Configuración
Parámetros configurables.
```

### 2. Probar Completamente
- Test unitarios
- Test de integración
- Test con diferentes tipos de entrada
- Test con datos edge case

### 3. Contribuir
1. Fork del repositorio principal
2. Crear branch para tu habilidad
3. Añadir documentación
4. Enviar Pull Request

## 💡Tips y Trucos

### Reutilizar Código
```python
# Crear utilidades compartidas
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'utils'))
from text_utils import clean_text, extract_dates
```

### Caché de Resultados
```python
from functools import lru_cache

class MySkill(Skill):
    @lru_cache(maxsize=100)
    def _expensive_operation(self, param):
        # Operación costosa que se puede cachear
        return resultado
```

### Async/Await
```python
class AsyncSkill(Skill):
    async def execute(self, query, context):
        # Para operaciones asíncronas
        resultado = await self._async_operation()
        return self.format_response(resultado)
```

¡Ahora estás listo para crear habilidades increíbles para Nyx! 🎉
'''

with open('nyx/docs/SKILL_DEVELOPMENT.md', 'w') as f:
    f.write(skill_development_guide)

print("✅ Guía de desarrollo de skills creada")

# 3. Crear un ejemplo de uso con API
api_example = '''# Ejemplos de Uso de la API de Nyx

Este documento muestra cómo interactuar con Nyx a través de su API REST.

## 🌐 Endpoints Disponibles

### Base URL
```
http://localhost:3000
```

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servidor |
| POST | `/api/query` | Enviar consulta a Nyx |
| GET | `/api/skills` | Listar habilidades disponibles |

## 🔍 Ejemplos de Uso

### 1. Verificar Estado del Servidor

```bash
curl http://localhost:3000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "uptime": 3600,
  "bridge": "connected"
}
```

### 2. Enviar Consulta General

```bash
curl -X POST http://localhost:3000/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hola Nyx, ¿cómo estás?"}'
```

**Respuesta:**
```json
{
  "success": true,
  "level": 2,
  "method": "gemini_direct",
  "result": {
    "response": "¡Hola! Estoy funcionando perfectamente. Soy Nyx, tu asistente personal. ¿En qué puedo ayudarte hoy?",
    "type": "text"
  },
  "requestId": "1642248600123"
}
```

### 3. Consulta de Calendario

```bash
curl -X POST http://localhost:3000/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"message": "¿Qué eventos tengo mañana?", "userId": "user123"}'
```

**Respuesta:**
```json
{
  "success": true,
  "level": 1,
  "method": "local_classification",
  "skill": "calendar",
  "result": {
    "content": "📅 Tienes 2 evento(s) programado(s):\\n\\n1. **Reunión de equipo**\\n   🕒 2024-01-16T09:00:00Z\\n\\n2. **Llamada con cliente**\\n   🕒 2024-01-16T14:00:00Z\\n   📍 Zoom",
    "type": "calendar_events",
    "skill": "calendar"
  }
}
```

### 4. Búsqueda Web

```bash
curl -X POST http://localhost:3000/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"message": "¿Cuáles son las últimas noticias sobre inteligencia artificial?"}'
```

**Respuesta:**
```json
{
  "success": true,
  "level": 3,
  "method": "perplexity_search",
  "result": {
    "response": "🔍 **Búsqueda Web**\\n\\nSegún las últimas fuentes, la inteligencia artificial continúa avanzando rápidamente en 2024...",
    "sources": [
      {
        "id": "1",
        "title": "AI News - Latest Developments",
        "url": "https://example.com/ai-news"
      }
    ],
    "type": "search_result",
    "cost": 0.002
  }
}
```

### 5. Crear Evento de Calendario

```bash
curl -X POST http://localhost:3000/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Programa una reunión con Ana mañana a las 3pm", "userId": "user123"}'
```

**Respuesta:**
```json
{
  "success": true,
  "level": 2,
  "method": "gemini_reasoning",
  "skill": "calendar",
  "result": {
    "content": "✅ Evento creado: Reunión con Ana\\n📅 Fecha: 2024-01-16T15:00:00Z\\n🔗 Link: https://calendar.google.com/event?eid=...",
    "type": "event_created",
    "skill": "calendar"
  }
}
```

### 6. Listar Habilidades Disponibles

```bash
curl http://localhost:3000/api/skills
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "name": "calendar",
        "description": "Gestión de calendario de Google",
        "version": "0.1.0",
        "triggers": ["calendario", "evento", "reunión"],
        "author": "Nyx Team"
      },
      {
        "name": "perplexity",
        "description": "Búsqueda web en tiempo real",
        "version": "0.1.0",
        "triggers": ["buscar", "qué es", "noticias"],
        "author": "Nyx Team"
      }
    ],
    "count": 2
  }
}
```

## 🐍 Ejemplos en Python

### Cliente Python Simple

```python
import requests
import json

class NyxClient:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
    
    def query(self, message, user_id="anonymous"):
        """Envía una consulta a Nyx"""
        url = f"{self.base_url}/api/query"
        payload = {
            "message": message,
            "userId": user_id
        }
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def get_skills(self):
        """Obtiene la lista de habilidades disponibles"""
        url = f"{self.base_url}/api/skills"
        response = requests.get(url)
        return response.json()
    
    def health_check(self):
        """Verifica el estado del servidor"""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        return response.json()

# Uso del cliente
client = NyxClient()

# Verificar estado
health = client.health_check()
print(f"Estado: {health['status']}")

# Enviar consulta
result = client.query("¿Qué tiempo hace hoy?")
print(f"Respuesta: {result}")

# Listar habilidades
skills = client.get_skills()
print(f"Habilidades disponibles: {len(skills['data']['skills'])}")
```

### Cliente Asíncrono

```python
import aiohttp
import asyncio

class AsyncNyxClient:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
    
    async def query(self, session, message, user_id="anonymous"):
        """Envía una consulta asíncrona a Nyx"""
        url = f"{self.base_url}/api/query"
        payload = {
            "message": message,
            "userId": user_id
        }
        
        async with session.post(url, json=payload) as response:
            return await response.json()
    
    async def multiple_queries(self, queries):
        """Envía múltiples consultas en paralelo"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.query(session, query) 
                for query in queries
            ]
            results = await asyncio.gather(*tasks)
            return results

# Uso
async def main():
    client = AsyncNyxClient()
    queries = [
        "¿Qué eventos tengo hoy?",
        "Busca noticias sobre tecnología",
        "¿Cuál es mi próxima reunión?"
    ]
    
    results = await client.multiple_queries(queries)
    for i, result in enumerate(results):
        print(f"Consulta {i+1}: {result['success']}")

asyncio.run(main())
```

## 🌐 Ejemplos en JavaScript

### Cliente JavaScript (Node.js)

```javascript
const axios = require('axios');

class NyxClient {
    constructor(baseUrl = 'http://localhost:3000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    
    async query(message, userId = 'anonymous') {
        try {
            const response = await this.client.post('/api/query', {
                message,
                userId
            });
            return response.data;
        } catch (error) {
            throw new Error(`Query failed: ${error.message}`);
        }
    }
    
    async getSkills() {
        try {
            const response = await this.client.get('/api/skills');
            return response.data;
        } catch (error) {
            throw new Error(`Get skills failed: ${error.message}`);
        }
    }
    
    async healthCheck() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }
}

// Uso
async function main() {
    const client = new NyxClient();
    
    try {
        // Verificar estado
        const health = await client.healthCheck();
        console.log(`Estado: ${health.status}`);
        
        // Enviar consulta
        const result = await client.query('Hola Nyx!');
        console.log(`Respuesta: ${result.result.response}`);
        
        // Obtener habilidades
        const skills = await client.getSkills();
        console.log(`Habilidades: ${skills.data.count}`);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

### Cliente Web (Frontend)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Nyx Web Client</title>
</head>
<body>
    <div id="app">
        <input type="text" id="queryInput" placeholder="Pregunta algo a Nyx...">
        <button onclick="sendQuery()">Enviar</button>
        <div id="response"></div>
    </div>

    <script>
        class NyxWebClient {
            constructor(baseUrl = 'http://localhost:3000') {
                this.baseUrl = baseUrl;
            }
            
            async query(message) {
                const response = await fetch(`${this.baseUrl}/api/query`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        userId: 'web-user'
                    })
                });
                
                return await response.json();
            }
        }
        
        const client = new NyxWebClient();
        
        async function sendQuery() {
            const input = document.getElementById('queryInput');
            const responseDiv = document.getElementById('response');
            
            if (!input.value.trim()) return;
            
            responseDiv.innerHTML = 'Pensando...';
            
            try {
                const result = await client.query(input.value);
                
                if (result.success) {
                    responseDiv.innerHTML = `
                        <strong>Nyx:</strong> ${result.result.content || result.result.response}
                        <br><small>Método: ${result.method} | Nivel: ${result.level}</small>
                    `;
                } else {
                    responseDiv.innerHTML = `<strong>Error:</strong> ${result.error}`;
                }
                
                input.value = '';
            } catch (error) {
                responseDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }
        
        // Enviar con Enter
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendQuery();
            }
        });
    </script>
</body>
</html>
```

## 📊 Manejo de Errores

### Tipos de Error Comunes

```json
// Error de validación
{
  "success": false,
  "error": "Mensaje requerido",
  "code": "VALIDATION_ERROR"
}

// Error de presupuesto agotado
{
  "success": false,
  "error": "Presupuesto de búsqueda web agotado para este mes",
  "budget_status": {
    "limit": 5.0,
    "spent": 5.0,
    "remaining": 0.0
  },
  "type": "budget_exceeded"
}

// Error de API externa
{
  "success": false,
  "error": "Error accediendo al calendario: 401 Unauthorized",
  "level": 1,
  "skill": "calendar"
}

// Error interno del servidor
{
  "success": false,
  "error": "Error interno del servidor",
  "code": "INTERNAL_ERROR"
}
```

### Manejo de Errores en Cliente

```python
def handle_nyx_response(response):
    if not response.get('success'):
        error_type = response.get('type', 'unknown')
        
        if error_type == 'budget_exceeded':
            print("⚠️ Presupuesto de búsqueda agotado")
            budget = response.get('budget_status', {})
            print(f"Gastado: ${budget.get('spent', 0):.2f} de ${budget.get('limit', 0):.2f}")
        
        elif 'calendar' in response.get('error', '').lower():
            print("📅 Error de calendario - verifica tus credenciales")
        
        else:
            print(f"❌ Error: {response.get('error', 'Error desconocido')}")
        
        return None
    
    return response['result']
```

¡Ahora ya sabes cómo integrar Nyx en tus aplicaciones! 🚀
'''

with open('nyx/docs/API_EXAMPLES.md', 'w') as f:
    f.write(api_example)

print("✅ Ejemplos de API creados")

# 4. Archivo de contribución
contributing_guide = '''# Guía de Contribución a Nyx

¡Gracias por tu interés en contribuir a Nyx! Esta guía te ayudará a empezar.

## 🤝 Formas de Contribuir

- 🐛 **Reportar bugs** y problemas
- 💡 **Sugerir nuevas funcionalidades**
- 📝 **Mejorar documentación**
- 🔧 **Crear nuevas habilidades**
- 🔍 **Revisar código** y pull requests
- 🧪 **Escribir pruebas**
- 🌍 **Traducir** a otros idiomas

## 🚀 Configuración de Desarrollo

### 1. Fork y Clone
```bash
# Fork el repositorio en GitHub
git clone https://github.com/tu-usuario/nyx.git
cd nyx
```

### 2. Configurar Entorno
```bash
# Instalar dependencias
npm run install-deps
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
pip install -r bridge/requirements.txt

# Configurar pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de desarrollo
```

## 🔧 Flujo de Desarrollo

### 1. Crear Rama de Feature
```bash
git checkout -b feature/nueva-funcionalidad
# o
git checkout -b fix/corregir-bug
# o
git checkout -b skill/nueva-habilidad
```

### 2. Hacer Cambios
- Escribe código limpio y bien documentado
- Sigue las convenciones de estilo del proyecto
- Añade pruebas para nueva funcionalidad
- Actualiza documentación si es necesario

### 3. Probar Cambios
```bash
# Tests de Node.js
cd server
npm test

# Tests de Python
cd bridge
python -m pytest

# Tests de integración
npm run test:integration
```

### 4. Commit y Push
```bash
git add .
git commit -m "feat: añadir nueva funcionalidad X"
git push origin feature/nueva-funcionalidad
```

### 5. Crear Pull Request
- Ve a GitHub y crea un PR
- Describe claramente los cambios
- Referencia issues relacionados
- Espera revisión del equipo

## 📋 Estándares de Código

### JavaScript/Node.js
- Usar ESLint y Prettier
- Seguir estilo Standard
- Documentar funciones públicas
- Usar async/await en lugar de callbacks

```javascript
// ✅ Bueno
async function procesarConsulta(query) {
  try {
    const resultado = await llamadaAPI(query);
    return { success: true, data: resultado };
  } catch (error) {
    logger.error('Error procesando consulta:', error);
    throw error;
  }
}

// ❌ Malo
function procesarConsulta(query, callback) {
  llamadaAPI(query, function(err, resultado) {
    if (err) callback(err);
    else callback(null, resultado);
  });
}
```

### Python
- Seguir PEP 8
- Usar Black para formateo
- Type hints cuando sea posible
- Documentar con docstrings

```python
# ✅ Bueno
def procesar_consulta(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa una consulta del usuario.
    
    Args:
        query: La consulta del usuario
        context: Contexto adicional
        
    Returns:
        Resultado procesado
    """
    try:
        resultado = self._analizar_query(query)
        return {"success": True, "data": resultado}
    except Exception as e:
        logger.error(f"Error procesando consulta: {e}")
        raise

# ❌ Malo
def procesar_consulta(query, context):
    resultado = self._analizar_query(query)
    return resultado
```

## 🧪 Escribir Pruebas

### Tests de Node.js (Jest)
```javascript
// server/tests/api.test.js
describe('API Endpoints', () => {
  test('POST /api/query should return success', async () => {
    const response = await request(app)
      .post('/api/query')
      .send({ message: 'test query' })
      .expect(200);
    
    expect(response.body.success).toBe(true);
  });
});
```

### Tests de Python (pytest)
```python
# bridge/tests/test_skill_manager.py
import pytest
from src.skill_manager import SkillManager

class TestSkillManager:
    def setup_method(self):
        self.skill_manager = SkillManager()
    
    def test_load_skills(self):
        skills = self.skill_manager.get_available_skills()
        assert len(skills) > 0
        assert 'calendar' in [s['name'] for s in skills]
```

### Tests de Habilidades
```python
# skills/calendar/test_calendar.py
from main import CalendarSkill

def test_calendar_skill_execution():
    config = {'name': 'calendar', 'triggers': ['calendario']}
    skill = CalendarSkill(config)
    
    result = skill.execute("listar eventos", {'user_id': 'test'})
    assert result['success'] is True
```

## 📝 Documentación

### Documentar Código
- Usar JSDoc para JavaScript
- Usar docstrings para Python
- Explicar el "por qué", no solo el "qué"

### Actualizar README
Si añades funcionalidad importante:
- Actualizar README.md principal
- Añadir ejemplos de uso
- Actualizar guías de instalación

### Documentación de APIs
Si modificas endpoints:
- Actualizar docs/API_EXAMPLES.md
- Añadir ejemplos de uso
- Documentar parámetros y respuestas

## 🎯 Crear Nueva Habilidad

### 1. Planificar Habilidad
- Definir propósito claro
- Identificar APIs/recursos necesarios
- Diseñar interfaz de usuario

### 2. Implementar
```bash
mkdir skills/mi_habilidad
cd skills/mi_habilidad
```

Seguir guía en `docs/SKILL_DEVELOPMENT.md`

### 3. Documentar
- README.md específico
- Ejemplos de uso
- Configuración requerida

### 4. Probar
- Tests unitarios
- Tests de integración
- Validar con diferentes entradas

## 🐛 Reportar Bugs

### Información a Incluir
```markdown
**Descripción del Bug**
Descripción clara y concisa del problema.

**Pasos para Reproducir**
1. Ir a '...'
2. Hacer click en '....'
3. Ejecutar '....'
4. Ver error

**Comportamiento Esperado**
Lo que esperabas que pasara.

**Comportamiento Actual**
Lo que realmente pasó.

**Entorno**
- OS: [e.g. Ubuntu 20.04]
- Node.js: [e.g. 18.17.0]
- Python: [e.g. 3.11.0]
- Versión de Nyx: [e.g. 0.1.0]

**Logs**
```
logs del error aquí
```

**Información Adicional**
Cualquier otra información relevante.
```

## 💡 Sugerir Funcionalidades

### Template para Sugerencias
```markdown
**¿Tu solicitud está relacionada con un problema?**
Descripción clara del problema. Ej: "Me frustra que..."

**Describe la solución que te gustaría**
Descripción clara de lo que quieres que pase.

**Describe alternativas consideradas**
Otras soluciones que hayas considerado.

**Información adicional**
Cualquier otro contexto sobre la solicitud.
```

## 🔍 Revisión de Código

### Como Revisor
- Sé constructivo y amable
- Verifica funcionalidad y tests
- Sugiere mejoras específicas
- Aprueba cambios buenos rápidamente

### Como Autor
- Responde a comentarios constructivamente
- Haz cambios solicitados prontamente
- Explica decisiones de diseño si es necesario
- Agradece el feedback

## 🏷️ Convenciones de Commit

Usar [Conventional Commits](https://conventionalcommits.org/):

```bash
# Nuevas funcionalidades
git commit -m "feat: añadir habilidad de clima"

# Corrección de bugs
git commit -m "fix: corregir error en clasificador de intenciones"

# Documentación
git commit -m "docs: actualizar guía de instalación"

# Refactoring
git commit -m "refactor: mejorar estructura de clientes de API"

# Tests
git commit -m "test: añadir tests para skill de calendario"

# Configuración
git commit -m "chore: actualizar dependencias"
```

## 🏆 Reconocimiento

Los contribuidores serán reconocidos:
- En CONTRIBUTORS.md
- En releases notes
- En README.md (contribuidores principales)

## 📞 Obtener Ayuda

- 💬 **Discord**: [Link del servidor]
- 🐛 **Issues**: GitHub Issues
- 📧 **Email**: nyx-dev@example.com
- 📚 **Docs**: Documentación completa

## 📜 Código de Conducta

### Nuestro Compromiso
Crear un ambiente acogedor e inclusivo para todos.

### Estándares
**Comportamientos positivos:**
- Usar lenguaje acogedor e inclusivo
- Respetar diferentes puntos de vista
- Aceptar críticas constructivas
- Enfocarse en lo que es mejor para la comunidad

**Comportamientos inaceptables:**
- Uso de lenguaje o imágenes sexualizadas
- Comentarios insultantes o despectivos
- Acoso público o privado
- Publicar información privada sin permiso

### Cumplimiento
Instancias de comportamiento abusivo pueden ser reportadas a nyx-conduct@example.com.

---

¡Gracias por contribuir a Nyx! 🎉 Juntos estamos construyendo el futuro de los asistentes personales de código abierto.
'''

with open('nyx/CONTRIBUTING.md', 'w') as f:
    f.write(contributing_guide)

print("✅ Guía de contribución creada")

print("\n📚 Documentación completa creada exitosamente")
print("\n🎉 ¡Proyecto Nyx completado!")
print("\nEstructura final:")
print("📁 nyx/")
print("  ├── 🟢 server/          # Servidor Node.js")
print("  ├── 🐍 bridge/          # Puente Python")
print("  ├── 🔌 clients/         # Clientes de API")
print("  ├── 📋 skills/          # Habilidades modulares")
print("  ├── 📚 docs/            # Documentación completa")
print("  ├── 🐳 Dockerfile       # Containerización")
print("  ├── 📝 README.md        # Documentación principal")
print("  └── ⚙️  .env.example    # Variables de entorno")