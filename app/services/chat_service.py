from app.rag.pregnancy_rag_assistant import PregnancyRAGAssistant
from app.models import ChatMessage
from sqlmodel import select

# Initialize a single RAG assistant instance
rag_assistant = PregnancyRAGAssistant()
rag_assistant.initialise()


async def get_conversation_history(db, session_id: int):
    """Retrieve conversation history for a session."""
    statement = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp)
    result = await db.execute(statement)
    messages = result.scalars().all()

    history = []
    for msg in messages:
        history.append({
            "role": "user" if msg.sender == "user" else "assistant",
            "content": msg.message
        })

    return history


async def generate_bot_reply(user_message: str, history: list, user_profile: dict = None):
    """
    Generate dynamic answer using PregnancyRAGAssistant.

    Args:
        user_message: question from the user
        history: conversation history
        user_profile: optional dictionary with pregnancy info
                      {"pregnancy_week": int, "trimester": int, "allergies": [], "illnesses": []}

    Returns:
        str: generated reply
    """
    if user_profile is None:
        # default profile if none provided
        user_profile = {"pregnancy_week": 20, "trimester": 2, "allergies": [], "illnesses": []}

    try:
        # Combine history messages into a single context string for RAG (optional)
        context_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])

        # Ask RAG assistant
        reply = rag_assistant.ask(user_message, user_profile)
        return reply

    except Exception as e:
        print(f"RAG service error: {e}")
        # fallback message
        return (
            "I'm here to help with pregnancy-related questions. "
            "Ask me about symptoms, nutrition, prenatal care, exercise, or baby development. "
            "Please remember this chat does not replace professional medical advice."
        )