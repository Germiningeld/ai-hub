import apiClient from './apiClient';

export const promptsService = {
  async getPrompts(params = {}) {
    const response = await apiClient.get('/prompts/', { params });
    return response.data;
  },
  
  async getPrompt(promptId) {
    const response = await apiClient.get(`/prompts/${promptId}`);
    return response.data;
  },
  
  async createPrompt(promptData) {
    const response = await apiClient.post('/prompts/', promptData);
    return response.data;
  },
  
  async updatePrompt(promptId, promptData) {
    const response = await apiClient.put(`/prompts/${promptId}`, promptData);
    return response.data;
  },
  
  async deletePrompt(promptId) {
    await apiClient.delete(`/prompts/${promptId}`);
  }
};