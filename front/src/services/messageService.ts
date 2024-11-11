// src/services/messageService.ts
import axios from 'axios';

const MESSAGE_API_URL = 'http://34.116.196.137:8000/messages/'; // Adjust this URL based on your API

// Exporting SendMessageParams so it can be used in other files
export interface SendMessageParams {
    content: string; // The message content
}

export const sendMessage = async (token: string | null, roomOid: string, messageData: SendMessageParams) => {
    if (!token) {
        throw new Error('No authentication token found.');
    }

    const response = await axios.post(`${MESSAGE_API_URL}${roomOid}/`, messageData, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    return response.data;
};
