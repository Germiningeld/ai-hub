// src/services/threadService.js
import api from './api';

export default {
  // Получение списка тредов с фильтрацией
  getThreads(params = {}) {
    return api.get('/threads/', { params });
  },
  
  // Получение конкретного треда по ID
  getThread(threadId) {
    return api.get(`/threads/${threadId}`);
  },
  
  // Создание нового треда
  createThread(threadData) {
    return api.post('/threads/', threadData);
  },
  
  // Создание треда с потоковой обработкой
  createThreadStream(threadData) {
    return api.post('/threads/stream', threadData, {
      responseType: 'stream'
    });
  },
  
  // Обновление треда
  updateThread(threadId, threadData) {
    return api.put(`/threads/${threadId}`, threadData);
  },
  
  // Удаление треда
  deleteThread(threadId) {
    return api.delete(`/threads/${threadId}`);
  },
  
  // Массовое удаление тредов
  bulkDeleteThreads(threadIds) {
    return api.post('/threads/bulk-delete', { thread_ids: threadIds });
  },
  
  // Массовое архивирование тредов
  bulkArchiveThreads(threadIds) {
    return api.post('/threads/bulk-archive', { thread_ids: threadIds });
  }
};