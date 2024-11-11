// utils/decodeToken.ts
export const getUserIdFromToken = (token: string | null): number | null => {
    if (!token) return null;

    try {
        // Decode the token (without verifying the signature)
        const decodedToken = JSON.parse(atob(token.split('.')[1])); // Decode the payload part of the JWT
        return decodedToken.user_id || null;  // Adjust based on how the ID is stored in your payload
    } catch (error) {
        console.error('Error decoding JWT:', error);
        return null;
    }
};
