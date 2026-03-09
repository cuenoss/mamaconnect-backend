# app/services/rag_service.py
from app.rag.pregnancy_rag_assistant import PregnancyRAGAssistant

# Singleton assistant instance to avoid reloading model every request
_assistant_instance = None

def get_assistant():
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = PregnancyRAGAssistant()
        _assistant_instance.initialise()
    return _assistant_instance


def get_rag_response(question: str, user_profile: dict) -> str:
    """
    Call the RAG assistant with the user question and profile.
    """
    assistant = get_assistant()
    return assistant.ask(question, user_profile)