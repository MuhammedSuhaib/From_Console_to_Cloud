from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from models import Conversation, Message, UserContext
from database import get_session
from auth.jwt import get_current_user_id
from simple_agents.aagents import Todo_Agent
from agents import Runner, set_tracing_export_api_key, trace
import os
from typing import Optional

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize tracing globally
set_tracing_export_api_key(os.getenv('Tracing_key'))

@router.get("/{user_id}/history")
async def get_chat_history(
    user_id: str,
    conversation_id: Optional[int] = None,
    session: Session = Depends(get_session),
    auth_id: str = Depends(get_current_user_id),
):
    if auth_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    query = select(Message).where(Message.user_id == user_id)
    if conversation_id:
        query = query.where(Message.conversation_id == conversation_id)
    
    messages = session.exec(query.order_by(Message.created_at.asc())).all()
    return {"messages": [{"role": m.role, "content": m.content} for m in messages]}

@router.post("/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session),
    auth_id: str = Depends(get_current_user_id),
):
    if auth_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    body = await request.json()
    user_msg = body.get("message", "")
    conversation_id = body.get("conversation_id")

    if not conversation_id:
        conv = Conversation(user_id=user_id)
        session.add(conv)
        session.commit()
        session.refresh(conv)
        conversation_id = conv.id

    # 1. Fetch History from Neon
    existing_messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    # Map DB messages to format
    history = [{"role": m.role, "content": m.content} for m in existing_messages]

    # 2. Store current user message in Neon
    session.add(
        Message(conversation_id=conversation_id, user_id=user_id, role="user", content=user_msg)
    )
    session.commit()

    user_ctx = UserContext(name=user_id, uid=user_id)
    
    # 3. Run Agent with combined history and new message as the input list
    # This fixes the 'unexpected keyword argument message_history' error
    messages_to_process = history + [{"role": "user", "content": user_msg}]
    
    try:
        with trace(workflow_name="Focus AI Assistant", group_id=str(conversation_id)):
            result = await Runner.run(
                Todo_Agent,
                messages_to_process,
                context=user_ctx
            )
        
        ai_resp = result.final_output

        # 4. Store assistant response in Neon
        session.add(
            Message(
                conversation_id=conversation_id, user_id=user_id, role="assistant", content=ai_resp
            )
        )
        session.commit()

        return {"response": ai_resp, "conversation_id": conversation_id}
    except Exception as e:
        import logging
        logging.error(f"Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI processing failed")