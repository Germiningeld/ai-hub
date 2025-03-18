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

/**
 * Адаптирует массив сообщений
 * @param {Array} messages - Массив сообщений
 * @returns {Array} - Адаптированные сообщения
 */
function adaptMessages(messages) {
  if (!Array.isArray(messages)) return messages;
  return messages.map(adaptMessage);
}

class MessageService {
  /**
   * Добавление сообщения в тред
   * @param {string} threadId - ID треда
   * @param {Object} messageData - Данные сообщения
   * @returns {Promise} - Промис с результатом запроса
   */
  async addMessage(threadId, messageData) {
    try {
      const response = await api.post(`/threads/${threadId}/messages`, messageData);
      if (response && response.data) {
        response.data = adaptMessage(response.data);
      }
      return response;
    } catch (error) {
      console.error('Error adding message:', error);
      throw error;
    }
  }

  /**
   * Отправка сообщения в тред и получение ответа от AI
   * @param {string} threadId - ID треда
   * @param {Object} messageData - Данные сообщения
   * @param {boolean} useContext - Использовать ли контекст для генерации ответа
   * @returns {Promise} - Промис с результатом запроса
   */
  async sendMessage(threadId, messageData, useContext = true) {
    try {
      // Преобразование строковых значений в числовые для температуры и max_tokens
      const formattedData = {
        content: messageData.content,
        system_prompt: messageData.system_prompt,
        temperature: parseFloat(messageData.temperature),
        max_tokens: parseInt(messageData.max_tokens)
      };
      
      // Удаляем все неопределенные/пустые значения
      const cleanData = Object.fromEntries(
        Object.entries(formattedData).filter(([_, v]) => v !== undefined && v !== null)
      );
      
      const response = await api.post(`/threads/${threadId}/send`, cleanData, {
        params: { use_context: useContext }
      });
      
      // Адаптируем полученное сообщение
      if (response && response.data) {
        response.data = adaptMessage(response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Отправка сообщения с потоковой обработкой ответа
   * @param {string} threadId - ID треда
   * @param {Object} messageData - Данные сообщения
   * @param {boolean} useContext - Использовать ли контекст для генерации ответа
   * @param {number} timeout - Таймаут в секундах
   * @returns {Promise} - Промис с результатом запроса в виде потока событий
   */
  async streamMessage(threadId, messageData, useContext = true, timeout = 120) {
    try {
      // Преобразование строковых значений в числовые для температуры и max_tokens
      const formattedData = {
        content: messageData.content,
        system_prompt: messageData.system_prompt,
        temperature: parseFloat(messageData.temperature),
        max_tokens: parseInt(messageData.max_tokens)
      };
      
      // Удаляем все неопределенные/пустые значения
      const cleanData = Object.fromEntries(
        Object.entries(formattedData).filter(([_, v]) => v !== undefined && v !== null)
      );
      
      return await api.post(`/threads/${threadId}/stream`, cleanData, {
        params: { 
          use_context: useContext,
          timeout: timeout
        },
        responseType: 'stream'
      });
    } catch (error) {
      console.error('Error streaming message:', error);
      throw error;
    }
  }

  /**
   * Остановка потоковой генерации ответа
   * @param {string} threadId - ID треда
   * @param {string} messageId - ID сообщения (опционально)
   * @returns {Promise} - Промис с результатом запроса
   */
  async stopStreamGeneration(threadId, messageId = null) {
    try {
      const params = messageId ? { message_id: messageId } : {};
      return await api.post(`/threads/${threadId}/stream/stop`, null, { params });
    } catch (error) {
      console.error('Error stopping stream generation:', error);
      throw error;
    }
  }

  /**
   * Подсчет токенов в тексте
   * @param {string} provider - Провайдер (openai, anthropic и т.д.)
   * @param {string} model - Модель
   * @param {string} text - Текст для подсчета токенов
   * @returns {Promise} - Промис с результатом запроса
   */
  async countTokens(provider, model, text) {
    try {
      return await api.post('/threads/token-count', {
        provider,
        model,
        text
      });
    } catch (error) {
      console.error('Error counting tokens:', error);
      throw error;
    }
  }

  /**
   * Получение завершения текста без сохранения в тред
   * @param {Object} completionData - Данные для запроса
   * @returns {Promise} - Промис с результатом запроса
   */
  async getCompletion(completionData) {
    try {
      // Преобразование строковых значений в числовые для температуры и max_tokens
      const formattedData = {
        ...completionData,
        temperature: parseFloat(completionData.temperature),
        max_tokens: parseInt(completionData.max_tokens)
      };
      
      return await api.post('/threads/completion', formattedData);
    } catch (error) {
      console.error('Error getting completion:', error);
      throw error;
    }
  }
}

export default new MessageService();