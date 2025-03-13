// src/services/categoryService.js
import api from './api';

export default {
  // Получение списка категорий
  getCategories() {
    return api.get('/categories/');
  },
  
  // Создание новой категории
  createCategory(categoryData) {
    return api.post('/categories/', categoryData);
  },
  
  // Обновление категории
  updateCategory(categoryId, categoryData) {
    return api.put(`/categories/${categoryId}`, categoryData);
  },
  
  // Удаление категории
  deleteCategory(categoryId) {
    return api.delete(`/categories/${categoryId}`);
  }
};