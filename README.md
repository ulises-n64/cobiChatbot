# Chatbot Cobi

¡Bienvenido a Chatbot Cobi! Este es un asistente virtual inspirado en la mascota de los Juegos Olímpicos de Barcelona 1992, diseñado para responder preguntas específicas basadas en el contenido del archivo **SAP.pdf**. Cobi está desarrollado con FastAPI en el backend y React en el frontend.

## Descripción

Cobi es un chatbot impulsado por inteligencia artificial que responde preguntas exclusivamente relacionadas con el archivo **SAP.pdf**. Esto es útil para extraer información específica o responder dudas relacionadas con el documento, manteniendo una conversación interactiva y amigable.

## Características

- **Interfaz interactiva**: Permite al usuario hacer preguntas relacionadas con el archivo SAP.pdf y recibir respuestas detalladas.
- **Backend robusto**: Desarrollado con FastAPI, maneja conexiones WebSocket para interacciones en tiempo real y endpoints HTTP para interacciones individuales.
- **Frontend moderno**: Creado en React, proporciona una interfaz intuitiva para la experiencia del usuario.

## Estructura del Proyecto
La estructura del proyecto es la siguiente:

- chatbot_project/
  - backend/                   # Código del backend (FastAPI)
    - main.py                  # Código principal de FastAPI
    - requirements.txt         # Dependencias del backend
    - Otros archivos de dependencias
  - frontend/                  # Código del frontend (React)
    - public/                  # Archivos públicos de React
    - src/                     # Código fuente de React
    - package.json             # Dependencias del frontend
    - Otros archivos de dependencias
  - README.md                  # Documentación del proyecto
## Configuración del Proyecto

### 1. Clonar el Repositorio

Clona el repositorio en tu máquina local:

```bash
git clone https://github.com/tu-usuario/chatbot_project.git
cd chatbot_project
```
Configura el backend

cd backend

uvicorn main:app --reload

y para arrancar el servidor 

fastapi dev main.py

Documentacion en: [Documentacion](http://localhost:8000/docs)

Configura el frontend

cd ../frontend

npm install

Corre el servidor en pruebas

npm run dev

Chat en 
[Chat](http://localhost:5173)

### Nota Puede que los puertos esten ocupados revisa sobre que puertos se despliega cada aplicacion