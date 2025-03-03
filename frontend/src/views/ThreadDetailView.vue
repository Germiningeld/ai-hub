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
        <div class="thread-header">
          <div class="thread-title">
            <h2>{{ thread.title }}</h2>
            <button @click="isEditingTitle = true" class="edit-title-btn" v-if="!isEditingTitle">
              ✏️
            </button>
            <div v-else class="edit-title-form">
              <input 
                v-model="editedTitle" 
                @keyup.enter="updateThreadTitle" 
                @keyup.esc="cancelEditTitle"
                ref="titleInput"
                class="title-input"
              />
              <button @click="updateThreadTitle" class="save-title-btn">✓</button>
              <button @click="cancelEditTitle" class="cancel-title-btn">✗</button>
            </div>
          </div>
          
          <div class="thread-actions">
            <button 
              @click="togglePin" 
              class="action-btn" 
              :class="{ 'active': thread.is_pinned }"
              title="Закрепить тред"
            >
              📌
            </button>
            <button 
              @click="toggleArchive" 
              class="action-btn" 
              :class="{ 'active': thread.is_archived }"
              title="Архивировать тред"
            >
              📂
            </button>
            <button 
              @click="confirmDelete" 
              class="action-btn delete-btn"
              title="Удалить тред"
            >
              🗑️
            </button>
          </div>
        </div>
        
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
            :disabled="thread.is_archived"
          />
        </div>
      </template>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, nextTick } from 'vue';
  import { useRouter } from 'vue-router';
  import MessageItem from '@/components/chat/MessageItem.vue';
  import MessageInput from '@/components/chat/MessageInput.vue';
  import { useThreadsStore } from '@/stores/threads';
  
  const props = defineProps({
    threadId: {
      type: [Number, String],
      required: true
    }
  });
  
  const router = useRouter();
  const threadsStore = useThreadsStore();
  
  const loading = ref(true);
  const error = ref(null);
  const isEditingTitle = ref(false);
  const editedTitle = ref('');
  const titleInput = ref(null);
  
  const thread = computed(() => threadsStore.currentThread);
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
  
  const togglePin = async () => {
    try {
      await threadsStore.updateThread({
        id: thread.value.id,
        is_pinned: !thread.value.is_pinned
      });
    } catch (error) {
      console.error('Error toggling pin:', error);
    }
  };
  
  const toggleArchive = async () => {
    try {
      await threadsStore.updateThread({
        id: thread.value.id,
        is_archived: !thread.value.is_archived
      });
    } catch (error) {
      console.error('Error toggling archive:', error);
    }
  };
  
  const confirmDelete = () => {
    if (confirm('Вы уверены, что хотите удалить этот тред?')) {
      deleteThread();
    }
  };
  
  const deleteThread = async () => {
    try {
      await threadsStore.deleteThread(thread.value.id);
      router.push('/chat');
    } catch (error) {
      console.error('Error deleting thread:', error);
    }
  };
  
  const updateThreadTitle = async () => {
    if (editedTitle.value.trim()) {
      try {
        await threadsStore.updateThread({
          id: thread.value.id,
          title: editedTitle.value.trim()
        });
        isEditingTitle.value = false;
      } catch (error) {
        console.error('Error updating thread title:', error);
      }
    }
  };
  
  const cancelEditTitle = () => {
    isEditingTitle.value = false;
    editedTitle.value = thread.value.title;
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
    editedTitle.value = thread.value?.title || '';
  });
  
  // Наблюдатель за isEditingTitle, фокусировка на поле ввода
  watch(isEditingTitle, (val) => {
    if (val) {
      nextTick(() => {
        titleInput.value?.focus();
      });
    }
  });
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
  
  .thread-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .thread-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .thread-title h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  .edit-title-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    opacity: 0.6;
  }
  
  .edit-title-btn:hover {
    opacity: 1;
  }
  
  .edit-title-form {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .title-input {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    width: 300px;
  }
  
  .save-title-btn, .cancel-title-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1rem;
  }
  
  .save-title-btn {
    color: #10b981;
  }
  
  .cancel-title-btn {
    color: #ef4444;
  }
  
  .thread-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .action-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0.5rem;
    opacity: 0.6;
    transition: opacity 0.2s;
  }
  
  .action-btn:hover, .action-btn.active {
    opacity: 1;
  }
  
  .delete-btn:hover {
    color: #ef4444;
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