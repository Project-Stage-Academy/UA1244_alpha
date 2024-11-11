/* components/MessageSender.tsx */
import React, { useState, useEffect } from 'react';

interface MessageSenderProps {
    roomOid: string;
}

const MessageSender: React.FC<MessageSenderProps> = ({ roomOid }) => {
    const [message, setMessage] = useState('');
    const [feedback, setFeedback] = useState('');
    const [socket, setSocket] = useState<WebSocket | null>(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setFeedback('No authentication token found.');
            return;
        }

        const ws = new WebSocket(`ws://34.116.196.137:8001/ws/chat/${roomOid}/?token=${token}`);
        setSocket(ws);

        ws.onopen = () => {
            setFeedback('Connected');
        };

        ws.onclose = () => setFeedback('Disconnected');
        ws.onerror = () => setFeedback('Error with WebSocket connection');

        return () => {
            ws.close();
        };
    }, [roomOid]);

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ message }));
            setMessage('');
            setFeedback('Message sent');
        } else {
            setFeedback('WebSocket is not open');
        }
    };

    return (
        <div className="message-sender">
            <form onSubmit={handleSendMessage}>
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                />
                <button type="submit">Send</button>
            </form>
            <div className="feedback">{feedback}</div>
        </div>
    );
};

export default MessageSender;
