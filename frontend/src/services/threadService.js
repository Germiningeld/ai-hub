// src/services/threadService.js
import api from './api';

/**
 * Адаптирует сообщение, полученное от API, к формату, используемому на фронтенде
 * @param {Object} message - Сообщение от API
 * @returns {Object} - Адаптированное сообщение
 */
function adaptMessage(message) {
  if (!message) return message;
  
  const adapted = { ...message };
  
  // Адаптация полей токенов (API возвращает tokens_total, но фронтенд ожидает tokens)
  if (adapted.tokens_total !== undefined && adapted.tokens === undefined) {
    adapted.tokens = adapted.tokens_total;
  } else if (adapted.tokens_input !== undefined && adapted.tokens === undefined) {
    // Если нет tokens_total, но есть tokens_input, используем его
    adapted.tokens = adapted.tokens_input + (adapted.tokens_output || 0);
  }
  
  return adapted;
}

/**
 * Адаптирует тред, полученный от API, к формату, используемому на фронтенде
 * @param {Object} thread - Тред от API
 * @returns {Object} - Адаптированный тред
 */
function adaptThread(thread) {
  if (!thread) return thread;
  
  const adapted = { ...thread };
  
  // Адаптируем сообщения в треде, если они есть
  if (Array.isArray(adapted.messages)) {
    adapted.messages = adapted.messages.map(adaptMessage);
  }
  
  return adapted;
}

export default {
  /**
   * Получение списка тредов с фильтрацией
   * @param {Object} params - Параметры запроса
   * @returns {Promise} - Промис с результатом запроса
   */
  async getThreads(params = {}) {
    try {
      const response = await api.get('/threads/', { params });
      
      // Адаптируем треды в ответе
      if (response.data && Array.isArray(response.data)) {
        response.data = response.data.map(adaptThread);
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching threads:', error);
      throw error;
    }
  },
  
  /**
   * Получение конкретного треда по ID
   * @param {string} threadId - ID треда
   * @returns {Promise} - Промис с результатом запроса
   */
  async getThread(threadId) {
    try {
      const response = await api.get(`/threads/${threadId}`);
      
      // Адаптируем тред в ответе
      if (response.data) {
        response.data = adaptThread(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching thread:', error);
      throw error;
    }
  },
  
  /**
   * Создание нового треда
   * @param {Object} threadData - Данные для создания треда
   * @returns {Promise} - Промис с результатом запроса
   */
  async createThread(threadData) {
    try {
      // Проверяем и преобразуем числовые значения
      const formattedData = {
        title: threadData.title || 'Новая беседа',
        provider: threadData.provider,
        model: threadData.model,
        category_id: threadData.category_id || null,
        is_pinned: threadData.is_pinned !== undefined ? threadData.is_pinned : false,
        is_archived: threadData.is_archived !== undefined ? threadData.is_archived : false,
        initial_message: threadData.initial_message || '',
        system_prompt: threadData.system_prompt || '',
        temperature: parseFloat(threadData.temperature || 0.7),
        max_tokens: parseInt(threadData.max_tokens || 2000)
      };
      
      // Убедимся, что все числовые поля имеют правильный тип
      if (isNaN(formattedData.temperature)) formattedData.temperature = 0.7;
      if (isNaN(formattedData.max_tokens)) formattedData.max_tokens = 2000;
      
      const response = await api.post('/threads/', formattedData);
      
      // Адаптируем тред в ответе
      if (response.data) {
        response.data = adaptThread(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error creating thread:', error);
      throw error;
    }
  },
  
  /**
   * Создание треда с потоковой обработкой
   * @param {Object} threadData - Данные для создания треда
   * @returns {Promise} - Промис с результатом запроса
   */
  async createThreadStream(threadData) {
    try {
      // Проверяем и преобразуем числовые значения
      const formattedData = {
        title: threadData.title || 'Новая беседа',
        provider: threadData.provider,
        model: threadData.model,
        category_id: threadData.category_id || null,
        is_pinned: threadData.is_pinned !== undefined ? threadData.is_pinned : false,
        is_archived: threadData.is_archived !== undefined ? threadData.is_archived : false,
        initial_message: threadData.initial_message || '',
        system_prompt: threadData.system_prompt || '',
        temperature: parseFloat(threadData.temperature || 0.7),
        max_tokens: parseInt(threadData.max_tokens || 2000)
      };
      
      // Убедимся, что все числовые поля имеют правильный тип
      if (isNaN(formattedData.temperature)) formattedData.temperature = 0.7;
      if (isNaN(formattedData.max_tokens)) formattedData.max_tokens = 2000;
      
      return await api.post('/threads/stream', formattedData, {
        responseType: 'stream'
      });
    } catch (error) {
      console.error('Error creating thread stream:', error);
      throw error;
    }
  },
  
  /**
   * Обновление треда
   * @param {string} threadId - ID треда
   * @param {Object} threadData - Данные для обновления
   * @returns {Promise} - Промис с результатом запроса
   */
  async updateThread(threadId, threadData) {
    try {
      // Если в данных есть числовые поля, преобразуем их к числовому типу
      if (threadData.temperature !== undefined) {
        threadData.temperature = parseFloat(threadData.temperature);
        if (isNaN(threadData.temperature)) threadData.temperature = 0.7;
      }
      
      if (threadData.max_tokens !== undefined) {
        threadData.max_tokens = parseInt(threadData.max_tokens);
        if (isNaN(threadData.max_tokens)) threadData.max_tokens = 2000;
      }
      
      const response = await api.put(`/threads/${threadId}`, threadData);
      
      // Адаптируем тред в ответе
      if (response.data) {
        response.data = adaptThread(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error updating thread:', error);
      throw error;
    }
  },
  
  /**
   * Удаление треда
   * @param {string} threadId - ID треда
   * @returns {Promise} - Промис с результатом запроса
   */
  async deleteThread(threadId) {
    try {
      return await api.delete(`/threads/${threadId}`);
    } catch (error) {
      console.error('Error deleting thread:', error);
      throw error;
    }
  },
  
  /**
   * Массовое удаление тредов
   * @param {Array} threadIds - Массив ID тредов для удаления
   * @returns {Promise} - Промис с результатом запроса
   */
  async bulkDeleteThreads(threadIds) {
    try {
      return await api.post('/threads/bulk-delete', { thread_ids: threadIds });
    } catch (error) {
      console.error('Error bulk deleting threads:', error);
      throw error;
    }
  },
  
  /**
   * Массовое архивирование тредов
   * @param {Array} threadIds - Массив ID тредов для архивирования
   * @returns {Promise} - Промис с результатом запроса
   */
  async bulkArchiveThreads(threadIds) {
    try {
      const response = await api.post('/threads/bulk-archive', { thread_ids: threadIds });
      
      // Адаптируем треды в ответе
      if (response.data && Array.isArray(response.data)) {
        response.data = response.data.map(adaptThread);
      }
      
      return response;
    } catch (error) {
      console.error('Error bulk archiving threads:', error);
      throw error;
    }
  },
  
  /**
   * Получение сообщений треда
   * @param {string} threadId - ID треда
   * @returns {Promise} - Промис с результатом запроса
   */
  async getThreadMessages(threadId) {
    try {
      const response = await api.get(`/threads/${threadId}/messages`);
      
      // Адаптируем сообщения в ответе
      if (response.data && Array.isArray(response.data)) {
        response.data = response.data.map(adaptMessage);
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching thread messages:', error);
      throw error;
    }
  },
  
  /**
   * Добавление сообщения в тред
   * @param {string} threadId - ID треда
   * @param {Object} messageData - Данные сообщения
   * @returns {Promise} - Промис с результатом запроса
   */
  async addMessage(threadId, messageData) {
    try {
      const response = await api.post(`/threads/${threadId}/messages`, messageData);
      
      // Адаптируем сообщение в ответе
      if (response.data) {
        response.data = adaptMessage(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error adding message to thread:', error);
      throw error;
    }
  }
};