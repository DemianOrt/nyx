# Crear los archivos principales del proyecto con contenido base

# 1. README.md principal
readme_content = """# Nyx - Tu Asistente Personal de Código Abierto

Nyx se concibe como un asistente personal de código abierto, autoalojado, diseñado específicamente para desarrolladores y usuarios con conocimientos técnicos. El proyecto se fundamenta en un compromiso inquebrantable con la privacidad, la modularidad y el control total del usuario sobre sus datos.

## 🚀 Características Principales

- **Autoalojamiento para la Privacidad**: Control absoluto de tus datos
- **Arquitectura Modular de "Habilidades"**: Sistema extensible de skills
- **Cerebro de IA Híbrido**: Combina Google Gemini y Perplexity API
- **Integración con Google Services**: Calendar, Drive y más
- **Control de Presupuesto**: Gestión automática de límites de API

## 🏗️ Arquitectura

Nyx utiliza una arquitectura híbrida Node.js + Python:

- **Servidor Node.js**: Gestión de comunicaciones y API web
- **Puente Python**: Ejecución de lógica de IA y habilidades
- **Sistema de Enrutamiento de 3 Niveles**:
  1. Clasificación local de intenciones
  2. Razonamiento avanzado (Gemini API)
  3. Búsqueda web en tiempo real (Perplexity API)

## 📋 Prerrequisitos

- Node.js >= 18.0.0
- Python >= 3.9
- Cuenta de Google Cloud (para APIs)
- Cuenta de Perplexity Pro (para API)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd nyx
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Instalar dependencias de Node.js
```bash
cd server
npm install
cd ..
```

### 4. Configurar entorno virtual de Python
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
pip install -r bridge/requirements.txt
```

### 5. Iniciar Nyx
```bash
npm start
```

## 🔧 Configuración

### Obtener Credenciales de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita las APIs necesarias:
   - Google Calendar API
   - Google Drive API
   - Google AI (Gemini) API
4. Configura OAuth 2.0 y descarga `client_secrets.json`
5. Genera una clave de API para Gemini

### Configurar Perplexity API

1. Ve a [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Genera tu clave de API
3. Nota: Plan Pro incluye $5/mes de crédito API

## 📁 Estructura del Proyecto

```
nyx/
├── server/           # Núcleo Node.js
├── bridge/           # Puente Python
├── skills/           # Habilidades modulares
│   ├── calendar/     # Integración Google Calendar
│   └── perplexity/   # Búsqueda web
├── clients/          # Clientes de API
├── docs/            # Documentación
└── tests/           # Pruebas
```

## 🎯 Habilidades Disponibles

### Google Calendar
- Crear eventos
- Listar próximos eventos
- Encontrar huecos libres
- Gestionar invitaciones

### Perplexity Search
- Búsquedas en tiempo real
- Respuestas con fuentes verificadas
- Control de presupuesto automático

## 🐳 Docker

### Ejecutar con Docker Compose
```bash
docker-compose up -d
```

### Construir imagen personalizada
```bash
docker build -t nyx .
docker run -p 3000:3000 --env-file .env nyx
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-habilidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva habilidad'`)
4. Push a la rama (`git push origin feature/nueva-habilidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Inspirado en [Leon AI](https://getleon.ai/)
- Powered by Google Gemini y Perplexity AI
- Comunidad de código abierto

---

**Nota**: Este proyecto está en desarrollo activo. Las funcionalidades pueden cambiar entre versiones.
"""

with open('nyx/README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✅ README.md principal creado")

# 2. .env.example
env_example = """# Google Cloud Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
GEMINI_API_KEY=your_gemini_api_key

# Perplexity Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key
PERPLEXITY_BUDGET_LIMIT=5.00

# Application Configuration
NODE_ENV=development
PORT=3000
HOST=localhost

# Logging
LOG_LEVEL=info

# Data Storage
DATA_PATH=./data
ENABLE_GOOGLE_DRIVE_SYNC=false
"""

with open('nyx/.env.example', 'w') as f:
    f.write(env_example)

print("✅ .env.example creado")

# 3. .gitignore principal
gitignore_content = """.env
.env.local
.env.production

# Node modules
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Data and credentials
data/
token.pickle
client_secrets.json
credentials.json

# Logs
logs/
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Temporary files
*.tmp
*.temp
"""

with open('nyx/.gitignore', 'w') as f:
    f.write(gitignore_content)

print("✅ .gitignore principal creado")

print("\n📁 Archivos de configuración principales creados exitosamente")