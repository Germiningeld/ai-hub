import { defineStore } from 'pinia';
import modelService from '@/services/modelService';

export const useModelStore = defineStore('model', {
  state: () => ({
    availableModels: [],
    modelPreferences: [],
    defaultModels: {},
    loading: false,
    error: null
  }),

  getters: {
    // Получение списка доступных моделей
    getAvailableModels: (state) => state.availableModels,

    // Получение списка предпочтений моделей
    getModelPreferences: (state) => state.modelPreferences,

    // Получение моделей по умолчанию
    getDefaultModels: (state) => state.defaultModels,

    // Проверка загрузки
    isLoading: (state) => state.loading,

    // Получение ошибки
    getError: (state) => state.error,

    // Получение модели по ID
    getModelById: (state) => (modelId) => {
      return state.availableModels.find(model => model.id === modelId);
    },

    // Получение моделей по провайдеру
    getModelsByProvider: (state) => (provider) => {
      return state.availableModels.filter(model => model.provider === provider);
    }
  },

  actions: {
    // Получение списка доступных моделей
    async fetchAvailableModels() {
      this.loading = true;
      this.error = null;

      try {
        const response = await modelService.getAvailableModels();
        this.availableModels = response.data.models || [];
        return this.availableModels;
      } catch (error) {
        this.error = error.response?.data?.detail?.error_message || error.message;
        console.error('Error fetching available models:', error);
        return [];
      } finally {
        this.loading = false;
      }
    },

    // Получение настроек моделей пользователя
    async fetchModelPreferences() {
      this.loading = true;
      this.error = null;

      try {
        const response = await modelService.getModelPreferences();
        this.modelPreferences = response.data || [];
        return this.modelPreferences;
      } catch (error) {
        this.error = error.response?.data?.detail?.error_message || error.message;
        console.error('Error fetching model preferences:', error);
        return [];
      } finally {
        this.loading = false;
      }
    },

    // Получение настроек моделей по умолчанию
    async fetchDefaultModelPreferences() {
      this.loading = true;
      this.error = null;

      try {
        const response = await modelService.getDefaultModelPreferences();
        this.defaultModels = response.data || {};
        return this.defaultModels;
      } catch (error) {
        this.error = error.response?.data?.detail?.error_message || error.message;
        console.error('Error fetching default model preferences:', error);
        return {};
      } finally {
        this.loading = false;
      }
    },

    // Создание настройки модели
    async createModelPreference(preferenceData) {
      this.loading = true;
      this.error = null;

      try {
        const response = await modelService.createModelPreference(preferenceData);
        // Обновляем список предпочтений
        await this.fetchModelPreferences();
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail?.error_message || error.message;
        console.error('Error creating model preference:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Обновление настройки модели
    async updateModelPreference(preferenceId, preferenceData) {
      this.loading = true;
      this.error = null;

      try {
        const response = await modelService.updateModelPreference(preferenceId, preferenceData);
        // Обновляем список предпочтений
        await this.fetchModelPreferences();
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail?.error_message || error.message;
        console.error('Error updating model preference:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Удаление настройки модели
    async deleteModelPreference(preferenceId) {
      this.loading = true;
      this.error = null;

      try {
        await modelService.deleteModelPreference(preferenceId);
        // Обновляем список предпочтений
        await this.fetchModelPreferences();
        return true;
      } catch (error) {
        this.error = error.response?.data?.detail?.error_message || error.message;
        console.error('Error deleting model preference:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Сброс состояния хранилища
    resetState() {
      this.availableModels = [];
      this.modelPreferences = [];
      this.defaultModels = {};
      this.loading = false;
      this.error = null;
    }
  }
});