// src/services/authService.ts
import axios from 'axios';

const API_URL = 'http://34.116.196.137:8000/auth/jwt/create/';

interface AuthResponse {
    access: string; // JWT token
}

export const authenticateUser = async (email: string, password: string): Promise<AuthResponse> => {
    const response = await axios.post(API_URL, { email, password });
    return response.data;
};
