import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiKeysService } from '@/services/apiKeysService';

export const useApiKeysStore = defineStore('apiKeys', () => {
  const apiKeys = ref([]);
  
  async function fetchApiKeys() {
    try {
      const data = await apiKeysService.getApiKeys();
      apiKeys.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching API keys:', error);
      throw error;
    }
  }
  
  async function createApiKey(keyData) {
    try {
      const newKey = await apiKeysService.createApiKey(keyData);
      apiKeys.value.push(newKey);
      return newKey;
    } catch (error) {
      console.error('Error creating API key:', error);
      throw error;
    }
  }
  
  async function updateApiKey(keyData) {
    try {
      const updatedKey = await apiKeysService.updateApiKey(keyData.id, keyData);
      const index = apiKeys.value.findIndex(key => key.id === keyData.id);
      
      if (index !== -1) {
        apiKeys.value[index] = updatedKey;
      }
      
      return updatedKey;
    } catch (error) {
      console.error('Error updating API key:', error);
      throw error;
    }
  }
  
  async function deleteApiKey(keyId) {
    try {
      await apiKeysService.deleteApiKey(keyId);
      apiKeys.value = apiKeys.value.filter(key => key.id !== keyId);
    } catch (error) {
      console.error('Error deleting API key:', error);
      throw error;
    }
  }
  
  return {
    apiKeys,
    fetchApiKeys,
    createApiKey,
    updateApiKey,
    deleteApiKey
  };
});