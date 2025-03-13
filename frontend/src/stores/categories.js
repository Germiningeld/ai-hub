import { defineStore } from 'pinia';
import { ref } from 'vue';
import { categoriesService } from '@/services/categoriesService';

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref([]);
  
  async function fetchCategories() {
    try {
      const data = await categoriesService.getCategories();
      categories.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  }
  
  async function createCategory(categoryData) {
    try {
      const newCategory = await categoriesService.createCategory(categoryData);
      categories.value.push(newCategory);
      return newCategory;
    } catch (error) {
      console.error('Error creating category:', error);
      throw error;
    }
  }
  
  async function updateCategory(categoryData) {
    try {
      const updatedCategory = await categoriesService.updateCategory(categoryData.id, categoryData);
      
      const index = categories.value.findIndex(category => category.id === categoryData.id);
      if (index !== -1) {
        categories.value[index] = updatedCategory;
      }
      
      return updatedCategory;
    } catch (error) {
      console.error(`Error updating category ${categoryData.id}:`, error);
      throw error;
    }
  }
  
  async function deleteCategory(categoryId) {
    try {
      await categoriesService.deleteCategory(categoryId);
      categories.value = categories.value.filter(category => category.id !== categoryId);
    } catch (error) {
      console.error(`Error deleting category ${categoryId}:`, error);
      throw error;
    }
  }
  
  return {
    categories,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory
  };
});