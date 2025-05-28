
from fastapi import FastAPI, Depends, HTTPException, Response, Query
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import List
from sqlalchemy.future import select
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from models import Message, User
from database import get_db
from sqlalchemy.exc import IntegrityError

#Define sent message 
class MessageIn(BaseModel):
    sender_username: str
    recipient_username: str
    message: str
    
class UserIn(BaseModel):
    username: str
    email: str
    phone_number: str
    address: str
    
class DeleteManyRequest(BaseModel):
    ids: List[str]

async def get_userID_by_username(username: str, db: AsyncSession) -> str:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    return user.id

#Create FastAPI app
app = FastAPI()

@app.head("/", tags=["Root"])
async def head_root():
    return Response(status_code=200)

#Define get on root 
@app.get("/", tags=["Root"])
def root():
    return {"message": "Message service is up and running."}

@app.post("/users", tags=["Admin"])
async def add_user(user: UserIn, db: AsyncSession = Depends(get_db)):
    # Lookup sender user by username
    
    new_user = User(
        id=str(uuid4()),
        email=user.email,
        address=user.address,
        phone_number=user.phone_number,
        username=user.username
    )
    
    db.add(new_user)
    try: 
        await db.commit() 
        return {"status": "User created", "username": new_user.username}
    except IntegrityError: 
        await db.rollback()
        raise HTTPException(
            status_code = 400,
            detail = "Username already taken")

@app.get("/messages/", tags=["Admin"])
async def get_messages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message))
    messages = result.scalars().all()
    return {"allMessages": [ 
        {
            "sender": msg.sender_id,
            "recipient": msg.recipient_id,
            "message": msg.message
        } for msg in messages
    ]}

@app.post("/users/{username}/messages/send", tags=["User"])
async def submit_message(msg: MessageIn, db: AsyncSession = Depends(get_db)):
    # Lookup sender user by username
    if msg.sender_username == msg.recipient_username:
        raise HTTPException(status_code=404, detail="Messages can only be sent to others users!")
    
    senderID = await get_userID_by_username(msg.sender_username, db)
        
    recipientID = await get_userID_by_username(msg.recipient_username, db)
    
    new_message = Message(
        id=str(uuid4()),
        sender_id=senderID,
        recipient_id=recipientID,
        message=msg.message,
        timestamp=datetime.utcnow(),
        read=False,
    )

    db.add(new_message)
    await db.commit()

    return {"status": "Message sent from " + msg.sender_username + " to " + msg.recipient_username}

@app.get("/users/{username}/messages/unread", tags=["User"])
async def get_unread_messages(username: str, db: AsyncSession = Depends(get_db)):
    userID = await get_userID_by_username(username, db)
    
    result = await db.execute(
        select(Message).where(
            Message.recipient_id == userID,
            Message.read == False
        )
    )
       
    messages = result.scalars().all()
    return {
        "unreadMessages": [
            {
                "id": msg.id,
                "sender": msg.sender_id,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            }
            for msg in messages
        ]
    }

@app.patch("/users/{username}/messages/read", tags=["User"])
async def mark_messages_read(username: str, db: AsyncSession = Depends(get_db)):
    userID = await get_userID_by_username(username, db)
        
    await db.execute(
        update(Message)
        .where(Message.recipient_id == userID, Message.read == False)
        .values(read=True)
    )
    await db.commit()

    return {"status": "Messages marked as read"}
"""
#Single Delete Call
@app.delete("/messages/{message_id}", tags=["User"])
async def delete_message(message_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalars().first()

    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    await db.delete(message)
    await db.commit()

    return {"status": "Message deleted"}
"""

@app.delete("/users/{username}/messages", tags=["User"])
async def delete_multiple_messages(request: DeleteManyRequest, db: AsyncSession = Depends(get_db)):
    if not request.ids:
        raise HTTPException(status_code=400, detail="No message IDs provided")

    stmt = delete(Message).where(Message.id.in_(request.ids))
    result = await db.execute(stmt)
    await db.commit()

    return {"status": f"Deleted {result.rowcount} message(s)"}

    return {"status": f"Deleted {result.rowcount} message(s)"}

@app.get("/users/{username}/messages", tags=["User"])
async def get_user_messages(
    username: str,
    start: int = Query(0, ge=0),
    stop: int = Query(10, ge=0),
    db: AsyncSession = Depends(get_db)
):
    if stop <= start:
        raise HTTPException(status_code=400, detail="`stop` must be greater than `start`")
    
    userID = await get_userID_by_username(username, db)
    
    

    stmt = (
        select(Message)
        .where(Message.recipient_id == userID)
        .order_by(Message.timestamp.desc())
        .offset(start)
        .limit(stop - start)
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    return {
        "messages": [
            {
                "message_id": msg.id,
                "recipient": msg.recipient_id,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "read": msg.read,
            }
            for msg in messages
        ]
    }

