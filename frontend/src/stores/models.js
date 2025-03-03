import { defineStore } from 'pinia';
import { ref } from 'vue';
import { modelsService } from '@/services/modelsService';

export const useModelsStore = defineStore('models', () => {
  const availableModels = ref([]);
  const modelPreferences = ref([]);
  const defaultPreferences = ref({});
  
  async function fetchAvailableModels() {
    try {
      const data = await modelsService.getAvailableModels();
      availableModels.value = data.models || [];
      return data;
    } catch (error) {
      console.error('Error fetching available models:', error);
      throw error;
    }
  }
  
  async function fetchModelPreferences() {
    try {
      const data = await modelsService.getModelPreferences();
      modelPreferences.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching model preferences:', error);
      throw error;
    }
  }
  
  async function fetchDefaultPreferences() {
    try {
      const data = await modelsService.getDefaultPreferences();
      defaultPreferences.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching default preferences:', error);
      throw error;
    }
  }
  
  async function createModelPreference(preferenceData) {
    try {
      const data = await modelsService.createModelPreference(preferenceData);
      modelPreferences.value.push(data);
      return data;
    } catch (error) {
      console.error('Error creating model preference:', error);
      throw error;
    }
  }
  
  async function updateModelPreference(preferenceData) {
    try {
      const data = await modelsService.updateModelPreference(preferenceData.id, preferenceData);
      const index = modelPreferences.value.findIndex(p => p.id === preferenceData.id);
      if (index !== -1) {
        modelPreferences.value[index] = data;
      }
      return data;
    } catch (error) {
      console.error('Error updating model preference:', error);
      throw error;
    }
  }
  
  async function deleteModelPreference(preferenceId) {
    try {
      await modelsService.deleteModelPreference(preferenceId);
      modelPreferences.value = modelPreferences.value.filter(p => p.id !== preferenceId);
    } catch (error) {
      console.error('Error deleting model preference:', error);
      throw error;
    }
  }
  
  return {
    availableModels,
    modelPreferences,
    defaultPreferences,
    fetchAvailableModels,
    fetchModelPreferences,
    fetchDefaultPreferences,
    createModelPreference,
    updateModelPreference,
    deleteModelPreference
  };
});