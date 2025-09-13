const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const winston = require('winston');
const rateLimit = require('express-rate-limit');
const { spawn } = require('child_process');
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
    this.pendingRequests = new Map();

    this.setupMiddleware();
    this.setupRoutes();
    this.startPythonBridge();
  }

  setupMiddleware() {
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.NODE_ENV === 'production' 
        ? process.env.FRONTEND_URL 
        : true,
      credentials: true
    }));

    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 100,
      message: 'Demasiadas requests desde esta IP'
    });
    this.app.use('/api/', limiter);

    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    this.app.use((req, res, next) => {
      logger.info(`${req.method} ${req.path} - ${req.ip}`);
      next();
    });
  }

  setupRoutes() {
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        bridge: this.pythonBridge ? 'connected' : 'disconnected'
      });
    });

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

    this.app.use(express.static('public'));

    this.app.use('*', (req, res) => {
      res.status(404).json({ error: 'Ruta no encontrada' });
    });
  }

  startPythonBridge() {
    logger.info('Iniciando puente Python...');

    this.pythonBridge = spawn('python', ['../bridge/main.py'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let buffer = '';

    this.pythonBridge.stdout.on('data', (data) => {
      buffer += data.toString();
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      lines.forEach(line => {
        if (line.trim()) {
          try {
            const response = JSON.parse(line);
            this.handlePythonResponse(response);
          } catch (error) {
            logger.error('Error parsing Python response:', error);
          }
        }
      });
    });

    this.pythonBridge.stderr.on('data', (data) => {
      logger.error(`Python bridge error: ${data}`);
    });

    this.pythonBridge.on('close', (code) => {
      logger.warn(`Python bridge cerrado con código ${code}`);
      setTimeout(() => this.startPythonBridge(), 5000);
    });
  }

  async sendToPythonBridge(data) {
    return new Promise((resolve, reject) => {
      if (!this.pythonBridge) {
        reject(new Error('Python bridge no disponible'));
        return;
      }

      const requestId = Date.now() + Math.random();
      data.requestId = requestId;

      const request = JSON.stringify(data) + '\n';
      this.pythonBridge.stdin.write(request);

      const timeout = setTimeout(() => {
        this.pendingRequests.delete(requestId);
        reject(new Error('Timeout esperando respuesta de Python bridge'));
      }, 30000);

      this.pendingRequests.set(requestId, { resolve, reject, timeout });
    });
  }

  handlePythonResponse(response) {
    if (response.requestId && this.pendingRequests.has(response.requestId)) {
      const { resolve, timeout } = this.pendingRequests.get(response.requestId);
      clearTimeout(timeout);
      this.pendingRequests.delete(response.requestId);
      resolve(response);
    } else {
      logger.debug('Respuesta sin request ID:', response);
    }
  }

  start() {
    this.app.listen(this.port, this.host, () => {
      logger.info(`🚀 Nyx Server iniciado en http://${this.host}:${this.port}`);
      logger.info(`Ambiente: ${process.env.NODE_ENV || 'development'}`);
    });

    process.on('SIGINT', () => {
      logger.info('Cerrando servidor...');
      if (this.pythonBridge) {
        this.pythonBridge.kill();
      }
      process.exit(0);
    });
  }
}

const server = new NyxServer();
server.start();

module.exports = NyxServer;
