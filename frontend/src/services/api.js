import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,  // 60 seconds for first-time searches (Reddit + Gemini takes time)
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeAddress = async (address) => {
  try {
    const response = await api.post('/api/analyze', { address });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to analyze address' };
  }
};

export const compareAddresses = async (address1, address2) => {
  try {
    const response = await api.post('/api/compare', {
      address1,
      address2
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to compare addresses' };
  }
};

export default api;
