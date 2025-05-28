
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import List, Dict
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from models import Message
from database import get_db

#Define sent message 
class MessageIn(BaseModel):
    recipient: str
    message: str
    
class DeleteManyRequest(BaseModel):
    ids: List[str]

#define an in memory storage for testing
messages_db: List[Dict] = []


#Create FastAPI app
app = FastAPI()

#Define get on root 
@app.get("/")
def root():
    return {"message": "Message service is up and running."}

@app.post("/messages")
async def submit_message(msg: MessageIn, db: AsyncSession = Depends(get_db)):
    new_message = Message(
        id=str(uuid4()),
        recipient=msg.recipient,
        message=msg.message,
        timestamp=datetime.utcnow(),
        read=False,
    )
    db.add(new_message)
    await db.commit()
    return {"status": "Message stored", "id": new_message.id}

@app.get("/message/")
async def get_messages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message))
    messages = result.scalars().all()
    # Optional: convert SQLAlchemy objects to dict for JSON serialization
    return {"allMessages": [ 
        {
            "recipient": msg.recipient,
            "message": msg.message
        } for msg in messages
    ]}

@app.get("/messages/unread/{recipient}")
async def get_unread_messages(recipient: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message).where(
            Message.recipient == recipient,
            Message.read == False
        )
    )
    messages = result.scalars().all()
    return {
        "unreadMessages": [
            {
                "id": msg.id,
                "recipient": msg.recipient,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            }
            for msg in messages
        ]
    }

@app.delete("/messages/{message_id}")
async def delete_message(message_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalars().first()

    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    await db.delete(message)
    await db.commit()

    return {"status": "Message deleted"}

@app.delete("/messages")
async def delete_multiple_messages(request: DeleteManyRequest, db: AsyncSession = Depends(get_db)):
    if not request.ids:
        raise HTTPException(status_code=400, detail="No message IDs provided")

    stmt = delete(Message).where(Message.id.in_(request.ids))
    result = await db.execute(stmt)
    await db.commit()

    return {"status": f"Deleted {result.rowcount} message(s)"}

    return {"status": f"Deleted {result.rowcount} message(s)"}

@app.get("/messages/{recipient}")
async def get_user_messages(
    recipient: str,
    start: int = Query(0, ge=0),
    stop: int = Query(10, ge=0),
    db: AsyncSession = Depends(get_db)
):
    if stop <= start:
        raise HTTPException(status_code=400, detail="`stop` must be greater than `start`")

    stmt = (
        select(Message)
        .where(Message.recipient == recipient)
        .order_by(Message.timestamp)
        .offset(start)
        .limit(stop - start)
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    return {
        "messages": [
            {
                "id": msg.id,
                "recipient": msg.recipient,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "read": msg.read,
            }
            for msg in messages
        ]
    }

