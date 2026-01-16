from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func
from models import Conversation, Message, UserContext
from database import get_session, engine
from auth.jwt import get_current_user_id
from todo_agent.todo_agent import Todo_Agent
from agents import Runner, set_tracing_export_api_key, trace
from openai.types.responses import ResponseTextDeltaEvent
import os
import json
import openai
import sqlalchemy
from typing import Optional

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize tracing globally
set_tracing_export_api_key(os.getenv('Tracing_key'))

@router.get("/{user_id}/conversations")
async def get_all_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    auth_id: str = Depends(get_current_user_id),
):
    if auth_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get all conversations for the user
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    # For each conversation, get the first message as preview
    result = []
    for conv in conversations:
        # Get the first message in the conversation as preview
        first_message = session.exec(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
            .limit(1)
        ).first()

        # Count total messages in conversation
        message_count = session.exec(
            select(func.count(Message.id))
            .where(Message.conversation_id == conv.id)
        ).one()

        result.append({
            "id": conv.id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "preview": first_message.content[:50] + "..." if first_message and len(first_message.content) > 50 else (first_message.content if first_message else "Empty conversation"),
            "message_count": message_count
        })

    return {"conversations": result}


@router.delete("/{user_id}/conversations/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: int,
    session: Session = Depends(get_session),
    auth_id: str = Depends(get_current_user_id),
):
    if auth_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get the conversation to ensure it belongs to the user
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this conversation")

    # Delete all messages in the conversation first (due to foreign key constraint)
    messages_to_delete = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
    ).all()

    for message in messages_to_delete:
        session.delete(message)

    # Delete the conversation
    session.delete(conversation)
    session.commit()

    return {"message": "Conversation deleted successfully"}


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

    # Fetch real name from the 'user' table managed by Better Auth
    db_user = session.execute(
        sqlalchemy.text('SELECT name FROM "user" WHERE id = :uid'),
        {"uid": user_id}
    ).fetchone()
    user_name = db_user[0] if db_user else "User"

    user_ctx = UserContext(name=user_name, uid=user_id)
    
    # 3. Prepare combined history and new message
    messages_to_process = history + [{"role": "user", "content": user_msg}]
    
    # Capture IDs for the generator closure
    target_conv_id = conversation_id
    target_user_id = user_id

    async def event_generator():
        full_response = ""
        try:
            with trace(workflow_name="Focus AI Assistant", group_id=str(target_conv_id)):
                # Runner.run_streamed returns a RunResultStreaming object
                result = Runner.run_streamed(
                    Todo_Agent,
                    messages_to_process,
                    context=user_ctx
                )
                
                # Iterate over the events using .stream_events()
                async for event in result.stream_events():
                    # Detect Tool Execution Status - Fix: use event.item.name
                    if event.type == "run_item_stream_event" and event.name == "tool_called":
                        t_name = getattr(event.item, 'name', 'task')
                        yield f"data: {json.dumps({'tool': t_name})}\n\n"

                    # Detect Text Chunks
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        chunk = event.data.delta
                        if chunk:
                            full_response += chunk
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # 4. Store assistant response in Neon after stream completes
            with Session(engine) as new_session:
                new_session.add(
                    Message(
                        conversation_id=target_conv_id, 
                        user_id=target_user_id, 
                        role="assistant", 
                        content=full_response
                    )
                )
                new_session.commit()
            
            yield f"data: {json.dumps({'done': True, 'conversation_id': target_conv_id})}\n\n"

        except openai.RateLimitError:
            yield f"data: {json.dumps({'error': 'Gemini quota exceeded (429). Please wait a moment.'})}\n\n"
        except Exception as e:
            import logging
            logging.error(f"Streaming Error: {str(e)}")
            yield f"data: {json.dumps({'error': 'AI processing failed'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")