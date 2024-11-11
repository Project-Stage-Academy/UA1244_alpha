class WebSocketService {
    private socket: WebSocket | null = null;
    private token: string | null = localStorage.getItem('token');
    private messageCallback: ((event: MessageEvent) => void) | null = null;
    private notificationCallback: ((notification: string) => void) | null = null;

    connect(roomOid: string) {
        if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
            console.log('WebSocket is already connected.');
            return;
        }

        if (!this.token) {
            console.error('No authentication token found.');
            return;
        }

        this.socket = new WebSocket(`ws://34.116.196.137:8001/ws/chat/${roomOid}/?token=${this.token}`);

        this.socket.onopen = () => console.log('WebSocket connected');
        this.socket.onclose = () => console.log('WebSocket closed');
        this.socket.onerror = (error) => console.error('WebSocket error:', error);

        // Єдиний обробник для всіх типів повідомлень
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'message' && this.messageCallback) {
                this.messageCallback(event);
            } else if (data.type === 'notification' && this.notificationCallback) {
                this.notificationCallback(data.content);
            }
        };
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    sendMessage(message: string) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ message }));
        } else {
            console.error('WebSocket is not open.');
        }
    }

    addMessageListener(callback: (event: MessageEvent) => void) {
        this.messageCallback = callback;
    }

    addNotificationListener(callback: (notification: string) => void) {
        this.notificationCallback = callback;
    }

    removeMessageListener() {
        this.messageCallback = null;
    }

    removeNotificationListener() {
        this.notificationCallback = null;
    }
}

export default new WebSocketService();
