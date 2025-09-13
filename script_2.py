# Crear los archivos del servidor Node.js

# 1. package.json del servidor
package_json = {
    "name": "nyx-server",
    "version": "0.1.0",
    "description": "Nyx Personal Assistant - Node.js Server",
    "main": "src/index.js",
    "scripts": {
        "start": "node src/index.js",
        "dev": "nodemon src/index.js",
        "test": "jest",
        "lint": "eslint src/",
        "bridge": "python ../bridge/main.py"
    },
    "keywords": ["ai", "assistant", "nodejs", "python", "gemini", "perplexity"],
    "author": "Nyx Team",
    "license": "MIT",
    "dependencies": {
        "express": "^4.18.2",
        "cors": "^2.8.5",
        "helmet": "^7.1.0",
        "dotenv": "^16.3.1",
        "ws": "^8.14.2",
        "winston": "^3.11.0",
        "express-rate-limit": "^7.1.5",
        "body-parser": "^1.20.2"
    },
    "devDependencies": {
        "nodemon": "^3.0.2",
        "jest": "^29.7.0",
        "eslint": "^8.55.0",
        "eslint-config-standard": "^17.1.0"
    },
    "engines": {
        "node": ">=18.0.0",
        "npm": ">=8.0.0"
    }
}

import json
with open('nyx/server/package.json', 'w') as f:
    json.dump(package_json, f, indent=2)

print("✅ package.json del servidor creado")

# 2. Servidor principal (Node.js)
server_index = """const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const winston = require('winston');
const rateLimit = require('express-rate-limit');
const { spawn } = require('child_process');
const WebSocket = require('ws');
require('dotenv').config();

// Configuración de logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: '../logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: '../logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

class NyxServer {
  constructor() {
    this.app = express();
    this.port = process.env.PORT || 3000;
    this.host = process.env.HOST || 'localhost';
    this.pythonBridge = null;
    this.wss = null;
    
    this.setupMiddleware();
    this.setupRoutes();
    this.startPythonBridge();
  }

  setupMiddleware() {
    // Seguridad
    this.app.use(helmet());
    
    // CORS
    this.app.use(cors({
      origin: process.env.NODE_ENV === 'production' 
        ? process.env.FRONTEND_URL 
        : true,
      credentials: true
    }));

    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutos
      max: 100, // máximo 100 requests por ventana
      message: 'Demasiadas requests desde esta IP'
    });
    this.app.use('/api/', limiter);

    // Parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    // Logging de requests
    this.app.use((req, res, next) => {
      logger.info(`${req.method} ${req.path} - ${req.ip}`);
      next();
    });
  }

  setupRoutes() {
    // Ruta de salud
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    });

    // API principal
    this.app.post('/api/query', async (req, res) => {
      try {
        const { message, userId } = req.body;
        
        if (!message) {
          return res.status(400).json({ error: 'Mensaje requerido' });
        }

        logger.info(`Query recibida: ${message}`);
        
        const response = await this.sendToPythonBridge({
          type: 'query',
          message,
          userId: userId || 'anonymous',
          timestamp: new Date().toISOString()
        });

        res.json(response);
      } catch (error) {
        logger.error('Error procesando query:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
      }
    });

    // Ruta para obtener habilidades disponibles
    this.app.get('/api/skills', async (req, res) => {
      try {
        const response = await this.sendToPythonBridge({
          type: 'list_skills'
        });
        res.json(response);
      } catch (error) {
        logger.error('Error obteniendo skills:', error);
        res.status(500).json({ error: 'Error obteniendo habilidades' });
      }
    });

    // Servir archivos estáticos (si hay frontend)
    this.app.use(express.static('public'));

    // Ruta catch-all
    this.app.use('*', (req, res) => {
      res.status(404).json({ error: 'Ruta no encontrada' });
    });
  }

  startPythonBridge() {
    logger.info('Iniciando puente Python...');
    
    this.pythonBridge = spawn('python', ['../bridge/main.py'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    this.pythonBridge.stdout.on('data', (data) => {
      const response = data.toString().trim();
      logger.debug(`Python bridge output: ${response}`);
      
      try {
        const parsedResponse = JSON.parse(response);
        this.handlePythonResponse(parsedResponse);
      } catch (error) {
        logger.error('Error parsing Python response:', error);
      }
    });

    this.pythonBridge.stderr.on('data', (data) => {
      logger.error(`Python bridge error: ${data}`);
    });

    this.pythonBridge.on('close', (code) => {
      logger.warn(`Python bridge cerrado con código ${code}`);
      // Reintentar conexión después de 5 segundos
      setTimeout(() => this.startPythonBridge(), 5000);
    });
  }

  async sendToPythonBridge(data) {
    return new Promise((resolve, reject) => {
      if (!this.pythonBridge) {
        reject(new Error('Python bridge no disponible'));
        return;
      }

      const request = JSON.stringify(data) + '\\n';
      this.pythonBridge.stdin.write(request);

      // Timeout para la respuesta
      const timeout = setTimeout(() => {
        reject(new Error('Timeout esperando respuesta de Python bridge'));
      }, 30000);

      // Esta es una implementación simplificada
      // En producción, necesitarías un sistema más robusto para manejar respuestas
      const responseHandler = (data) => {
        clearTimeout(timeout);
        try {
          const response = JSON.parse(data.toString());
          resolve(response);
        } catch (error) {
          reject(error);
        }
      };

      this.pythonBridge.stdout.once('data', responseHandler);
    });
  }

  handlePythonResponse(response) {
    // Manejar respuestas del puente Python
    logger.debug('Respuesta del puente Python:', response);
    
    // Enviar a clientes WebSocket si es necesario
    if (this.wss) {
      this.wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(response));
        }
      });
    }
  }

  setupWebSocket() {
    this.wss = new WebSocket.Server({ port: 8080 });
    
    this.wss.on('connection', (ws) => {
      logger.info('Nueva conexión WebSocket');
      
      ws.on('message', async (message) => {
        try {
          const data = JSON.parse(message);
          const response = await this.sendToPythonBridge(data);
          ws.send(JSON.stringify(response));
        } catch (error) {
          logger.error('Error en WebSocket:', error);
          ws.send(JSON.stringify({ error: 'Error procesando mensaje' }));
        }
      });

      ws.on('close', () => {
        logger.info('Conexión WebSocket cerrada');
      });
    });

    logger.info('Servidor WebSocket iniciado en puerto 8080');
  }

  start() {
    this.app.listen(this.port, this.host, () => {
      logger.info(`🚀 Nyx Server iniciado en http://${this.host}:${this.port}`);
      logger.info(`Ambiente: ${process.env.NODE_ENV || 'development'}`);
    });

    // Iniciar WebSocket server
    this.setupWebSocket();

    // Manejo de cierre graceful
    process.on('SIGINT', () => {
      logger.info('Cerrando servidor...');
      if (this.pythonBridge) {
        this.pythonBridge.kill();
      }
      process.exit(0);
    });
  }
}

// Iniciar servidor
const server = new NyxServer();
server.start();

module.exports = NyxServer;
"""

with open('nyx/server/src/index.js', 'w') as f:
    f.write(server_index)

print("✅ Servidor Node.js principal creado")

# 3. .gitignore del servidor
server_gitignore = """node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env
.env.local
.env.production
logs/
*.log
"""

with open('nyx/server/.gitignore', 'w') as f:
    f.write(server_gitignore)

print("✅ .gitignore del servidor creado")

print("\n🟢 Servidor Node.js configurado exitosamente")