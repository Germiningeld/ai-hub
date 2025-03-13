<template>
    <div class="model-settings">
      <h2 class="section-title">Настройки моделей</h2>
      <p class="section-description">
        Настройте параметры моделей искусственного интеллекта для вашего использования.
      </p>
      
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка настроек моделей...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="fetchModels" class="retry-button">Повторить</button>
      </div>
      
      <template v-else>
        <div class="tabs">
          <button 
            class="tab-button" 
            :class="{ 'active': activeTab === 'openai' }"
            @click="activeTab = 'openai'"
          >
            OpenAI
          </button>
          <button 
            class="tab-button" 
            :class="{ 'active': activeTab === 'anthropic' }"
            @click="activeTab = 'anthropic'"
          >
            Anthropic
          </button>
        </div>
        
        <div class="tab-content">
          <div v-if="activeTab === 'openai'">
            <h3 class="provider-title">Настройки моделей OpenAI</h3>
            <ModelPreferenceForm 
              provider="openai"
              :available-models="openaiModels"
              :preferences="openaiPreferences"
              @save="saveModelPreference"
              @delete="deleteModelPreference"
              @set-default="setDefaultModel"
            />
          </div>
          
          <div v-if="activeTab === 'anthropic'">
            <h3 class="provider-title">Настройки моделей Anthropic</h3>
            <ModelPreferenceForm 
              provider="anthropic"
              :available-models="anthropicModels"
              :preferences="anthropicPreferences"
              @save="saveModelPreference"
              @delete="deleteModelPreference"
              @set-default="setDefaultModel"
            />
          </div>
        </div>
      </template>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import ModelPreferenceForm from '@/components/settings/ModelPreferenceForm.vue';
  import { useModelsStore } from '@/stores/models';
  
  const modelsStore = useModelsStore();
  
  const loading = ref(true);
  const error = ref(null);
  const activeTab = ref('openai');
  
  // Доступные модели (обычно получены с сервера)
  const availableModels = ref([
    // OpenAI модели
    { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', description: 'Последняя версия GPT-4 с улучшенными возможностями' },
    { id: 'gpt-4', name: 'GPT-4', provider: 'openai', description: 'Продвинутая модель с улучшенными способностями рассуждения' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai', description: 'Быстрая и экономичная модель для большинства задач' },
    
    // Anthropic модели
    { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'anthropic', description: 'Самая мощная модель Claude для сложных задач' },
    { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'anthropic', description: 'Сбалансированная модель по соотношению производительности и стоимости' },
    { id: 'claude-3-haiku', name: 'Claude 3 Haiku', provider: 'anthropic', description: 'Быстрая и экономичная модель для простых задач' }
  ]);
  
  const openaiModels = computed(() => {
    return availableModels.value.filter(model => model.provider === 'openai');
  });
  
  const anthropicModels = computed(() => {
    return availableModels.value.filter(model => model.provider === 'anthropic');
  });
  
  // Предпочтения моделей пользователя
  const modelPreferences = ref([]);
  
  // Предпочтения моделей, отфильтрованные по провайдерам
  const openaiPreferences = computed(() => {
    return modelPreferences.value.filter(pref => pref.provider === 'openai');
  });
  
  const anthropicPreferences = computed(() => {
    return modelPreferences.value.filter(pref => pref.provider === 'anthropic');
  });
  
  const fetchModels = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      // Загрузка доступных моделей
      const modelsData = await modelsStore.fetchAvailableModels();
      availableModels.value = modelsData.models || [];
      
      // Загрузка предпочтений моделей
      const preferences = await modelsStore.fetchModelPreferences();
      modelPreferences.value = preferences || [];
    } catch (err) {
      error.value = 'Ошибка при загрузке настроек моделей. Попробуйте позже.';
      console.error('Error fetching models:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const saveModelPreference = async (preferenceData) => {
    try {
      let savedPreference;
      
      if (preferenceData.id) {
        // Обновление существующего предпочтения
        savedPreference = await modelsStore.updateModelPreference(preferenceData);
      } else {
        // Создание нового предпочтения
        savedPreference = await modelsStore.createModelPreference(preferenceData);
      }
      
      // Обновляем локальный список
      const index = modelPreferences.value.findIndex(p => p.id === savedPreference.id);
      if (index !== -1) {
        modelPreferences.value[index] = savedPreference;
      } else {
        modelPreferences.value.push(savedPreference);
      }
      
      return savedPreference;
    } catch (error) {
      console.error('Error saving model preference:', error);
      throw error;
    }
  };
  
  const deleteModelPreference = async (preferenceId) => {
    try {
      await modelsStore.deleteModelPreference(preferenceId);
      
      // Удаляем из локального списка
      modelPreferences.value = modelPreferences.value.filter(p => p.id !== preferenceId);
    } catch (error) {
      console.error('Error deleting model preference:', error);
      throw error;
    }
  };
  
  const setDefaultModel = async (preferenceId) => {
    try {
      const preference = modelPreferences.value.find(p => p.id === preferenceId);
      if (!preference) return;
      
      // Обновляем предпочтение, делая его по умолчанию
      await saveModelPreference({
        ...preference,
        is_default: true
      });
      
      // Обновляем все другие предпочтения для того же провайдера
      const provider = preference.provider;
      for (const pref of modelPreferences.value) {
        if (pref.provider === provider && pref.id !== preferenceId && pref.is_default) {
          await saveModelPreference({
            ...pref,
            is_default: false
          });
        }
      }
      
      // Перезагружаем все предпочтения, чтобы обновить UI
      await fetchModels();
    } catch (error) {
      console.error('Error setting default model:', error);
      throw error;
    }
  };
  
  onMounted(fetchModels);
  </script>
  
  <style scoped>
  .model-settings {
    max-width: 800px;
  }
  
  .section-title {
    margin-top: 0;
    margin-bottom: 0.75rem;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  .section-description {
    margin-bottom: 2rem;
    color: #6b7280;
  }
  
  .provider-title {
    margin-top: 0;
    margin-bottom: 1.5rem;
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  .tabs {
    display: flex;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .tab-button {
    padding: 0.75rem 1.5rem;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .tab-button.active {
    border-bottom-color: var(--primary-color);
    color: var(--primary-color);
    font-weight: 500;
  }
  
  .tab-content {
    margin-top: 1rem;
  }
  
  .loading-state, .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
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
  </style>