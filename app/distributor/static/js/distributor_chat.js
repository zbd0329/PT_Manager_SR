new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],  // Jinja2와의 충돌을 피하기 위해 구분자 변경
    data: {
        messages: [],
        newMessage: '',
        room_id: '',
        user_id: '',
        showDialog: false,
        spreadAmount: 0,
        spreadCount: 0,
        ws: null
    },
    created() {
        // URL에서 room_id와 user_id 가져오기
        const urlParams = new URLSearchParams(window.location.search);
        this.room_id = urlParams.get('room_id');
        this.user_id = urlParams.get('user_id');
        
        // WebSocket 연결
        this.connectWebSocket();
    },
    methods: {
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.room_id}`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.ws.onclose = () => {
                // 연결이 끊어지면 3초 후 재연결 시도
                setTimeout(() => this.connectWebSocket(), 3000);
            };
        },
        
        handleMessage(data) {
            if (data.type === 'chat') {
                this.messages.push({
                    id: Date.now(),
                    user_id: data.user_id,
                    content: data.content,
                    timestamp: new Date().toLocaleTimeString(),
                    type: 'chat'
                });
            } else if (data.type === 'spread') {
                this.messages.push({
                    id: Date.now(),
                    user_id: data.user_id,
                    content: `${data.amount}원을 ${data.count}명에게 뿌렸습니다.`,
                    token: data.token,
                    timestamp: new Date().toLocaleTimeString(),
                    type: 'spread'
                });
            }
            this.$nextTick(() => {
                this.scrollToBottom();
            });
        },
        
        sendMessage() {
            if (!this.newMessage.trim()) return;
            
            const message = {
                type: 'chat',
                content: this.newMessage,
                user_id: this.user_id,
                room_id: this.room_id
            };
            
            this.ws.send(JSON.stringify(message));
            this.newMessage = '';
        },
        
        showSpreadDialog() {
            this.showDialog = true;
        },
        
        closeDialog() {
            this.showDialog = false;
            this.spreadAmount = 0;
            this.spreadCount = 0;
        },
        
        async createSpread() {
            if (this.spreadAmount <= 0 || this.spreadCount <= 0) {
                alert('올바른 금액과 인원수를 입력해주세요.');
                return;
            }
            
            try {
                const response = await fetch('/api/distributor/spread', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Room-ID': this.room_id,
                        'X-User-ID': this.user_id
                    },
                    body: JSON.stringify({
                        amount: this.spreadAmount,
                        count: this.spreadCount
                    })
                });
                
                if (!response.ok) {
                    throw new Error('돈뿌리기 생성에 실패했습니다.');
                }
                
                const result = await response.json();
                
                // WebSocket을 통해 뿌리기 메시지 전송
                const spreadMessage = {
                    type: 'spread',
                    amount: this.spreadAmount,
                    count: this.spreadCount,
                    token: result.token,
                    user_id: this.user_id,
                    room_id: this.room_id
                };
                
                this.ws.send(JSON.stringify(spreadMessage));
                this.closeDialog();
                
            } catch (error) {
                alert(error.message);
            }
        },
        
        scrollToBottom() {
            const container = this.$refs.messageContainer;
            container.scrollTop = container.scrollHeight;
        }
    }
}); 