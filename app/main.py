
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import List, Dict

#Define sent message 
class MessageIn(BaseModel):
    recipient: str
    message: str

#define an in memory storage for testing
messages_db: List[Dict] = []


#Create FastAPI app
app = FastAPI()

#Define get on root 
@app.get("/")
def root():
    return {"message": "Message service is up and running."}

#define post on messages
@app.post("/messages")
def submit_message(msg: MessageIn):
    new_message = {
        "id": str(uuid4()),
        "recipient": msg.recipient,
        "message": msg.message,
        "timestamp": datetime.utcnow().isoformat(),
        "read": False
    }
    messages_db.append(new_message)
    return {"status": "Message stored", "id": new_message["id"]}

@app.get("/messages/unread/{recipient}")
def get_unread_messages(recipient: str):
    unread_messages = [
        msg for msg in messages_db if msg["recipient"] == recipient and not msg["read"]
    ]
    for msg in unread_messages:
        msg["read"] = True  # Mark them as read
    return {"unread_messages": unread_messages}

