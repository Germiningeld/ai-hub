import apiClient from './apiClient';

export const apiKeysService = {
  async getApiKeys() {
    const response = await apiClient.get('/api-keys/');
    return response.data;
  },
  
  async createApiKey(keyData) {
    const response = await apiClient.post('/api-keys/', keyData);
    return response.data;
  },
  
  async updateApiKey(keyId, keyData) {
    const response = await apiClient.put(`/api-keys/${keyId}`, keyData);
    return response.data;
  },
  
  async deleteApiKey(keyId) {
    const response = await apiClient.delete(`/api-keys/${keyId}`);
    return response.data;
  }
};