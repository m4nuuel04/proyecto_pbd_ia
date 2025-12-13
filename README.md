# 🤖 Agente de Base de Datos con IA

Un asistente inteligente que permite consultar bases de datos PostgreSQL y MongoDB usando lenguaje natural. Utiliza modelos de lenguaje (LLM) con Ollama para generar consultas SQL y PyMongo automáticamente.

## ✨ Características

- 🗣️ **Consultas en lenguaje natural**: Pregunta en español y obtén respuestas de tu base de datos
- 🔄 **Soporte multi-base de datos**: Compatible con PostgreSQL y MongoDB
- 🖥️ **Interfaz dual**: CLI interactiva y GUI moderna con CustomTkinter
- 🎨 **Respuestas formateadas**: Salida colorizada en terminal y renderizado de markdown en GUI
- 🧠 **Powered by Ollama**: Utiliza modelos LLM locales para privacidad y control
- 📊 **Sistema de evaluación**: Herramientas para medir la precisión de las consultas generadas

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- PostgreSQL (opcional, si usarás bases de datos relacionales)
- MongoDB (opcional, si usarás bases de datos NoSQL)
- [Ollama](https://ollama.ai/) instalado y ejecutándose

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd proyecto_pbd_ia
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**

Copia el archivo de ejemplo y configura tus credenciales:
```bash
cp .env.example .env
```

Edita el archivo `.env` con tus datos:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
POSTGRES_URI=postgresql://user:password@localhost:5432/dbname
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=llm_agent_db
```

4. **Iniciar Ollama**

Asegúrate de tener Ollama ejecutándose con un modelo compatible (por ejemplo, `llama2` o `mistral`):
```bash
ollama run llama2
```

## 📖 Uso

### Interfaz de Línea de Comandos (CLI)

#### Modo interactivo
```bash
python main.py
```

Comandos disponibles en modo interactivo:
- Escribe tu consulta en lenguaje natural
- `switch mongo` o `switch postgres` - Cambiar entre bases de datos
- `salir` o `exit` - Terminar la sesión

#### Modo de consulta única
```bash
# Consulta a PostgreSQL
python main.py --query "¿Cuántos usuarios hay en la base de datos?" --db postgres

# Consulta a MongoDB
python main.py --query "Lista todos los documentos de la colección productos" --db mongo
```

### Interfaz Gráfica (GUI)

```bash
python gui.py
```

La GUI ofrece:
- 🎯 Selector de base de datos (PostgreSQL/MongoDB)
- 💬 Chat interactivo con historial
- 🎨 Renderizado de markdown para respuestas formateadas
- 📝 Visualización de código SQL/PyMongo generado
- ⚡ Ejecución asíncrona sin bloquear la interfaz

## 🏗️ Estructura del Proyecto

```
proyecto_pbd_ia/
├── src/
│   ├── agents/
│   │   ├── sql_agent.py      # Agente para PostgreSQL
│   │   └── mongo_agent.py    # Agente para MongoDB
│   └── utils/
│       └── encoding_utils.py # Utilidades de codificación
├── evaluation/
│   └── evaluate.py           # Sistema de evaluación
├── scripts/
│   └── verify_mongo.py       # Script de verificación MongoDB
├── main.py                   # CLI principal
├── gui.py                    # Interfaz gráfica
├── requirements.txt          # Dependencias
└── .env.example             # Plantilla de configuración
```

## 🔧 Componentes Principales

### SQL Agent (`src/agents/sql_agent.py`)
- Genera consultas SQL a partir de lenguaje natural
- Ejecuta consultas en PostgreSQL
- Interpreta resultados y los presenta en español

### Mongo Agent (`src/agents/mongo_agent.py`)
- Genera código PyMongo para consultas
- Ejecuta operaciones en MongoDB
- Formatea respuestas de documentos JSON

### Utilidades de Codificación (`src/utils/encoding_utils.py`)
- Manejo robusto de codificaciones UTF-8
- Compatibilidad entre diferentes sistemas operativos
- Prevención de errores de codificación

## 🎯 Ejemplos de Consultas

### PostgreSQL
```
¿Cuántos usuarios hay registrados?
Lista las 10 últimas transacciones
¿Cuál es el producto más vendido?
Muestra las ventas por categoría
```

### MongoDB
```
Lista todos los documentos de la colección usuarios
¿Cuántos productos hay en stock?
Muestra los pedidos del último mes
Busca usuarios con email que contenga "gmail"
```

## 🧪 Evaluación

Ejecuta el sistema de evaluación para medir la precisión del agente:

```bash
python evaluation/evaluate.py
```

Esto ejecutará casos de prueba predefinidos y mostrará:
- ✅ Estado de cada consulta (SUCCESS/FAILED)
- ⏱️ Tiempo de ejecución
- 📊 Resumen de resultados

## 🛠️ Tecnologías Utilizadas

- **LangChain**: Framework para aplicaciones con LLM
- **Ollama**: Ejecución local de modelos de lenguaje
- **PostgreSQL**: Base de datos relacional
- **MongoDB**: Base de datos NoSQL
- **CustomTkinter**: Interfaz gráfica moderna
- **Colorama**: Salida colorizada en terminal
- **Python-dotenv**: Gestión de variables de entorno

## 🐛 Solución de Problemas

### Error de codificación UTF-8
El proyecto incluye utilidades especiales para manejar problemas de codificación. Si encuentras errores, asegúrate de que:
- Tu terminal soporta UTF-8
- Los archivos `.env` están guardados con codificación UTF-8

### Ollama no responde
Verifica que:
- Ollama esté ejecutándose: `ollama list`
- Tengas un modelo descargado: `ollama pull llama2`
- El servicio esté activo en `http://localhost:11434`

### Conexión a base de datos fallida
Revisa:
- Las credenciales en el archivo `.env`
- Que los servicios de PostgreSQL/MongoDB estén activos
- Los puertos de conexión (5432 para PostgreSQL, 27017 para MongoDB)

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, por favor abre un issue en el repositorio.

---

**Nota**: Este proyecto fue desarrollado como parte de un ejercicio de bases de datos con inteligencia artificial, demostrando la integración de LLMs con sistemas de gestión de bases de datos relacionales y NoSQL.
