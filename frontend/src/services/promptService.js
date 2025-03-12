// src/services/promptService.js
import api from './api';

export default {
  // Получение списка промптов с фильтрацией
  getPrompts(params = {}) {
    return api.get('/prompts/', { params });
  },
  
  // Получение промпта по ID
  getPrompt(promptId) {
    return api.get(`/prompts/${promptId}`);
  },
  
  // Создание нового промпта
  createPrompt(promptData) {
    return api.post('/prompts/', promptData);
  },
  
  // Обновление промпта
  updatePrompt(promptId, promptData) {
    return api.put(`/prompts/${promptId}`, promptData);
  },
  
  // Удаление промпта
  deletePrompt(promptId) {
    return api.delete(`/prompts/${promptId}`);
  }
};