import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ChatList from '../components/ChatList';  // New component to display the chat list
import MessageSender from '../components/MessageSender';
import MessageList from '../components/MessageList';
import { getUserIdFromToken } from '../utils/decodeToken';
import '../styles/ChatRoom.css';

const ChatRoom: React.FC = () => {
    const { roomId } = useParams<{ roomId: string }>();
    const [currentUserId, setCurrentUserId] = useState<number | null>(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            const userId = getUserIdFromToken(token);
            setCurrentUserId(userId);
        }
    }, []);

    return (
        <div className="chat-room">
            <div className="chat-room__sidebar">
                <ChatList currentUserId={currentUserId}/>
            </div>
            <div className="chat-room__main">
                {roomId ? (
                    currentUserId !== null ? (
                        <>
                            <MessageList roomOid={roomId} currentUserId={currentUserId}/>
                            <MessageSender roomOid={roomId}/>
                        </>
                    ) : (
                        <p>Loading user data...</p>
                    )
                ) : (
                    <div className="welcome-container">
                        <h3 className="welcome-title">Welcome! Choose your chat or create a new one.</h3>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatRoom;
