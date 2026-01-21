
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import OllamaLLM
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import Dict

llm = OllamaLLM(
    model="gpt-oss:20b",
    temperature=0.7,
    num_predict=1024  # Permitir que se configure dinámicamente por petición
)
histories: Dict[str, ChatMessageHistory] = {}
sessions: Dict[str, RunnableWithMessageHistory] = {}

def get_session(session_id: str) -> RunnableWithMessageHistory:
    if session_id not in sessions:
        if session_id not in histories:
            from langchain_core.messages import SystemMessage
            histories[session_id] = ChatMessageHistory()
            histories[session_id].add_message(SystemMessage(
                content="Eres un asistente útil y preciso. Cuando se te pida traducir texto, debes proporcionar una traducción directa y precisa. Siempre debes dar una respuesta."
            ))
        sessions[session_id] = RunnableWithMessageHistory(
            runnable=llm,
            get_session_history=lambda s_id: histories[s_id]
        )
    return sessions[session_id]

def end_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    if session_id in histories:
        del histories[session_id]

