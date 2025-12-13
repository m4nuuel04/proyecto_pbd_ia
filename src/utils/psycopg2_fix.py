"""
Módulo de inicialización para parchear el encoding antes de importar psycopg2.
Este módulo DEBE importarse antes que cualquier código que use psycopg2.
"""
import sys
import os
import locale
import warnings

# SOLUCIÓN CRÍTICA: Configurar el encoding de Python a nivel de sistema
# antes de que psycopg2 intente leer cualquier archivo
if sys.platform == 'win32':
    # En Windows, forzar UTF-8 con reemplazo de errores
    import codecs
    
    # Registrar un codec handler que reemplace errores automáticamente
    def custom_error_handler(error):
        """Manejador de errores personalizado que reemplaza caracteres inválidos"""
        return ('?', error.end)
    
    codecs.register_error('custom_replace', custom_error_handler)
    
    # Configurar el encoding por defecto de Python
    if hasattr(sys, '_enablelegacywindowsfsencoding'):
        sys._enablelegacywindowsfsencoding()

# Configurar variables de entorno críticas
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
os.environ['PYTHONUTF8'] = '1'  # Fuerza UTF-8 mode en Python 3.7+

# Deshabilitar archivos de configuración de PostgreSQL que pueden tener encoding problemático
os.environ['PGPASSFILE'] = 'nul'
os.environ['PGSERVICEFILE'] = 'nul'
os.environ['PGSYSCONFDIR'] = 'nul'

# Configurar locale para PostgreSQL client
os.environ['PGLOCALEDIR'] = ''  # Deshabilitar traducciones
os.environ['PGDATESTYLE'] = 'ISO'

# Suprimir warnings de encoding
warnings.filterwarnings('ignore', category=UnicodeWarning)

print("[INFO] psycopg2_fix inicializado - protecciones de encoding activadas")
