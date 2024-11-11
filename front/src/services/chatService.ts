// src/services/chatService.ts
import axios from 'axios';

const CHAT_API_URL = 'http://localhost:8000/communications/chatrooms/';

interface CreateChatRoomParams {
    title: string;
    sender_id: number;
    receiver_id: number;
}

export const createChatRoom = async (token: string, chatRoomData: CreateChatRoomParams) => {
    const response = await axios.post(CHAT_API_URL, chatRoomData, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    return response.data;
};
