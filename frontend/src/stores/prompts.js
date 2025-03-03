import { defineStore } from 'pinia';
import { ref } from 'vue';
import { promptsService } from '@/services/promptsService';

export const usePromptsStore = defineStore('prompts', () => {
  const prompts = ref([]);
  
  async function fetchPrompts(params = {}) {
    try {
      const data = await promptsService.getPrompts(params);
      prompts.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching prompts:', error);
      throw error;
    }
  }
  
  async function fetchPrompt(promptId) {
    try {
      const prompt = await promptsService.getPrompt(promptId);
      return prompt;
    } catch (error) {
      console.error(`Error fetching prompt ${promptId}:`, error);
      throw error;
    }
  }
  
  async function createPrompt(promptData) {
    try {
      const newPrompt = await promptsService.createPrompt(promptData);
      prompts.value.unshift(newPrompt);
      return newPrompt;
    } catch (error) {
      console.error('Error creating prompt:', error);
      throw error;
    }
  }
  
  async function updatePrompt(promptData) {
    try {
      const updatedPrompt = await promptsService.updatePrompt(promptData.id, promptData);
      
      const index = prompts.value.findIndex(prompt => prompt.id === promptData.id);
      if (index !== -1) {
        prompts.value[index] = updatedPrompt;
      }
      
      return updatedPrompt;
    } catch (error) {
      console.error(`Error updating prompt ${promptData.id}:`, error);
      throw error;
    }
  }
  
  async function deletePrompt(promptId) {
    try {
      await promptsService.deletePrompt(promptId);
      prompts.value = prompts.value.filter(prompt => prompt.id !== promptId);
    } catch (error) {
      console.error(`Error deleting prompt ${promptId}:`, error);
      throw error;
    }
  }
  
  return {
    prompts,
    fetchPrompts,
    fetchPrompt,
    createPrompt,
    updatePrompt,
    deletePrompt
  };
});