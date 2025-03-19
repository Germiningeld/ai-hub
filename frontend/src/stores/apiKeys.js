import { defineStore } from 'pinia';
import api from '@/services/api';

export const useApiKeysStore = defineStore('apiKeys', {
  state: () => ({
    keys: [],
    loading: false,
    error: null,
    providers: [] // Добавляем providers в state
  }),
  
  getters: {
    // Получение списка API ключей
    getAllKeys: (state) => state.keys,
    
    // Получение ключей по провайдеру
    getKeysByProvider: (state) => (provider) => {
      return state.keys.filter(key => key.provider === provider);
    },
    
    // Получение активного ключа для провайдера
    getActiveKeyForProvider: (state) => (provider) => {
      return state.keys.find(key => key.provider === provider && key.is_active);
    },
    
    // Проверка наличия активного ключа для провайдера
    hasActiveKeyForProvider: (state) => (provider) => {
      return state.keys.some(key => key.provider === provider && key.is_active);
    },
    
    // Проверка загрузки
    isLoading: (state) => state.loading,
    
    // Получение ошибки
    getError: (state) => state.error,
    
    // Получение списка доступных провайдеров
    availableProviders: (state) => state.providers
  },
  
  actions: {
    // Загрузка списка API ключей
    async fetchApiKeys() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.get('/api-keys/');
        this.keys = response.data;
        return this.keys;
      } catch (error) {
        this.error = error.response?.data?.error_message || error.message;
        console.error('Error fetching API keys:', error);
        return [];
      } finally {
        this.loading = false;
      }
    },
    
    // Загрузка списка доступных провайдеров с сервера
    async fetchProviders() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.get('/ai-models/providers?is_active=true');
        // Преобразуем ответ сервера к нужному формату
        this.providers = response.data.map(provider => ({
          id: provider.code,
          name: provider.name,
          description: provider.description || '',
          serviceClass: provider.service_class,
          providerId: provider.id
        }));
        return this.providers;
      } catch (error) {
        this.error = error.response?.data?.error_message || error.message;
        console.error('Error fetching providers:', error);
        
        // Возвращаем стандартный список на случай ошибки
        this.providers = [
          { id: 'openai', name: 'OpenAI (ChatGPT)', description: 'GPT-3.5, GPT-4, GPT-4o' },
          { id: 'anthropic', name: 'Anthropic (Claude)', description: 'Claude 3 (Haiku, Sonnet, Opus)' }
        ];
        return this.providers;
      } finally {
        this.loading = false;
      }
    },
    
    // Создание нового API ключа
    async createApiKey(keyData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.post('/api-keys/', keyData);
        // Добавляем новый ключ в массив
        this.keys.push(response.data);
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.error_message || error.message;
        console.error('Error creating API key:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // Обновление API ключа (без передачи значения ключа на сервер)
    async updateApiKey(keyId, keyData) {
      this.loading = true;
      this.error = null;
      
      try {
        // Находим текущий ключ в массиве
        const existingKey = this.keys.find(key => key.id === keyId);
        if (!existingKey) {
          throw new Error('API key not found');
        }
        
        // Создаем новый объект данных, исключая поле api_key
        const { api_key, ...dataToUpdate } = keyData;
        
        const response = await api.put(`/api-keys/${keyId}`, dataToUpdate);
        
        // Обновляем ключ в массиве
        const index = this.keys.findIndex(key => key.id === keyId);
        if (index !== -1) {
          // Обновляем запись локально, сохраняя исходное значение api_key
          this.keys[index] = {
            ...response.data,
            api_key: existingKey.api_key
          };
        }
        
        return this.keys[index];
      } catch (error) {
        this.error = error.response?.data?.error_message || error.message;
        console.error('Error updating API key:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // Удаление API ключа
    async deleteApiKey(keyId) {
      this.loading = true;
      this.error = null;
      
      try {
        await api.delete(`/api-keys/${keyId}`);
        
        // Удаляем ключ из массива
        this.keys = this.keys.filter(key => key.id !== keyId);
        
        return true;
      } catch (error) {
        this.error = error.response?.data?.error_message || error.message;
        console.error('Error deleting API key:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // Активация/деактивация ключа
    async toggleKeyStatus(keyId, isActive) {
      const keyIndex = this.keys.findIndex(key => key.id === keyId);
      if (keyIndex === -1) return false;
      
      return await this.updateApiKey(keyId, {
        is_active: isActive
      });
    },
    
    // Проверка валидности API ключа (без сохранения)
    async validateApiKey(provider, apiKey) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.post('/api-keys/validate', {
          provider,
          api_key: apiKey
        });
        
        return response.data.valid;
      } catch (error) {
        this.error = error.response?.data?.error_message || error.message;
        console.error('Error validating API key:', error);
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    // Получение списка доступных провайдеров (сохраняем для обратной совместимости)
    getAvailableProviders() {
      // Если список провайдеров пуст, возвращаем стандартный набор
      if (this.providers.length === 0) {
        return [
          { id: 'openai', name: 'OpenAI (ChatGPT)', description: 'GPT-3.5, GPT-4, GPT-4o' },
          { id: 'anthropic', name: 'Anthropic (Claude)', description: 'Claude 3 (Haiku, Sonnet, Opus)' }
        ];
      }
      return this.providers;
    },
    
    // Инициализация списка провайдеров значениями по умолчанию
    initDefaultProviders() {
      if (this.providers.length === 0) {
        this.providers = [
          { id: 'openai', name: 'OpenAI (ChatGPT)', description: 'GPT-3.5, GPT-4, GPT-4o' },
          { id: 'anthropic', name: 'Anthropic (Claude)', description: 'Claude 3 (Haiku, Sonnet, Opus)' }
        ];
      }
    },
    
    // Сброс состояния хранилища
    resetState() {
      this.keys = [];
      this.loading = false;
      this.error = null;
      this.providers = [];
    },
    
    // Очистка ошибки
    clearError() {
      this.error = null;
    }
  },
  
  // Сохраняем данные о ключах в localStorage для быстрого доступа
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'apiKeys',
        storage: localStorage,
        paths: ['keys', 'providers'] // Добавляем провайдеров в персистентное хранилище
      }
    ]
  }
});