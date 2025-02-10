from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Set, List
from datetime import datetime
import json

from app.core.security import verify_token, verify_trainer
from app.models.user_model import User
from app.models.pt_session import PTSession
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

router = APIRouter(
    prefix="/chat",  # /api/v1/distributor는 main.py에서 처리
    tags=["distributor"]
)
templates = Jinja2Templates(directory="app/distributor/templates")

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 채팅방 관리를 위한 클래스
class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        self.active_connections[room_id].remove(websocket)
        if not self.active_connections[room_id]:
            del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

chat_manager = ChatManager()

# 채팅 페이지 렌더링
@router.get("/chat", response_class=HTMLResponse, name="get_chat_page")
async def get_chat_page(request: Request, room_id: str, user_id: str):
    return templates.TemplateResponse(
        "distributor_chat.html",
        {"request": request, "room_id": room_id, "user_id": user_id}
    )

# 트레이너의 채팅방 목록 조회
@router.get("/chat/rooms", response_class=HTMLResponse, name="get_chat_rooms")
async def get_chat_rooms(
    request: Request,
    token: str = Depends(verify_trainer),
    db: Session = Depends(get_db)
):
    # 토큰에서 트레이너 정보 추출
    trainer_data = verify_token(token)
    if not trainer_data:
        raise HTTPException(status_code=403, detail="트레이너만 접근 가능합니다.")
    
    # 트레이너와 연결된 회원들의 PT 세션 조회
    pt_sessions = db.query(PTSession).filter(
        PTSession.trainer_id == trainer_data["sub"]
    ).all()
    
    # 채팅방 정보 구성
    chat_rooms = []
    for session in pt_sessions:
        member = session.member
        chat_rooms.append({
            "id": f"pt_{session.id}",
            "member_name": member.name,
            "last_activity": session.updated_at.strftime("%Y-%m-%d %H:%M"),
            "unread_count": 0
        })
    
    return templates.TemplateResponse(
        "chat_rooms.html",
        {
            "request": request,
            "chat_rooms": chat_rooms,
            "current_user": trainer_data
        }
    )

# WebSocket 연결
@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await chat_manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # 메시지를 해당 방의 모든 연결된 클라이언트에게 브로드캐스트
            await chat_manager.broadcast(json.dumps(message), room_id)
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, room_id)
        disconnect_message = {
            "type": "system",
            "content": "사용자가 채팅방을 나갔습니다.",
            "room_id": room_id
        }
        await chat_manager.broadcast(json.dumps(disconnect_message), room_id) 