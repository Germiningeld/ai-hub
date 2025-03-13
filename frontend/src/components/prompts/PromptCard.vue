<template>
    <div class="prompt-card">
      <div class="prompt-header">
        <h3 class="prompt-title">{{ prompt.title }}</h3>
        <div class="prompt-actions">
          <button 
            @click.stop="$emit('toggle-favorite', prompt)" 
            class="action-btn" 
            :class="{ 'active': prompt.is_favorite }"
            title="Добавить в избранное"
          >
            ⭐
          </button>
          <button 
            @click.stop="$emit('edit', prompt)" 
            class="action-btn"
            title="Редактировать"
          >
            ✏️
          </button>
          <button 
            @click.stop="$emit('delete', prompt)" 
            class="action-btn delete-btn"
            title="Удалить"
          >
            🗑️
          </button>
        </div>
      </div>
      
      <div class="prompt-content">
        {{ truncate(prompt.content, 150) }}
      </div>
      
      <div class="prompt-footer">
        <div class="prompt-meta">
          <span v-if="prompt.category" class="prompt-category" :style="{ backgroundColor: getCategoryColor(prompt.category_id) + '33' }">
            {{ getCategoryName(prompt.category_id) }}
          </span>
        </div>
        <button @click.stop="$emit('use', prompt)" class="use-prompt-btn">
          Использовать
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { useCategoriesStore } from '@/stores/categories';
  
  const props = defineProps({
    prompt: {
      type: Object,
      required: true
    }
  });
  
  const categoriesStore = useCategoriesStore();
  
  const getCategoryName = (categoryId) => {
    const category = categoriesStore.categories.find(c => c.id === categoryId);
    return category ? category.name : '';
  };
  
  const getCategoryColor = (categoryId) => {
    const category = categoriesStore.categories.find(c => c.id === categoryId);
    return category ? category.color : '#888888';
  };
  
  const truncate = (text, maxLength) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };
  </script>
  
  <style scoped>
  .prompt-card {
    background-color: var(--background-color);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    height: 100%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .prompt-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .prompt-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  
  .prompt-title {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
  }
  
  .prompt-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .action-btn {
    background: none;
    border: none;
    font-size: 1rem;
    padding: 0.25rem;
    opacity: 0.6;
    transition: opacity 0.2s;
  }
  
  .action-btn:hover, .action-btn.active {
    opacity: 1;
  }
  
  .delete-btn:hover {
    color: #ef4444;
  }
  
  .prompt-content {
    flex: 1;
    font-size: 0.875rem;
    color: #4b5563;
    line-height: 1.4;
    white-space: pre-line;
  }
  
  .prompt-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
  }
  
  .prompt-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .prompt-category {
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
  }
  
  .use-prompt-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    transition: background-color 0.2s;
  }
  
  .use-prompt-btn:hover {
    background-color: #2563eb;
  }
  </style>