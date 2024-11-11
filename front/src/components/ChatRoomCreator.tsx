// src/components/ChatRoomCreator.tsx
import React, { useState } from 'react';
import { createChatRoom } from '../services/chatService';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import MessageSender from './MessageSender';
import '../styles/ChatRoomCreator.css';

const ChatRoomCreator: React.FC = () => {
    const [chatTitle, setChatTitle] = useState('');
    const [senderId, setSenderId] = useState<number | ''>('');
    const [retrieverId, setRetrieverId] = useState<number | ''>('');
    const [message, setMessage] = useState('');
    const [roomOid, setRoomOid] = useState<string | null>(null);
    const [loading, setLoading] = useState(false); // Loading state
    const navigate = useNavigate(); // Initialize navigate function

    const handleCreateChatRoom = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        if (!token) {
            setMessage('Please log in to create a chat room.');
            return;
        }

        setLoading(true); // Show loading indicator
        try {
            const chatRoom = await createChatRoom(token, {
                title: chatTitle,
                sender_id: Number(senderId),
                receiver_id: Number(retrieverId),
            });
            setRoomOid(chatRoom.room_oid);
            setMessage('Chat room created successfully!');
            setChatTitle('');
            setSenderId('');
            setRetrieverId('');

            // Redirect to the newly created chat room
            navigate(`/chat/${chatRoom.room_oid}`);
        } catch (error) {
            console.error(error);
            setMessage('Failed to create chat room.');
        } finally {
            setLoading(false); // Hide loading indicator
        }
    };

    return (
        <div className="chat-room-creator">
            <h2>Create a New Chat Room</h2>
            <form onSubmit={handleCreateChatRoom} className="chat-room-form">
                <div className="form-group">
                    <label>Chat Room Title:</label>
                    <input
                        type="text"
                        value={chatTitle}
                        onChange={(e) => setChatTitle(e.target.value)}
                        required
                        placeholder="Enter chat room title"
                    />
                </div>
                <div className="form-group">
                    <label>Sender ID:</label>
                    <input
                        type="number"
                        value={senderId}
                        onChange={(e) => setSenderId(Number(e.target.value))}
                        required
                        placeholder="Enter sender ID"
                    />
                </div>
                <div className="form-group">
                    <label>Retriever ID:</label>
                    <input
                        type="number"
                        value={retrieverId}
                        onChange={(e) => setRetrieverId(Number(e.target.value))}
                        required
                        placeholder="Enter retriever ID"
                    />
                </div>
                <button type="submit" className="create-button" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Chat Room'}
                </button>
            </form>
            {message && <p className="feedback-message">{message}</p>}
            {roomOid && (
                <div className="message-sender-container">
                    <MessageSender roomOid={roomOid}/>
                </div>
            )}
            <footer className="login-footer">
                <p>&copy; {new Date().getFullYear()} Forum. All rights reserved.</p>
            </footer>
        </div>

    )
        ;
};

export default ChatRoomCreator;
