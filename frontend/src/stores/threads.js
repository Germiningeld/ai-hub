import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { threadsService } from '@/services/threadsService';

export const useThreadsStore = defineStore('threads', () => {
  const threads = ref([]);
  const currentThread = ref(null);
  const isStreaming = ref(false);
  
  async function fetchThreads(params = {}) {
    try {
      const data = await threadsService.getThreads(params);
      threads.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching threads:', error);
      throw error;
    }
  }
  
  async function fetchThread(threadId) {
    try {
      const thread = await threadsService.getThread(threadId);
      currentThread.value = thread;
      return thread;
    } catch (error) {
      console.error(`Error fetching thread ${threadId}:`, error);
      throw error;
    }
  }
  
  async function createThread(threadData) {
    try {
      const newThread = await threadsService.createThread(threadData);
      threads.value.unshift(newThread);
      return newThread;
    } catch (error) {
      console.error('Error creating thread:', error);
      throw error;
    }
  }
  
  async function updateThread(threadData) {
    try {
      const updatedThread = await threadsService.updateThread(threadData.id, threadData);
      
      // Обновляем в списке тредов
      const index = threads.value.findIndex(thread => thread.id === threadData.id);
      if (index !== -1) {
        threads.value[index] = { ...threads.value[index], ...updatedThread };
      }
      
      // Обновляем текущий тред, если он открыт
      if (currentThread.value && currentThread.value.id === threadData.id) {
        currentThread.value = { ...currentThread.value, ...updatedThread };
      }
      
      return updatedThread;
    } catch (error) {
      console.error(`Error updating thread ${threadData.id}:`, error);
      throw error;
    }
  }
  
  async function deleteThread(threadId) {
    try {
      await threadsService.deleteThread(threadId);
      threads.value = threads.value.filter(thread => thread.id !== threadId);
      
      if (currentThread.value && currentThread.value.id === threadId) {
        currentThread.value = null;
      }
    } catch (error) {
      console.error(`Error deleting thread ${threadId}:`, error);
      throw error;
    }
  }
  
  async function bulkDeleteThreads(threadIds) {
    try {
      await threadsService.bulkDeleteThreads(threadIds);
      threads.value = threads.value.filter(thread => !threadIds.includes(thread.id));
      
      if (currentThread.value && threadIds.includes(currentThread.value.id)) {
        currentThread.value = null;
      }
    } catch (error) {
      console.error('Error bulk deleting threads:', error);
      throw error;
    }
  }
  
  async function sendMessage(threadId, messageData) {
    try {
      const message = await threadsService.sendMessage(threadId, messageData);
      
      if (currentThread.value && currentThread.value.id === threadId) {
        currentThread.value.messages.push(message);
      }
      
      return message;
    } catch (error) {
      console.error(`Error sending message to thread ${threadId}:`, error);
      throw error;
    }
  }
  
  async function streamMessage(threadId, messageData) {
    isStreaming.value = true;
    
    try {
      const message = await threadsService.streamMessage(threadId, messageData, (chunk) => {
        // Обрабатываем каждый чанк потока
        if (currentThread.value && currentThread.value.id === threadId) {
          const lastMessage = currentThread.value.messages[currentThread.value.messages.length - 1];
          
          if (lastMessage && lastMessage.role === 'assistant' && !lastMessage.id) {
            // Обновляем содержимое последнего сообщения
            lastMessage.content += chunk;
          } else {
            // Создаем новое сообщение для ассистента
            currentThread.value.messages.push({
              role: 'assistant',
              content: chunk,
              created_at: new Date().toISOString()
            });
          }
        }
      });
      
      // Заменяем временное сообщение на полное сообщение с метаданными
      if (currentThread.value && currentThread.value.id === threadId) {
        const lastIndex = currentThread.value.messages.findIndex(msg => msg.role === 'assistant' && !msg.id);
        
        if (lastIndex !== -1) {
          currentThread.value.messages[lastIndex] = message;
        }
      }
      
      return message;
    } catch (error) {
      console.error(`Error streaming message to thread ${threadId}:`, error);
      throw error;
    } finally {
      isStreaming.value = false;
    }
  }
  
  function stopStreaming(threadId) {
    if (isStreaming.value) {
      threadsService.stopStreaming(threadId);
      isStreaming.value = false;
    }
  }
  
  return {
    threads,
    currentThread,
    isStreaming,
    fetchThreads,
    fetchThread,
    createThread,
    updateThread,
    deleteThread,
    bulkDeleteThreads,
    sendMessage,
    streamMessage,
    stopStreaming
  };
});