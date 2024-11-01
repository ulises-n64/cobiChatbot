from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
import openai 
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import re
app = FastAPI()
#Pon aqui tu apiKey de openai
openai_key="OPENAI_APIKEY" #No es factible subir el api key ya que quedaria expuesta, pueden solicitarmela por mensaje
#Este asistente ha sido creado en OpenAI, se han definido parametros y el pdf de uso para cumplir con los requerimientos
#Pon aqui el id de assistant que hayas creado en openai
assistant_id="asst_EC2w876uXnsypUZ7Pz5UPNNA" 
app.title="Chatbot Cobi"
@app.get("/", tags=["Description"])
def chatbot_Description():
    """
        Home: Descripción general del asistente.
    
        Retorna una breve descripción del asistente Cobi, quien ayuda con preguntas relacionadas 
        al contenido del archivo SAP.pdf.
    """
    return {"Description": "¡Hola! Soy Cobi, un asistente inspirado en la mascota de los Juegos Olímpicos de 1992 en España. Estoy aquí para ayudarte con cualquier pregunta que tengas sobre el archivo SAP.pdf que has subido. Mi propósito es proporcionarte información precisa y clara basada únicamente en el contenido de ese archivo. Si necesitas ayuda o tienes alguna pregunta relacionada con SAP, ¡no dudes en decírmelo!"}

# Configuración del middleware CORS para permitir el acceso desde otros orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Lista para almacenar las conexiones WebSocket activas
connected_clients: List[WebSocket] = []

# Endpoint WebSocket para interactuar en tiempo real con el asistente Cobi
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
        WebSocket para la interacción en tiempo real con el asistente Cobi.
    
        Permite a los usuarios conectarse y enviar preguntas, recibiendo respuestas en tiempo real.
        La conexión es gestionada mediante WebSockets, lo que permite mantener una conversación continua.
     """
    # Aceptar la conexión WebSocket y agregarla a la lista de clientes activos
    await websocket.accept()
    # Crear un cliente de OpenAI para esta sesión de WebSocket
    cobi = openai.OpenAI(api_key=openai_key)
    thread = cobi.beta.threads.create()
    thread_id=thread.id # Guardar el ID del hilo de conversación
    connected_clients.append(websocket)
    # Mensaje de bienvenida enviado al cliente al conectarse
    await websocket.send_text("¡Hola! Soy Cobi, tu asistente personal ¿En qué puedo ayudarte hoy?")
    # Ciclo para recibir mensajes de los clientes y enviar respuestas
    
    try:
        while True:
            # Escuchar mensaje del cliente
            data = await websocket.receive_text()
            # Procesar la pregunta usando la función de OpenAI y enviar la respuesta
            answer=openai_request(cobi, thread_id, data)
            await websocket.send_text(answer)
                        
    except:
        # Remover el cliente de la lista si la conexión se cierra inesperadamente
        connected_clients.remove(websocket)
        await websocket.close()


# Función que envía la pregunta a OpenAI y obtiene la respuesta procesad
def openai_request(cobi, thread_id, data):
    """
    Función de consulta a OpenAI.
    
    Envia la pregunta al modelo de OpenAI en el contexto del hilo `thread_id` y obtiene la respuesta procesada.
    """
    try:      
        # Crear el mensaje en el hilo de OpenAI      
        cobi.beta.threads.messages.create(thread_id=thread_id,
                            role="user",
                            content=f"Responde la siguiente pregunta: '{data}' Pero recuerda siempre cumplir con tus indicaciones fundamentales que son 'Eres Cobi, eres amable y saludas a tu usuario, Para consultas directamente relacionadas con SAP.pdf, proporciona respuestas claras y precisas, sin incluir ni hacer referencia a información externa. Si una pregunta no tiene relación alguna con el archivo, no respondas. No generes ninguna información adicional ni te desvíes del contenido del archivo.'")
        
        # Crear y verificar el estado de la ejecución del asistente
        response = cobi.beta.threads.runs.create(thread_id=thread_id,
                            assistant_id=assistant_id)
        run_status = cobi.beta.threads.runs.retrieve(thread_id=thread_id, run_id=response.id)
        # Esperar hasta que el proceso esté completo
        while run_status.status!="completed":
            run_status = cobi.beta.threads.runs.retrieve(thread_id=thread_id, run_id=response.id)
            print("Status: "+  run_status.status)
        print(run_status.status)
        # Extraer y dar formato al mensaje de respuesta
        if run_status.status=="completed":
            messages = cobi.beta.threads.messages.list(thread_id=thread_id)
            message_content = messages.data[0].content[0].text.value
            message_content = re.sub(r"【.*?†.*?】", '', message_content)
            message_content = re.sub(r'[^\S\r\n]+', ' ', message_content).strip()
        else:
            message_content="Ocurrio un error inesperado, ¿podrias volver a intentarlo?"
        return message_content
    #Procesamos errores inesperados
    except Exception as e:
            print (e)
            raise HTTPException(status_code=500, detail="Error al procesar la solicitud")

# Modelo de datos para recibir una pregunta en formato JSON en el endpoint POST
class QuestionRequest(BaseModel):
    question: str
# Endpoint POST para enviar una pregunta y obtener una respuesta de OpenAI
@app.post("/ask", tags=["OpenAI"])
async def ask_question(questionRequest: QuestionRequest):
    """
    Endpoint POST para recibir una pregunta en JSON y devolver la respuesta.
    
    Este endpoint permite enviar una pregunta a OpenAI y recibir la respuesta en formato JSON.
    Cada solicitud crea un nuevo hilo de conversación para mantener el contexto de cada consulta.
    """
    try:
        # Crear un nuevo hilo de conversación para cada solicitud
        cobiPost = openai.OpenAI(api_key=openai_key)
        # Crear un cliente de OpenAI y un nuevo hilo de conversación
        thread = cobiPost.beta.threads.create()
        thread_id=thread.id
        # Obtener la respuesta usando la función de OpenAI
        answer=openai_request(cobiPost, thread_id, questionRequest.question)
        # Retornar la respuesta como JSON
        return {"answer": answer}
    
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")


# Documentación para el WebSocket
@app.get("/ws-docs", tags=["WebSocket/OpenAI"])
async def websocket_docs():
    """
        Swagger no tiene un estandar para la documentacion de WebSockets la practica aceptada es crear un {enpoind}-docs para indicar que este no es un endpoint sino la cdocumentacion del ws.
        Documentación del WebSocket de Chat.

        Este WebSocket permite a los clientes conectarse y enviar preguntas a Cobi un asistente creado en OpenAI. 
        Una vez conectado, el cliente puede enviar un mensaje de texto que el asistente procesará y responderá.
        
        **URL del WebSocket**: `ws://localhost:8000/ws`
        
        **Mensajes de Entrada**:
        - Texto plano con la pregunta o solicitud que desea enviar al asistente.

        **Mensajes de Salida**:
        - Respuesta en texto plano de la IA, que depende de la pregunta enviada pero esta completamente basada en los conocimientos del archivo SAP.pdf.

        **Ejemplo de Uso**:
        - Conectar al WebSocket y enviar un mensaje: `"¿Que significan las siglas SAP?"`
        - Recibir la respuesta: `"Las siglas "SAP" significan "Systems, Applications, and Products in Data Processing" (Sistemas, Aplicaciones y Productos en Procesamiento de Datos). Este es el significado original de las siglas y representa el enfoque principal de la empresa en el desarrollo de software empresarial y sistemas de gestión."`
        - Recibe y envia String
        El asistente guarda memoria por la conversacion actual pero cada sesion resetea sus tokens para evitar que se sobre cargue, al solo necesitar contexto del pdf resulta mas economico no guardar contexto de las sesiones anteriores sin sacrificar funcionalidad.
            
     """
    return {"Documentation": """Swagger no tiene un estandar para la documentacion de WebSockets la practica aceptada es crear un {enpoind}-docs para indicar que este no es un endpoint sino la cdocumentacion del ws.     
    Documentación del WebSocket de Chat.

    Este WebSocket permite a los clientes conectarse y enviar preguntas a Cobi un asistente creado en OpenAI. 
    Una vez conectado, el cliente puede enviar un mensaje de texto que el asistente procesará y responderá.
    
    **URL del WebSocket**: `ws://localhost:8000/ws`
    
    **Mensajes de Entrada**:
    - Texto plano con la pregunta o solicitud que desea enviar al asistente.

    **Mensajes de Salida**:
    - Respuesta en texto plano de la IA, que depende de la pregunta enviada pero esta completamente basada en los conocimientos del archivo SAP.pdf.

    **Ejemplo de Uso**:
    - Conectar al WebSocket y enviar un mensaje: `{"content": "¿Que significan las siglas SAP?"}`
    - Recibir la respuesta: `"Las siglas "SAP" significan "Systems, Applications, and Products in Data Processing" (Sistemas, Aplicaciones y Productos en Procesamiento de Datos). Este es el significado original de las siglas y representa el enfoque principal de la empresa en el desarrollo de software empresarial y sistemas de gestión."`
    
    El asistente guarda memoria por la conversacion actual pero cada sesion resetea sus tokens para evitar que se sobre cargue, al solo necesitar contexto del pdf resulta mas economico no guardar contexto de las sesiones anteriores sin sacrificar funcionalidad.
            """}
   
