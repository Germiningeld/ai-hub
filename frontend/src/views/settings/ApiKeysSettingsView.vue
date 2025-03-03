<template>
    <div class="api-keys-settings">
      <h2 class="section-title">API ключи</h2>
      <p class="section-description">
        Настройте ваши ключи API для использования с различными провайдерами AI моделей.
      </p>
      
      <div class="api-keys-list">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Загрузка API ключей...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button @click="fetchApiKeys" class="retry-button">Повторить</button>
        </div>
        
        <template v-else>
          <div v-for="provider in providers" :key="provider.id" class="api-key-card">
            <div class="provider-info">
              <div class="provider-icon" :style="{ backgroundColor: provider.color }">
                {{ provider.icon }}
              </div>
              <div class="provider-details">
                <h3>{{ provider.name }}</h3>
                <p>{{ provider.description }}</p>
              </div>
            </div>
            
            <div class="key-status">
              <template v-if="getApiKeyForProvider(provider.id)">
                <div class="status-badge active">Активен</div>
                <button @click="() => editApiKey(getApiKeyForProvider(provider.id))" class="edit-btn">
                  Изменить
                </button>
              </template>
              <template v-else>
                <div class="status-badge inactive">Не настроен</div>
                <button @click="() => addNewApiKey(provider.id)" class="add-btn">
                  Добавить
                </button>
              </template>
            </div>
          </div>
          
          <div v-if="apiKeys.length === 0" class="empty-state">
            <p>У вас еще нет настроенных API ключей</p>
            <p>Добавьте ключи для начала работы с AI моделями</p>
          </div>
        </template>
      </div>
      
      <!-- Модальное окно для добавления/редактирования API ключа -->
      <ApiKeyModal
        v-if="showModal"
        :providers="providers"
        :selected-provider="selectedProvider"
        :editing-key="editingKey"
        @close="closeModal"
        @save="saveApiKey"
      />
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import ApiKeyModal from '@/components/settings/ApiKeyModal.vue';
  import { useApiKeysStore } from '@/stores/apiKeys';
  
  const apiKeysStore = useApiKeysStore();
  
  const loading = ref(true);
  const error = ref(null);
  const showModal = ref(false);
  const selectedProvider = ref(null);
  const editingKey = ref(null);
  
  // Список поддерживаемых провайдеров
  const providers = ref([
    {
      id: 'openai',
      name: 'OpenAI',
      icon: '🤖',
      color: '#10a37f',
      description: 'API для доступа к моделям GPT-4, GPT-3.5 и другим от OpenAI'
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      icon: '🧠',
      color: '#b980ff',
      description: 'API для доступа к моделям Claude от Anthropic'
    }
  ]);
  
  const apiKeys = computed(() => apiKeysStore.apiKeys);
  
  const getApiKeyForProvider = (providerId) => {
    return apiKeys.value.find(key => key.provider === providerId);
  };
  
  const fetchApiKeys = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      await apiKeysStore.fetchApiKeys();
    } catch (err) {
      error.value = 'Ошибка при загрузке API ключей. Попробуйте позже.';
      console.error('Error fetching API keys:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const addNewApiKey = (providerId) => {
    selectedProvider.value = providerId;
    editingKey.value = null;
    showModal.value = true;
  };
  
  const editApiKey = (apiKey) => {
    selectedProvider.value = apiKey.provider;
    editingKey.value = { ...apiKey };
    showModal.value = true;
  };
  
  const closeModal = () => {
    showModal.value = false;
    selectedProvider.value = null;
    editingKey.value = null;
  };
  
  const saveApiKey = async (keyData) => {
    try {
      if (editingKey.value) {
        await apiKeysStore.updateApiKey({
          id: editingKey.value.id,
          ...keyData
        });
      } else {
        await apiKeysStore.createApiKey(keyData);
      }
      closeModal();
    } catch (error) {
      console.error('Error saving API key:', error);
    }
  };
  
  onMounted(fetchApiKeys);
  </script>
  
  <style scoped>
  .api-keys-settings {
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
  
  .api-keys-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .api-key-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem;
    background-color: var(--background-color);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
  }
  
  .provider-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .provider-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 0.5rem;
    font-size: 1.5rem;
  }
  
  .provider-details h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1.125rem;
  }
  
  .provider-details p {
    margin: 0;
    font-size: 0.875rem;
    color: #6b7280;
    max-width: 400px;
  }
  
  .key-status {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .status-badge {
    padding: 0.375rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .status-badge.active {
    background-color: rgba(16, 185, 129, 0.1);
    color: #065f46;
  }
  
  .status-badge.inactive {
    background-color: rgba(239, 68, 68, 0.1);
    color: #991b1b;
  }
  
  .edit-btn, .add-btn {
    padding: 0.5rem 0.75rem;
    border: none;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    cursor: pointer;
  }
  
  .edit-btn {
    background-color: #e5e7eb;
    color: #1f2937;
  }
  
  .add-btn {
    background-color: var(--primary-color);
    color: white;
  }
  
  .loading-state, .error-state, .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
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
  
  .empty-state p {
    margin: 0.5rem 0;
  }
  </style>