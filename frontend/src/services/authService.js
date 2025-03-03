import apiClient from './apiClient';

export const authService = {
  async login(email, password) {
    const response = await apiClient.post('/auth/login', {
      email,
      password
    });
    return response.data;
  },
  
  async getUserInfo() {
    const response = await apiClient.get('/users/me');
    return response.data;
  },
  
  async updateUserInfo(userData) {
    const response = await apiClient.put('/users/me', userData);
    return response.data;
  }
};