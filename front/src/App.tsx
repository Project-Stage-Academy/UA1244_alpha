// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import ChatRoomCreator from './components/ChatRoomCreator';
import ChatRoom from './pages/ChatRoom';

const App: React.FC = () => {
    return (
        <Router>
            <div className="container-fluid">
                <Routes>
                    <Route path="/" element={<Login />} />
                    <Route path="/create-chat" element={<ChatRoomCreator />} />
                    <Route path="/chat/:roomId?" element={<ChatRoom />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
