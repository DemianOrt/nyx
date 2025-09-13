#!/bin/bash

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
