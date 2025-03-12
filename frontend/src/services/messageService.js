// src/services/messageService.js
import api from './api';

export default {
  // Получение сообщений треда
  getMessages(threadId) {
    return api.get(`/threads/${threadId}/messages`);
  },
  
  // Добавление сообщения в тред (без ответа)
  addMessage(threadId, messageData) {
    return api.post(`/threads/${threadId}/messages`, messageData);
  },
  
  // Отправка сообщения и получение ответа
  sendMessage(threadId, messageData, useContext = true) {
    return api.post(`/threads/${threadId}/send`, messageData, {
      params: { use_context: useContext }
    });
  },
  
  // Отправка сообщения с потоковой обработкой
  sendMessageStream(threadId, messageData, useContext = true) {
    return api.post(`/threads/${threadId}/stream`, messageData, {
      params: { use_context: useContext },
      responseType: 'stream'
    });
  },
  
  // Остановка потоковой генерации
  stopMessageStream(threadId, messageId) {
    return api.post(`/threads/${threadId}/stream/stop`, { message_id: messageId });
  },
  
  // Подсчет токенов в тексте
  countTokens(text, provider = 'openai', model = 'gpt-4o') {
    return api.post('/threads/token-count', {
      text,
      provider,
      model
    });
  }
};