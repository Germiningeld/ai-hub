// src/services/messageService.js
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

export default {
  /**
   * Отправка сообщения в тред и получение ответа от ассистента
   * @param {string} threadId - ID треда
   * @param {Object} messageData - Данные сообщения
   * @param {boolean} useContext - Использовать ли контекст предыдущих сообщений
   * @returns {Promise} - Промис с результатом запроса
   */
  async sendMessage(threadId, messageData, useContext = true) {
    try {
      // Проверяем маршрут API в соответствии с документацией
      const endpoint = `/threads/${threadId}/send`;
      
      // Добавляем параметр использования контекста в запрос
      const params = { use_context: useContext };
      
      // Проверяем и преобразуем числовые значения
      if (messageData.temperature !== undefined) {
        messageData.temperature = parseFloat(messageData.temperature);
      }
      
      if (messageData.max_tokens !== undefined) {
        messageData.max_tokens = parseInt(messageData.max_tokens);
      }
      
      const response = await api.post(endpoint, messageData, { params });
      
      // Адаптируем сообщение в ответе
      if (response.data) {
        response.data = adaptMessage(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },
  
/**
 * Получение URL для потокового соединения через SSE
 * @param {string} threadId - ID треда
 * @param {Object} messageData - Данные сообщения
 * @param {boolean} useContext - Использовать ли контекст предыдущих сообщений
 * @returns {string} - URL для создания EventSource
 */
getStreamUrl(threadId, messageData, useContext = true) {
  try {
    // Создаем базовый URL
    const baseUrl = `/api/threads/${threadId}/stream`;
    
    // Подготавливаем параметры запроса
    const params = new URLSearchParams();
    
    // Добавляем базовые параметры
    params.append('use_context', useContext);
    
    // Добавляем все поля из messageData
    for (const [key, value] of Object.entries(messageData)) {
      // Преобразуем значения в строки
      if (value !== null && value !== undefined) {
        params.append(key, String(value));
      }
    }
    
    // Формируем полный URL
    return `${baseUrl}?${params.toString()}`;
  } catch (error) {
    console.error('Error creating stream URL:', error);
    throw error;
  }
},
  
  /**
   * Получение сообщения по ID
   * @param {string} threadId - ID треда
   * @param {string} messageId - ID сообщения
   * @returns {Promise} - Промис с результатом запроса
   */
  async getMessage(threadId, messageId) {
    try {
      const response = await api.get(`/threads/${threadId}/messages/${messageId}`);
      
      // Адаптируем сообщение в ответе
      if (response.data) {
        response.data = adaptMessage(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error getting message:', error);
      throw error;
    }
  },
  
  /**
   * Создание системного сообщения (для обновления системного промпта)
   * @param {string} threadId - ID треда
   * @param {Object} messageData - Данные сообщения
   * @returns {Promise} - Промис с результатом запроса
   */
  async createSystemMessage(threadId, messageData) {
    try {
      const systemData = {
        ...messageData,
        role: 'system'
      };
      
      const response = await api.post(`/threads/${threadId}/messages`, systemData);
      
      // Адаптируем сообщение в ответе
      if (response.data) {
        response.data = adaptMessage(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error creating system message:', error);
      throw error;
    }
  },
  
  /**
   * Обновление существующего сообщения
   * @param {string} threadId - ID треда
   * @param {string} messageId - ID сообщения
   * @param {Object} messageData - Данные для обновления
   * @returns {Promise} - Промис с результатом запроса
   */
  async updateMessage(threadId, messageId, messageData) {
    try {
      const response = await api.put(`/threads/${threadId}/messages/${messageId}`, messageData);
      
      // Адаптируем сообщение в ответе
      if (response.data) {
        response.data = adaptMessage(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error updating message:', error);
      throw error;
    }
  },
  
/**
 * Остановка потокового получения ответа
 * @param {string} threadId - ID треда
 * @returns {Promise} - Промис с результатом запроса
 */
async stopMessageStream(threadId) {
  try {
    // Используем api.post, который уже настроен на использование правильного базового URL
    return await api.post(`/threads/${threadId}/stream/stop`);
  } catch (error) {
    console.error('Error stopping message stream:', error);
    throw error;
  }
}
};