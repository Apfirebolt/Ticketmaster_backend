from fastapi import WebSocket, WebSocketDisconnect
from typing import Any, Dict, Set
import json
from datetime import datetime
from . import services, schema


class ConnectionManager:
    def __init__(self) -> None:
        # Store active connections: {user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # Store user presence info: {user_id: {last_seen, status}}
        self.user_presence: Dict[int, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Update presence status
        self.user_presence[user_id] = {
            "status": "online",
            "last_seen": datetime.utcnow().isoformat(),
            "connected_at": datetime.utcnow().isoformat()
        }
        
        print(f"User {user_id} connected to chat")
        
        # Broadcast user came online to all other connected users
        await self.broadcast_presence_update(user_id, "online")
    
    def disconnect(self, user_id: int) -> None:
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
            # Update presence status to offline
            self.user_presence[user_id] = {
                "status": "offline",
                "last_seen": datetime.utcnow().isoformat()
            }
            
            print(f"User {user_id} disconnected from chat")
            
            # Broadcast user went offline to all other connected users
            # We need to do this synchronously since the user is disconnecting
            import asyncio
            asyncio.create_task(self.broadcast_presence_update(user_id, "offline"))
    
    def get_online_users(self) -> Set[int]:
        """Get list of currently online user IDs"""
        return set(self.active_connections.keys())
    
    def get_user_presence(self, user_id: int) -> dict[str, Any]:
        """Get presence info for a specific user"""
        if user_id in self.active_connections:
            return {
                "user_id": user_id,
                "status": "online",
                "last_seen": self.user_presence.get(user_id, {}).get("last_seen"),
                "connected_at": self.user_presence.get(user_id, {}).get("connected_at")
            }
        else:
            presence_info = self.user_presence.get(user_id, {})
            return {
                "user_id": user_id,
                "status": "offline", 
                "last_seen": presence_info.get("last_seen")
            }
    
    async def broadcast_presence_update(self, user_id: int, status: str) -> None:
        """Broadcast presence update to all connected users"""
        presence_update = {
            "type": "presence_update",
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        message = json.dumps(presence_update)
        
        # Send to all connected users except the user whose status changed
        for connected_user_id, websocket in list(self.active_connections.items()):
            if connected_user_id != user_id:
                try:
                    await websocket.send_text(message)
                except:
                    # Connection is likely closed, remove it
                    self.disconnect(connected_user_id)
    
    async def send_personal_message(self, message: str, user_id: int) -> None:
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
            except:
                # Connection is likely closed, remove it
                self.disconnect(user_id)
    
    async def send_message_to_conversation(self, message_data: dict[str, Any], sender_id: int, receiver_id: int) -> None:
        # Send to receiver if online
        await self.send_personal_message(json.dumps(message_data), receiver_id)
        
        # Send confirmation back to sender
        confirmation = {
            "type": "message_sent",
            "message": message_data
        }
        await self.send_personal_message(json.dumps(confirmation), sender_id)
    
    async def send_online_users_list(self, user_id: int) -> None:
        """Send list of online users to a specific user"""
        online_users = []
        for online_user_id in self.get_online_users():
            if online_user_id != user_id:  # Don't include self
                presence_info = self.get_user_presence(online_user_id)
                online_users.append(presence_info)
        
        online_users_message = {
            "type": "online_users",
            "users": online_users,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(json.dumps(online_users_message), user_id)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: int) -> None:
    await manager.connect(websocket, user_id)
    
    # Send initial online users list to the newly connected user
    await manager.send_online_users_list(user_id)
    
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
            
            elif message_data["type"] == "get_online_users":
                # Send current online users list
                await manager.send_online_users_list(user_id)
            
            elif message_data["type"] == "ping":
                # Update last seen timestamp for presence
                manager.user_presence[user_id]["last_seen"] = datetime.utcnow().isoformat()
                
                # Send pong response
                pong_response = {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_personal_message(json.dumps(pong_response), user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {str(e)}")
        manager.disconnect(user_id)
    finally:
        db.close()
        manager.disconnect(user_id)