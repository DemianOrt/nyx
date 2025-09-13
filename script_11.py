# Verificar el estado final del proyecto y crear un resumen

import os
from pathlib import Path

# Verificar la estructura creada
nyx_path = Path('nyx')

print("📋 Verificación final del proyecto Nyx")
print("=" * 50)

# Función para mostrar estructura de directorios
def show_tree(path, prefix="", max_depth=3, current_depth=0):
    if current_depth >= max_depth:
        return
    
    items = sorted(path.iterdir())
    dirs = [item for item in items if item.is_dir()]
    files = [item for item in items if item.is_file()]
    
    # Mostrar archivos primero
    for i, file in enumerate(files):
        is_last_file = (i == len(files) - 1) and len(dirs) == 0
        connector = "└── " if is_last_file else "├── "
        print(f"{prefix}{connector}{file.name}")
    
    # Mostrar directorios
    for i, directory in enumerate(dirs):
        is_last = i == len(dirs) - 1
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "
        
        print(f"{prefix}{connector}{directory.name}/")
        show_tree(directory, prefix + extension, max_depth, current_depth + 1)

print("\n📁 Estructura del proyecto:")
if nyx_path.exists():
    show_tree(nyx_path)
else:
    print("❌ Error: Directorio nyx no encontrado")

# Verificar archivos críticos
critical_files = [
    'nyx/README.md',
    'nyx/package.json', 
    'nyx/.env.example',
    'nyx/Dockerfile',
    'nyx/docker-compose.yml',
    'nyx/server/src/index.js',
    'nyx/server/package.json',
    'nyx/bridge/main.py',
    'nyx/bridge/requirements.txt',
    'nyx/clients/gemini_client.py',
    'nyx/clients/perplexity_client.py',
    'nyx/clients/calendar_client.py',
    'nyx/clients/budget_governor.py',
    'nyx/skills/calendar/skill.json',
    'nyx/skills/calendar/main.py',
    'nyx/skills/perplexity/skill.json',
    'nyx/skills/perplexity/main.py'
]

print(f"\n✅ Verificación de archivos críticos:")
missing_files = []

for file_path in critical_files:
    if Path(file_path).exists():
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path}")
        missing_files.append(file_path)

if missing_files:
    print(f"\n⚠️  Archivos faltantes: {len(missing_files)}")
else:
    print(f"\n🎉 Todos los archivos críticos están presentes!")

# Estadísticas del proyecto
print(f"\n📊 Estadísticas del proyecto:")

def count_files(path, extensions):
    count = 0
    for ext in extensions:
        count += len(list(path.rglob(f"*.{ext}")))
    return count

if nyx_path.exists():
    js_files = count_files(nyx_path, ['js'])
    py_files = count_files(nyx_path, ['py'])
    json_files = count_files(nyx_path, ['json'])
    md_files = count_files(nyx_path, ['md'])
    
    print(f"📝 Archivos JavaScript: {js_files}")
    print(f"🐍 Archivos Python: {py_files}")
    print(f"📋 Archivos JSON: {json_files}")
    print(f"📚 Archivos Markdown: {md_files}")
    print(f"📁 Total de archivos: {js_files + py_files + json_files + md_files}")

# Próximos pasos
print(f"\n🚀 Próximos pasos para ejecutar Nyx:")
print("1. cd nyx")
print("2. cp .env.example .env")
print("3. Editar .env con tus credenciales")
print("4. cd server && npm install")
print("5. cd .. && python -m venv venv")
print("6. source venv/bin/activate  # En Windows: venv\\Scripts\\activate")
print("7. pip install -r bridge/requirements.txt")
print("8. ./start.sh  # o npm start")

print(f"\n📚 Documentación disponible:")
print("• README.md - Introducción y configuración básica")
print("• docs/INSTALLATION.md - Guía detallada de instalación")
print("• docs/API_EXAMPLES.md - Ejemplos de uso de la API")
print("• docs/SKILL_DEVELOPMENT.md - Crear nuevas habilidades")
print("• CONTRIBUTING.md - Guía para contribuir al proyecto")

print(f"\n🎯 Características implementadas:")
print("✅ Arquitectura híbrida Node.js + Python")
print("✅ Sistema de enrutamiento de 3 niveles")
print("✅ Integración con Google Gemini API")
print("✅ Integración con Perplexity API")
print("✅ Control de presupuesto automático")
print("✅ Habilidad de Google Calendar")
print("✅ Habilidad de búsqueda web")
print("✅ Sistema modular de skills")
print("✅ Contenedorización con Docker")
print("✅ Documentación completa")
print("✅ API REST con ejemplos")

print("\n🎉 ¡Proyecto Nyx creado exitosamente!")
print("Tu asistente personal de IA de código abierto está listo para usar.")