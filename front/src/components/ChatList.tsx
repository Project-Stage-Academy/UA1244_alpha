import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Chat {
    oid: string;
    title: string;
    sender_id: number;
    receiver_id: number;
    messages: [];
}

interface ChatListProps {
    currentUserId: number | null;
}

const ChatList: React.FC<ChatListProps> = ({ currentUserId }) => {
    const [chats, setChats] = useState<Chat[]>([]);

    useEffect(() => {
        if (currentUserId === null) return;

        const fetchChats = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get(
                    `http://localhost:8000/communications/chatrooms/user_chats/`,
                    {
                        headers: { Authorization: `Bearer ${token}` },
                    }
                );
                setChats(response.data);
            } catch (error) {
                console.error('Error fetching chats:', error);
            }
        };

        fetchChats();
    }, [currentUserId]);

    return (
        <div className="chat-list">
            <h2 className="chat-list-title">Conversations</h2>
            {chats.length > 0 ? (
                chats.map((chat) => (
                    <div key={chat.oid} className="chat-list-item">
                        <a href={`/chat/${chat.oid}`}>
                            <strong>{chat.title}</strong>
                        </a>
                    </div>
                ))
            ) : (
                <p>No chats available</p>
            )}
            <div className="create-chat-button">
                <a href="http://localhost:5173/create-chat">
                    <button>Create New Chat</button>
                </a>
            </div>
        </div>
    );
};

export default ChatList;
