from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict
import json
from ..auth.jwt import verify_token_simple
from ..auth.models import User
from ..db import get_db
from . import services, schema


class ConnectionManager:
    def __init__(self):
        # Store active connections: {user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected to chat")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected from chat")
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
            except:
                # Connection is likely closed, remove it
                self.disconnect(user_id)
    
    async def send_message_to_conversation(self, message_data: dict, sender_id: int, receiver_id: int):
        # Send to receiver if online
        await self.send_personal_message(json.dumps(message_data), receiver_id)
        
        # Send confirmation back to sender
        confirmation = {
            "type": "message_sent",
            "message": message_data
        }
        await self.send_personal_message(json.dumps(confirmation), sender_id)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    
    # Create a database session for this connection
    from ..db import SessionLocal
    db = SessionLocal()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "send_message":
                # Create message in database
                message_create = schema.MessageCreate(
                    content=message_data["content"],
                    receiver_id=message_data["receiver_id"]
                )
                
                # Save to database
                db_message = await services.send_message(db, message_create, user_id)
                
                # Prepare message for broadcasting
                broadcast_data = {
                    "type": "new_message",
                    "message": {
                        "id": db_message.id,
                        "content": db_message.content,
                        "sender_id": db_message.sender_id,
                        "conversation_id": db_message.conversation_id,
                        "created_at": db_message.created_at.isoformat(),
                        "is_read": db_message.is_read
                    }
                }
                
                # Send message to receiver and confirmation to sender
                await manager.send_message_to_conversation(
                    broadcast_data, user_id, message_data["receiver_id"]
                )
            
            elif message_data["type"] == "mark_read":
                # Mark message as read
                await services.mark_message_as_read(db, message_data["message_id"], user_id)
                
                # Send read confirmation
                read_confirmation = {
                    "type": "message_read",
                    "message_id": message_data["message_id"]
                }
                await manager.send_personal_message(json.dumps(read_confirmation), user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {str(e)}")
        manager.disconnect(user_id)
    finally:
        db.close()
        manager.disconnect(user_id)