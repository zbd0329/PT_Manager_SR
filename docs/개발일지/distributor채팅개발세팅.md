# Distributor 채팅 기능 개발 설정

## 1. API 명세서

### 1.1 채팅 페이지 렌더링 API
- **기능**: 채팅 페이지를 렌더링
- **Method**: GET
- **Endpoint**: `/distributor/chat`
- **Parameters**:
  - `room_id`: 채팅방 ID (query parameter)
  - `user_id`: 사용자 ID (query parameter)
- **응답**: HTML 페이지 (distributor_chat.html)

### 1.2 채팅방 목록 조회 API
- **기능**: 트레이너의 채팅방 목록을 조회
- **Method**: GET
- **Endpoint**: `/distributor/chat/rooms`
- **인증**: 트레이너 토큰 필요
- **응답**: HTML 페이지 (chat_rooms.html)
  ```json
  {
    "chat_rooms": [
      {
        "id": "pt_[session_id]",
        "member_name": "회원명",
        "last_activity": "YYYY-MM-DD HH:MM",
        "unread_count": 0
      }
    ]
  }
  ```

### 1.3 WebSocket 엔드포인트
- **기능**: 실시간 채팅을 위한 WebSocket 연결
- **Endpoint**: `/distributor/ws/chat/{room_id}`
- **메시지 형식**:
  ```json
  {
    "type": "chat|spread|system",
    "content": "메시지 내용",
    "user_id": "사용자 ID",
    "room_id": "방 ID"
  }
  ```

## 2. 기술 스택 및 구조

### 2.1 프론트엔드
- **Vue.js**: 채팅 UI 구현
  - 양방향 데이터 바인딩
  - 컴포넌트 기반 구조
  - Jinja2 템플릿과 통합

### 2.2 백엔드
- **FastAPI**: 웹 서버 및 WebSocket 구현
- **SQLAlchemy**: 데이터베이스 ORM
- **WebSocket**: 실시간 양방향 통신

### 2.3 파일 구조
```
app/
├── distributor/
│   ├── static/
│   │   ├── js/
│   │   │   ├── distributor_chat.js     # Vue.js 채팅 애플리케이션
│   │   │   └── vue.min.js              # Vue.js 라이브러리
│   │   └── css/
│   │       └── distributor_chat.css     # 채팅 스타일
│   ├── templates/
│   │   ├── distributor_chat.html        # 채팅 페이지
│   │   └── chat_rooms.html             # 채팅방 목록 페이지
│   └── api/
│       └── endpoints/
│           └── distributor_chat_endpoints.py  # 채팅 관련 API
```

## 3. 주요 구현 사항

### 3.1 채팅 관리자 (ChatManager)
```python
class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str)
    async def broadcast(self, message: str, room_id: str)
    def disconnect(self, websocket: WebSocket, room_id: str)
```

### 3.2 인증 처리
- 트레이너 인증: `verify_trainer` 미들웨어 사용
- 토큰 기반 인증: JWT 토큰 검증

### 3.3 데이터베이스 연동
- PT 세션과 연계한 채팅방 구현
- 트레이너-회원 관계 기반 채팅방 생성

## 4. 문제 해결 과정

### 4.1 모듈 Import 오류
1. `app.core.auth` 모듈 누락
   - 해결: `app.core.security`에서 인증 관련 함수 import

2. `app.db.session` 모듈 누락
   - 해결: `app.core.database`에서 `SessionLocal` import
   - 로컬에 `get_db` 함수 구현

### 4.2 라우터 설정
- 문제: URL 경로 이름 불일치
- 해결: 
  ```python
  router = APIRouter(prefix="/distributor", tags=["distributor"])
  ```

## 5. 보안 설정

### 5.1 채팅방 접근 제어
- 트레이너: 자신의 회원 채팅방만 접근 가능
- 회원: 자신의 트레이너와의 채팅방만 접근 가능

### 5.2 WebSocket 보안
- 룸 기반 메시지 격리
- 사용자 인증 확인
- 메시지 유효성 검사

## 6. 향후 개선 사항

1. 메시지 영구 저장 구현
2. 읽지 않은 메시지 카운트 실제 구현
3. 채팅방 입장/퇴장 알림 개선
4. 메시지 전송 실패 처리
5. 재연결 메커니즘 강화 