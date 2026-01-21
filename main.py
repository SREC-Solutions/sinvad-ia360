from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest
from chatbot import get_session, end_session, histories  # importa histories
from db import log_conversation
import re
import asyncio
import logging
import os
from datetime import datetime

# Configurar logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/app.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI()

# Solo permite estos dominios
origins = [
    "https://tudominio.com",
    "https://otrodominio.com",
    "http://localhost",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(req: ChatRequest):
    session = get_session(req.session_id)
    histories[req.session_id].add_user_message(req.message)

    # Construye el historial como diálogo
    dialogo = ""
    for m in histories[req.session_id].messages[:-1]:
        if m.type == "human":
            dialogo += f"Usuario: {m.content}\n"
        elif m.type == "ai":
            dialogo += f"Asistente: {m.content}\n"
    dialogo += f"Usuario: {req.message}\n"

    prompt = dialogo

    try:
        logging.info(f"Procesando solicitud para session_id: {req.session_id}")
        logging.debug(f"Prompt enviado al modelo: {prompt}")
        
        response = session.invoke(
            prompt,
            config={"configurable": {"session_id": req.session_id, "num_predict": int(req.max_token)}}
        )
        
        logging.info(f"Tipo de respuesta: {type(response)}")
        logging.info(f"Contenido de respuesta raw: {response}")

        # Si la respuesta es un dict, extrae el mensaje
        if isinstance(response, dict) and "message" in response:
            message = str(response["message"])
            logging.debug("Respuesta extraída del diccionario")
        else:
            # Si la respuesta no es un diccionario, usamos la respuesta directamente
            message = str(response).strip()
            logging.debug("Respuesta convertida directamente a string")
            
        logging.info(f"Mensaje procesado: {message}")
            
        # Si el mensaje está vacío, proporcionar una respuesta por defecto
        if not message or message.isspace():
            logging.warning("Se recibió una respuesta vacía del modelo")
            message = "Lo siento, hubo un problema al procesar tu solicitud. Por favor, intenta de nuevo."

        histories[req.session_id].add_ai_message(message)
        log_conversation(req.session_id, req.message, message)
        
    except Exception as e:
        logging.error(f"Error al procesar la respuesta: {str(e)}", exc_info=True)
        message = "Ha ocurrido un error al procesar tu solicitud. Por favor, intenta de nuevo."

    response_dict = {"message": message}
    return response_dict

@app.post("/stream-chat")
async def stream_chat(req: ChatRequest):
    session = get_session(req.session_id)
    histories[req.session_id].add_user_message(req.message)

    # Construye el historial como diálogo
    dialogo = ""
    for m in histories[req.session_id].messages[:-1]:
        if m.type == "human":
            dialogo += f"Usuario: {m.content}\n"
        elif m.type == "ai":
            dialogo += f"Asistente: {m.content}\n"
    dialogo += f"Usuario: {req.message}\n"

    async def generate():
        full_response = ""
        stream = session.astream(
            dialogo,
            config={"configurable": {"session_id": req.session_id, "num_predict": req.max_token}}
        )
        
        async for chunk in stream:
            if isinstance(chunk, dict) and "message" in chunk:
                content = chunk["message"]
            else:
                content = str(chunk)
            
            if content and not content.isspace():
                content = content.strip()
                full_response += content
                yield f"data: {content}\n\n"
        
        # Al finalizar, guardamos la respuesta completa en el historial y la BD
        histories[req.session_id].add_ai_message(full_response)
        log_conversation(req.session_id, req.message, full_response)
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.post("/end-session")
async def terminate(req: ChatRequest):
    end_session(req.session_id)
    return {"status": "session ended"}
