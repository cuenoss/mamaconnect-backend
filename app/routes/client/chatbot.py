from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_async_session
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import get_conversation_history, generate_bot_reply

router = APIRouter(tags=["Client", "Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_async_session)):

    # get session
    session = await db.get(ChatSession, request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # save user message
    user_message = ChatMessage(
        session_id=request.session_id,
        sender="user",
        message=request.message
    )
    db.add(user_message)
    await db.commit()

    # get chat history
    history = await get_conversation_history(db, request.session_id)

    # generate bot reply
    reply = await generate_bot_reply(request.message, history)

    # save bot reply
    bot_message = ChatMessage(
        session_id=request.session_id,
        sender="bot",
        message=reply
    )
    db.add(bot_message)
    await db.commit()

    return ChatResponse(reply=reply)


@router.post("/session")
async def create_session(user_id: int, db: AsyncSession = Depends(get_async_session)):

    new_session = ChatSession(user_id=user_id)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session


@router.get("/session/{session_id}")
async def get_session_messages(session_id: int, db: AsyncSession = Depends(get_async_session)):

    statement = select(ChatMessage).where(ChatMessage.session_id == session_id)
    result = await db.execute(statement)
    messages = result.scalars().all()

    return messages