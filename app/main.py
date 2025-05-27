
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import List, Dict
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.future import select
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
def get_messages():
    return {"allMessages": messages_db}

@app.get("/messages/unread/{recipient}")
def get_unread_messages(recipient: str):
    unread_messages = [
        msg for msg in messages_db if msg["recipient"] == recipient and not msg["read"]
    ]
    for msg in unread_messages:
        msg["read"] = True  # Mark them as read
    return {"unread_messages": unread_messages}

@app.delete("/messages/{message_id}")
def delete_message(message_id: str):
    global messages_db
    original_length = len(messages_db)
    messages_db = [msg for msg in messages_db if msg["id"] != message_id]
    if len(messages_db) == original_length:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "Message deleted"}

@app.delete("/messages")
def delete_multiple_messages(request: DeleteManyRequest):
    global messages_db
    before = len(messages_db)
    messages_db = [msg for msg in messages_db if msg["id"] not in request.ids]
    deleted_count = before - len(messages_db)
    return {"status": f"Deleted {deleted_count} messages"}

@app.get("/messages/{recipient}")
def get_user_messages(
    recipient: str,
    start: int = Query(0, ge=0),
    stop: int = Query(10, ge=0)
):
    # Filter by recipient
    recipient_msgs = [msg for msg in messages_db if msg["recipient"] == recipient]
    # Sort by timestamp
    sorted_msgs = sorted(recipient_msgs, key=lambda x: x["timestamp"])
    # Return paginated slice
    return {"messages": sorted_msgs[start:stop]}

