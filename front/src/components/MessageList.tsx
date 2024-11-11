import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';

interface Message {
    oid: string;
    sender_id: number | string;
    sender_name: string;
    content: string;
    created_at: string;
    receiver_id?: number;
}

interface MessageListProps {
    roomOid: string;
    currentUserId: number;
}

const MessageList: React.FC<MessageListProps> = ({ roomOid, currentUserId }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [notifications, setNotifications] = useState<string[]>([]);
    const messageEndRef = useRef<HTMLDivElement | null>(null);

    // Fetch messages from the backend API
    useEffect(() => {
        const fetchMessages = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get(
                    `http://localhost:8000/communications/chatrooms/${roomOid}/messages/`,
                    {
                        headers: { Authorization: `Bearer ${token}` },
                    }
                );
                setMessages(response.data);
            } catch (error) {
                console.error('Error fetching messages:', error);
            }
        };
        fetchMessages();
    }, [roomOid]);

    // WebSocket connection for the chat room
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) return;

        const ws = new WebSocket(`ws://localhost:8001/ws/chat/${roomOid}/?token=${token}`);

        ws.onmessage = (event) => {
            const newMessage: Message = JSON.parse(event.data);
            setMessages((prevMessages) => [...prevMessages, newMessage]);
        };

        ws.onclose = () => console.log("Chat WebSocket closed.");
        ws.onerror = (error) => console.error('Chat WebSocket error:', error);

        return () => {
            ws.close();
        };
    }, [roomOid]);

    // WebSocket connection for notifications
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) return;

        const notificationWs = new WebSocket(`ws://localhost:8001/ws/notifications/?token=${token}`);

        notificationWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.notification) {
                setNotifications((prevNotifications) => [...prevNotifications, data.notification]);
            }
        };

        notificationWs.onclose = () => console.log("Notification WebSocket closed.");
        notificationWs.onerror = (error) => console.error('Notification WebSocket error:', error);

        return () => {
            notificationWs.close();
        };
    }, []);

    // Automatically remove notifications after 2 seconds
    useEffect(() => {
        const timers = notifications.map((_, index) =>
            setTimeout(() => {
                setNotifications((prevNotifications) => prevNotifications.slice(1));
            }, 2000)
        );

        return () => {
            timers.forEach(clearTimeout);
        };
    }, [notifications]);

    useEffect(() => {
        if (messageEndRef.current) {
            messageEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    return (
        <div className="message-list">
            <div className="notifications">
                {notifications.map((notification, index) => (
                    <div key={index} className="notification">
                        {notification}
                    </div>
                ))}
            </div>
            {messages.map((message) => (
                <MessageItem
                    key={message.oid}
                    message={message}
                    isOwnMessage={message.sender_id === currentUserId}
                />
            ))}
            <div ref={messageEndRef} />
        </div>
    );
};

const MessageItem: React.FC<{ message: Message; isOwnMessage: boolean }> = ({ message, isOwnMessage }) => {
    return (
        <div className={`message-item ${isOwnMessage ? 'own-message' : 'other-message'}`}>
            <div className="message-content">
                <strong>{message.sender_name}:</strong> {message.content}
            </div>
            <div className="message-time">{new Date(message.created_at).toLocaleString()}</div>
        </div>
    );
};

export default MessageList;
