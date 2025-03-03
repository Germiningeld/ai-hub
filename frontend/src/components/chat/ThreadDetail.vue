<template>
    <div class="thread-detail">
      <div v-if="loading" class="thread-loading">
        <div class="loading-spinner"></div>
        <p>Загрузка треда...</p>
      </div>
      
      <div v-else-if="error" class="thread-error">
        <p>{{ error }}</p>
        <button @click="fetchThread" class="retry-button">Повторить</button>
      </div>
      
      <template v-else>
        <div class="messages-container">
          <div v-for="message in thread.messages" :key="message.id" class="message-wrapper">
            <MessageItem 
              :message="message" 
              :is-last="message.id === lastMessageId"
            />
          </div>
        </div>
        
        <div class="input-container">
          <MessageInput 
            :thread-id="threadId" 
            @message-sent="handleMessageSent" 
            :disabled="thread?.is_archived"
          />
        </div>
      </template>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, nextTick, watch } from 'vue';
  import MessageItem from '@/components/chat/MessageItem.vue';
  import MessageInput from '@/components/chat/MessageInput.vue';
  import { useThreadsStore } from '@/stores/threads';
  
  const props = defineProps({
    threadId: {
      type: [Number, String],
      required: true
    }
  });
  
  const threadsStore = useThreadsStore();
  
  const loading = ref(true);
  const error = ref(null);
  
  const thread = computed(() => threadsStore.currentThread || {});
  const lastMessageId = computed(() => {
    if (!thread.value || !thread.value.messages || thread.value.messages.length === 0) {
      return null;
    }
    return thread.value.messages[thread.value.messages.length - 1].id;
  });
  
  const fetchThread = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      await threadsStore.fetchThread(props.threadId);
    } catch (err) {
      error.value = 'Ошибка при загрузке треда. Попробуйте позже.';
      console.error('Error fetching thread:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const handleMessageSent = () => {
    // Прокрутка до последнего сообщения
    nextTick(() => {
      const container = document.querySelector('.messages-container');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    });
  };
  
  onMounted(async () => {
    await fetchThread();
  });
  
  // Наблюдение за изменением threadId и обновление данных
  watch(() => props.threadId, fetchThread);
  </script>
  
  <style scoped>
  .thread-detail {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .thread-loading, .thread-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    color: #6b7280;
  }
  
  .loading-spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid var(--primary-color);
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .retry-button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
  }
  
  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
  }
  
  .message-wrapper {
    margin-bottom: 1.5rem;
  }
  
  .input-container {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
  }
  </style>