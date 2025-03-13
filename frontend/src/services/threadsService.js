import apiClient from './apiClient';

export const threadsService = {
  async getThreads(params = {}) {
    const response = await apiClient.get('/threads/', { params });
    return response.data;
  },
  
  async getThread(threadId) {
    const response = await apiClient.get(`/threads/${threadId}`);
    return response.data;
  },
  
  async createThread(threadData) {
    const response = await apiClient.post('/threads/', threadData);
    return response.data;
  },
  
  async updateThread(threadId, threadData) {
    const response = await apiClient.put(`/threads/${threadId}`, threadData);
    return response.data;
  },
  
  async deleteThread(threadId) {
    await apiClient.delete(`/threads/${threadId}`);
  },
  
  async bulkDeleteThreads(threadIds) {
    await apiClient.post('/threads/bulk-delete', { thread_ids: threadIds });
  },
  
  async bulkArchiveThreads(threadIds) {
    const response = await apiClient.post('/threads/bulk-archive', { thread_ids: threadIds });
    return response.data;
  },
  
  async sendMessage(threadId, messageData) {
    const response = await apiClient.post(`/threads/${threadId}/send`, messageData);
    return response.data;
  },
  
  async streamMessage(threadId, messageData, onChunk) {
    return new Promise((resolve, reject) => {
      const eventSource = new EventSource(
        `/api/threads/${threadId}/stream?use_context=${messageData.use_context || true}`
      );
      
      let message = null;
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
          onChunk(data.content);
        } else if (data.type === 'done') {
          message = data.message;
          eventSource.close();
          resolve(message);
        }
      };
      
      eventSource.onerror = (error) => {
        eventSource.close();
        reject(error);
      };
      
      // Отправляем сообщение для инициализации стрима
      apiClient.post(`/threads/${threadId}/stream`, messageData)
        .catch((error) => {
          eventSource.close();
          reject(error);
        });
    });
  },
  
  async stopStreaming(threadId) {
    await apiClient.post(`/threads/${threadId}/stream/stop`);
  }
};