<template>
    <div class="chat-container">
      <div class="threads-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
        <div class="threads-header">
          <h3>Треды</h3>
          <button class="new-thread-btn" @click="createNewThread">
            <span>+</span> Новый тред
          </button>
          <button class="collapse-btn" @click="toggleSidebar">
            <span v-if="sidebarCollapsed">›</span>
            <span v-else>‹</span>
          </button>
        </div>
        
        <div class="search-container">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Поиск тредов..." 
            class="search-input"
          />
        </div>
        
        <div class="threads-list">
          <ThreadListItem 
            v-for="thread in filteredThreads" 
            :key="thread.id" 
            :thread="thread" 
            :active="activeThreadId === thread.id"
            @click="selectThread(thread)"
          />
          
          <div v-if="filteredThreads.length === 0" class="empty-state">
            <p>Нет тредов для отображения</p>
          </div>
        </div>
      </div>
      
      <div class="chat-main">
        <div v-if="!activeThread" class="empty-chat">
          <div class="welcome-message">
            <h2>Добро пожаловать в AIHub!</h2>
            <p>Выберите существующий тред или создайте новый, чтобы начать общение.</p>
            <button class="create-thread-btn" @click="createNewThread">
              Создать новый тред
            </button>
          </div>
        </div>
        
        <ThreadDetail v-else :thread-id="activeThreadId" />
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import ThreadListItem from '@/components/chat/ThreadListItem.vue';
  import ThreadDetail from '@/components/chat/ThreadDetail.vue';
  import { useThreadsStore } from '@/stores/threads';
  
  const route = useRoute();
  const router = useRouter();
  const threadsStore = useThreadsStore();
  
  const sidebarCollapsed = ref(false);
  const searchQuery = ref('');
  const activeThreadId = ref(null);
  
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  };
  
  const filteredThreads = computed(() => {
    if (!searchQuery.value) {
      return threadsStore.threads;
    }
    
    const query = searchQuery.value.toLowerCase();
    return threadsStore.threads.filter(thread => 
      thread.title.toLowerCase().includes(query)
    );
  });
  
  const activeThread = computed(() => {
    if (!activeThreadId.value) return null;
    return threadsStore.threads.find(t => t.id === activeThreadId.value);
  });
  
  const selectThread = (thread) => {
    activeThreadId.value = thread.id;
    router.push(`/chat/${thread.id}`);
  };
  
  const createNewThread = async () => {
    try {
      const newThread = await threadsStore.createThread({
        title: 'Новый тред',
        provider: 'openai',
        model: 'gpt-4o',
        initial_message: '',
        system_prompt: '',
        is_pinned: false,
        is_archived: false
      });
      
      selectThread(newThread);
    } catch (error) {
      console.error('Error creating new thread:', error);
    }
  };
  
  onMounted(async () => {
    // Загружаем треды
    await threadsStore.fetchThreads();
    
    // Если в URL указан ID треда, активируем его
    const threadId = parseInt(route.params.id);
    if (threadId) {
      activeThreadId.value = threadId;
    } else if (threadsStore.threads.length > 0) {
      // Если треды есть, выбираем первый
      selectThread(threadsStore.threads[0]);
    }
  });
  </script>
  
  <style scoped>
  .chat-container {
    display: flex;
    height: calc(100vh - 64px); /* Высота экрана минус высота шапки */
    overflow: hidden;
  }
  
  .threads-sidebar {
    width: 300px;
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
  }
  
  .threads-sidebar.collapsed {
    width: 0;
  }
  
  .threads-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .threads-header h3 {
    margin: 0;
    font-weight: 600;
  }
  
  .new-thread-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    cursor: pointer;
  }
  
  .collapse-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0.25rem;
  }
  
  .search-container {
    padding: 0.75rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .search-input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .threads-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
  }
  
  .chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .empty-chat {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
  
  .welcome-message {
    text-align: center;
    max-width: 500px;
  }
  
  .welcome-message h2 {
    margin-bottom: 1rem;
  }
  
  .welcome-message p {
    margin-bottom: 2rem;
    color: #6b7280;
  }
  
  .create-thread-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    cursor: pointer;
  }
  
  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100px;
    color: #6b7280;
  }
  
  @media (max-width: 768px) {
    .chat-container {
      flex-direction: column;
    }
    
    .threads-sidebar {
      width: 100%;
      max-height: 50vh;
    }
    
    .threads-sidebar.collapsed {
      max-height: 0;
    }
  }
  </style>