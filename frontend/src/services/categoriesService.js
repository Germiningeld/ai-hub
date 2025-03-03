import apiClient from './apiClient';

export const categoriesService = {
  async getCategories() {
    const response = await apiClient.get('/categories/');
    return response.data;
  },
  
  async createCategory(categoryData) {
    const response = await apiClient.post('/categories/', categoryData);
    return response.data;
  },
  
  async updateCategory(categoryId, categoryData) {
    const response = await apiClient.put(`/categories/${categoryId}`, categoryData);
    return response.data;
  },
  
  async deleteCategory(categoryId) {
    await apiClient.delete(`/categories/${categoryId}`);
  }
};