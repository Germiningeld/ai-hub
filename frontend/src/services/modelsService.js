import apiClient from './apiClient';

export const modelsService = {
  async getAvailableModels() {
    const response = await apiClient.get('/models/available');
    return response.data;
  },
  
  async getModelPreferences() {
    const response = await apiClient.get('/models/preferences');
    return response.data;
  },
  
  async getDefaultPreferences() {
    const response = await apiClient.get('/models/preferences/default');
    return response.data;
  },
  
  async createModelPreference(preferenceData) {
    const response = await apiClient.post('/models/preferences', preferenceData);
    return response.data;
  },
  
  async updateModelPreference(preferenceId, preferenceData) {
    const response = await apiClient.put(`/models/preferences/${preferenceId}`, preferenceData);
    return response.data;
  },
  
  async deleteModelPreference(preferenceId) {
    await apiClient.delete(`/models/preferences/${preferenceId}`);
  }
};