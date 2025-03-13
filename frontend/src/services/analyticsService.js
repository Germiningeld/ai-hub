import apiClient from './apiClient';

export const analyticsService = {
  async getUsageData(params = {}) {
    const response = await apiClient.get('/statistics/usage', { params });
    return response.data;
  },
  
  async getSummary() {
    const response = await apiClient.get('/statistics/summary');
    return response.data;
  }
};