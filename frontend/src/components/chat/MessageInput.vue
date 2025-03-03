<template>
    <div class="message-input-container">
      <div class="input-toolbar">
        <div class="prompt-selector">
          <button 
            @click="showPromptSelector = !showPromptSelector" 
            class="prompt-btn"
            title="Выбрать промпт"
          >
            📝
          </button>
          <div v-if="showPromptSelector" class="prompt-dropdown">
            <div class="prompt-search">
              <input 
                type="text" 
                v-model="promptSearch" 
                placeholder="Поиск промптов..." 
                class="prompt-search-input"
              />
            </div>
            <div class="prompt-list">
              <div 
                v-for="prompt in filteredPrompts" 
                :key="prompt.id"
                class="prompt-item"
                @click="insertPrompt(prompt)"
              >
                <div class="prompt-title">{{ prompt.title }}</div>
                <div class="prompt-preview">{{ truncate(prompt.content, 60) }}</div>
              </div>
              <div v-if="filteredPrompts.length === 0" class="prompt-empty">
                Нет промптов для отображения
              </div>
            </div>
          </div>
        </div>
        
        <div class="model-selector">
          <select v-model="selectedModel" class="model-select">
            <option 
              v-for="model in availableModels" 
              :key="model.id" 
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="input-area">
        <textarea 
          v-model="messageText" 
          placeholder="Введите сообщение..." 
          class="message-textarea"
          :disabled="disabled || sending"
          @keydown.enter.ctrl="sendMessage"
          @keydown.enter.meta="sendMessage"
          ref="textareaRef"
        ></textarea>
        
        <div class="input-controls">
          <div class="token-counter" :class="{ 'token-limit': tokenCount > 2000 }">
            {{ tokenCount }} токенов
          </div>
          
          <button 
            @click="sendMessage" 
            class="send-button"
            :disabled="!canSend || sending"
          >
            {{ sending ? 'Отправка...' : 'Отправить' }}
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch } from 'vue';
  import { usePromptsStore } from '@/stores/prompts';
  import { threadsService } from '@/services/threadsService';
  
  const props = defineProps({
    threadId: {
      type: [Number, String],
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    }
  });
  
  const emit = defineEmits(['message-sent']);
  
  const promptsStore = usePromptsStore();
  
  const messageText = ref('');
  const sending = ref(false);
  const tokenCount = ref(0);
  const showPromptSelector = ref(false);
  const promptSearch = ref('');
  const textareaRef = ref(null);
  const selectedModel = ref('gpt-4o'); // По умолчанию
  
  // Моковые данные для упрощения примера
  const availableModels = ref([
    { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai' },
    { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'anthropic' }
  ]);
  
  const filteredPrompts = computed(() => {
    if (!promptSearch.value) {
      return promptsStore.prompts;
    }
    
    const search = promptSearch.value.toLowerCase();
    return promptsStore.prompts.filter(prompt => 
      prompt.title.toLowerCase().includes(search) || 
      prompt.content.toLowerCase().includes(search)
    );
  });
  
  const canSend = computed(() => {
    return messageText.value.trim() !== '' && !props.disabled;
  });
  
  const fetchPrompts = async () => {
    if (promptsStore.prompts.length === 0) {
      try {
        await promptsStore.fetchPrompts();
      } catch (error) {
        console.error('Error fetching prompts:', error);
      }
    }
  };
  
  const insertPrompt = (prompt) => {
    messageText.value = prompt.content;
    showPromptSelector.value = false;
    updateTokenCount();
    
    // Фокус на текстовое поле и перемещение курсора в конец
    nextTick(() => {
      textareaRef.value.focus();
      const length = messageText.value.length;
      textareaRef.value.setSelectionRange(length, length);
    });
  };
  
  const updateTokenCount = async () => {
    if (!messageText.value.trim()) {
      tokenCount.value = 0;
      return;
    }
    
    try {
      const response = await threadsService.countTokens({
        provider: getModelProvider(selectedModel.value),
        model: selectedModel.value,
        text: messageText.value
      });
      
      tokenCount.value = response.token_count;
    } catch (error) {
      console.error('Error counting tokens:', error);
      // Примерная оценка: 1 токен ~= 4 символа
      tokenCount.value = Math.ceil(messageText.value.length / 4);
    }
  };
  
  const getModelProvider = (modelId) => {
    const model = availableModels.value.find(m => m.id === modelId);
    return model ? model.provider : 'openai';
  };
  
  const sendMessage = async () => {
    if (!canSend.value || sending.value) return;
    
    sending.value = true;
    
    const message = {
      content: messageText.value.trim(),
      system_prompt: '', // Можно добавить опционально в интерфейсе
      model: selectedModel.value,
      provider: getModelProvider(selectedModel.value),
      max_tokens: 2000,
      temperature: 0.7
    };
    
    try {
      await threadsService.streamMessage(props.threadId, message, () => {});
      messageText.value = '';
      tokenCount.value = 0;
      emit('message-sent');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      sending.value = false;
    }
  };
  
  const truncate = (text, maxLength) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };
  
  // Обновление счетчика токенов при изменении текста
  watch(messageText, () => {
    updateTokenCount();
  });
  
  onMounted(() => {
    fetchPrompts();
    textareaRef.value.focus();
  });
  </script>
  
  <style scoped>
  .message-input-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .input-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .prompt-selector {
    position: relative;
  }
  
  .prompt-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0.5rem;
    border-radius: 0.25rem;
    transition: background-color 0.2s;
  }
  
  .prompt-btn:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .prompt-dropdown {
    position: absolute;
    bottom: 100%;
    left: 0;
    width: 300px;
    max-height: 400px;
    background-color: var(--background-color);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 10;
    display: flex;
    flex-direction: column;
  }
  
  .prompt-search {
    padding: 0.75rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .prompt-search-input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .prompt-list {
    overflow-y: auto;
    max-height: 300px;
  }
  
  .prompt-item {
    padding: 0.75rem;
    cursor: pointer;
    border-bottom: 1px solid var(--border-color);
  }
  
  .prompt-item:last-child {
    border-bottom: none;
  }
  
  .prompt-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .prompt-title {
    font-weight: 500;
    margin-bottom: 0.25rem;
  }
  
  .prompt-preview {
    font-size: 0.875rem;
    color: #6b7280;
  }
  
  .prompt-empty {
    padding: 1rem;
    text-align: center;
    color: #6b7280;
  }
  
  .model-selector {
    display: flex;
    align-items: center;
  }
  
  .model-select {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .input-area {
    position: relative;
  }
  
  .message-textarea {
    width: 100%;
    min-height: 100px;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    background-color: var(--background-color);
    color: var(--text-color);
    resize: vertical;
    font-family: inherit;
    line-height: 1.5;
  }
  
  .input-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.5rem;
  }
  
  .token-counter {
    font-size: 0.875rem;
    color: #6b7280;
  }
  
  .token-limit {
    color: #ef4444;
  }
  
  .send-button {
    padding: 0.5rem 1rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .send-button:hover:not(:disabled) {
    background-color: #2563eb;
  }
  
  .send-button:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
  }
  </style>