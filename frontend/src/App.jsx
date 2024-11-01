import { useEffect, useState } from "react";

// Crear instancia de WebSocket directamente
export default function App() {
  const [ws, setWs] = useState(null); // Estado para almacenar la conexión WebSocket
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false); // Estado para manejar la carga
  const [error, setError] = useState(null); // Estado para manejar errores

  useEffect(() => {
    // Crear conexión WebSocket solo una vez
    const socket = new WebSocket("ws://localhost:8000/ws");
    setWs(socket);
    
    console.log(socket)
    console.log("redy "+ socket.readyState)
    // Configurar recepción de mensajes
    socket.onmessage = (event) => {
      const newMessage = {
        body: event.data,
        from: "Server",
      };
      setMessages((prevMessages) => [newMessage, ...prevMessages]);
      setIsLoading(false); // Detener la animación de carga cuando llega la respuesta
      setError(null); // Reiniciar el estado de error al recibir respuesta
    };

    // Manejar cierre de conexión
    socket.onclose = () => {
      setError("Intentando establecer la conexión, si toma demasiado tiempo intente recargar la página.");
      setIsLoading(false); // Detener la animación de carga en caso de cierre
    };

    // Limpiar la conexión al desmontar el componente
    return () => socket.close();
  }, []);

  const sendMessage = () => {
    if (!message.trim()) return; // Evitar enviar mensajes vacíos

    const newMessage = {
      body: message,
      from: "Me",
    };
    setMessages((prevMessages) => [newMessage, ...prevMessages]);
    setIsLoading(true); // Activa el estado de carga hasta que llegue la respuesta del servidor
    setMessage("");

    // Enviar mensaje al servidor WebSocket
    ws.send(message);

    // Iniciar temporizador para mostrar error si la respuesta tarda demasiado
    const timeoutId = setTimeout(() => {
      setIsLoading(false);
      setError("La respuesta está tardando demasiado. Intente nuevamente.");
    }, 120000); // 120,000 ms = 2 minutos

    // Limpiar temporizador si llega la respuesta antes de los 2 minutos
    ws.onmessage = (event) => {
      const newMessage = {
        body: event.data,
        from: "Server",
      };
      setMessages((prevMessages) => [newMessage, ...prevMessages]);
      setIsLoading(false);
      setError(null);
      clearTimeout(timeoutId); // Limpiar el temporizador
    };
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      event.preventDefault(); // Evitar el comportamiento por defecto de Enter
      sendMessage(); // Llama a la función para enviar el mensaje
    }
  };

  return (
    <div className="h-screen w-screen bg-zinc-800 text-white flex items-center justify-center scroll-p-0">
      <form
        onSubmit={(e) => {
          e.preventDefault(); // Evitar el envío del formulario por defecto
          sendMessage(); // Llama a la función para enviar el mensaje
        }}
        className="bg-zinc-900 p-4 relative w-full max-w-lg h-full flex flex-col justify-between"
      >
        <img src="Cobi.png" alt="" className="w-12 h-12 absolute top-2 right-2" />
        <h1 className="text-2xl font-bold my-2">Chatbot Cobi</h1>

        <ul className="h-[80%] w-full overflow-y-auto mt-4 flex flex-col-reverse bg-zinc-900 rounded-lg scroll-p-0 p-2">
          {messages.map((msg, index) => (
            <li
              key={index}
              className={`my-2 p-3 rounded-lg max-w-xs ${
                msg.from === "Me" ? "bg-sky-700 text-right ml-auto" : "bg-gray-700 text-left"
              }`}
            >
              {msg.body}
            </li>
          ))}

          
        </ul>

        {/* Mostrar mensaje de error si hay algún problema */}
        {/* {error && (
          <div className={`my-2 p-3 bg-red-600 rounded-lg text-left text-gray-200 text-sm italic ${
                socket.close === "true" ? "" : "hidden"
              } `}>
            {error}
          </div>
        )} */}
        {error && (
          <div className={`my-2 p-3 bg-red-600 rounded-lg text-left text-gray-200 text-sm italic ${true? "":"hidden"}`}
              >
            {error}
          </div>
        )}
{/* Mostrar animación de "Escribiendo..." cuando se está esperando respuesta */}
{isLoading && (
            <li className="my-2 p-3 bg-gray-700 rounded-lg max-w-xs text-left text-gray-400 italic flex items-center space-x-2">
              <img
                src="Cobi.png"
                alt="Cargando"
                className="w-6 h-6 animate-spin"
              />
              <span>Procesando...</span>
            </li>
          )}
        <div className="flex items-center mt-4 w-full">
          <input
            name="message"
            type="text"
            placeholder="Escribe tu mensaje..."
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress} // Maneja el evento de tecla
            className={`border-2 border-gray-600 p-3 w-full rounded-l-lg text-black focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              isLoading ? "opacity-50" : ""
            }`}
            value={message}
            autoFocus
          />
          <button
            type="button" // Cambia a botón de tipo "button" para evitar el envío del formulario
            onClick={sendMessage} // Llama a la función para enviar el mensaje
            className="p-3 bg-blue-600 text-white rounded-r-lg flex justify-center items-center hover:bg-blue-700"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 12h16m-8 8l8-8-8-8" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}
