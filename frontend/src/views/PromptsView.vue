<template>
    <div class="prompts-container">
      <div class="prompts-header">
        <div class="filter-container">
          <div class="search-container">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Поиск промптов..." 
              class="search-input"
            />
          </div>
          
          <div class="category-filter">
            <select v-model="selectedCategory" class="category-select">
              <option value="all">Все категории</option>
              <option 
                v-for="category in categories" 
                :key="category.id" 
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>
          
          <div class="favorite-filter">
            <label class="favorite-label">
              <input type="checkbox" v-model="showFavoritesOnly" />
              Только избранные
            </label>
          </div>
        </div>
        
        <button @click="showAddPromptModal = true" class="add-prompt-btn">
          <span>+</span> Новый промпт
        </button>
      </div>
      
      <div class="prompts-grid">
        <div v-if="loading" class="prompts-loading">
          <div class="loading-spinner"></div>
          <p>Загрузка промптов...</p>
        </div>
        
        <div v-else-if="error" class="prompts-error">
          <p>{{ error }}</p>
          <button @click="fetchPrompts" class="retry-button">Повторить</button>
        </div>
        
        <template v-else>
          <PromptCard 
            v-for="prompt in filteredPrompts" 
            :key="prompt.id" 
            :prompt="prompt"
            @edit="editPrompt"
            @delete="confirmDeletePrompt"
            @toggle-favorite="toggleFavorite"
            @use="usePrompt"
          />
          
          <div v-if="filteredPrompts.length === 0" class="empty-state">
            <p>Промпты не найдены</p>
            <button @click="showAddPromptModal = true" class="create-prompt-btn">
              Создать новый промпт
            </button>
          </div>
        </template>
      </div>
      
      <!-- Модальное окно для добавления/редактирования промпта -->
      <PromptModal
        v-if="showAddPromptModal"
        :editing="!!editingPrompt"
        :prompt="editingPrompt"
        :categories="categories"
        @close="closePromptModal"
        @save="savePrompt"
      />
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import PromptCard from '@/components/prompts/PromptCard.vue';
  import PromptModal from '@/components/prompts/PromptModal.vue';
  import { usePromptsStore } from '@/stores/prompts';
  import { useCategoriesStore } from '@/stores/categories';
  import { useRouter } from 'vue-router';
  
  const router = useRouter();
  const promptsStore = usePromptsStore();
  const categoriesStore = useCategoriesStore();
  
  const loading = ref(true);
  const error = ref(null);
  const searchQuery = ref('');
  const selectedCategory = ref('all');
  const showFavoritesOnly = ref(false);
  const showAddPromptModal = ref(false);
  const editingPrompt = ref(null);
  
  const categories = computed(() => categoriesStore.categories);
  
  const filteredPrompts = computed(() => {
    let result = [...promptsStore.prompts];
    
    // Фильтрация по поисковому запросу
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(prompt => 
        prompt.title.toLowerCase().includes(query) || 
        prompt.content.toLowerCase().includes(query) ||
        prompt.description?.toLowerCase().includes(query)
      );
    }
    
    // Фильтрация по категории
    if (selectedCategory.value !== 'all') {
      result = result.filter(prompt => 
        prompt.category_id === parseInt(selectedCategory.value)
      );
    }
    
    // Фильтрация по избранным
    if (showFavoritesOnly.value) {
      result = result.filter(prompt => prompt.is_favorite);
    }
    
    return result;
  });
  
  const fetchPrompts = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      await promptsStore.fetchPrompts();
    } catch (err) {
      error.value = 'Ошибка при загрузке промптов. Попробуйте позже.';
      console.error('Error fetching prompts:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const fetchCategories = async () => {
    try {
      await categoriesStore.fetchCategories();
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };
  
  const editPrompt = (prompt) => {
    editingPrompt.value = { ...prompt };
    showAddPromptModal.value = true;
  };
  
  const confirmDeletePrompt = (prompt) => {
    if (confirm(`Вы уверены, что хотите удалить промпт "${prompt.title}"?`)) {
      deletePrompt(prompt.id);
    }
  };
  
  const deletePrompt = async (promptId) => {
    try {
      await promptsStore.deletePrompt(promptId);
    } catch (error) {
      console.error('Error deleting prompt:', error);
    }
  };
  
  const toggleFavorite = async (prompt) => {
    try {
      await promptsStore.updatePrompt({
        id: prompt.id,
        is_favorite: !prompt.is_favorite
      });
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };
  
  const closePromptModal = () => {
    showAddPromptModal.value = false;
    editingPrompt.value = null;
  };
  
  const savePrompt = async (promptData) => {
    try {
      if (editingPrompt.value) {
        await promptsStore.updatePrompt({
          id: editingPrompt.value.id,
          ...promptData
        });
      } else {
        await promptsStore.createPrompt(promptData);
      }
      closePromptModal();
    } catch (error) {
      console.error('Error saving prompt:', error);
    }
  };
  
  const usePrompt = (prompt) => {
    // Перенаправление на страницу чата с предзаполненным промптом
    router.push({
      path: '/chat',
      query: { prompt_id: prompt.id }
    });
  };
  
  onMounted(async () => {
    await Promise.all([fetchPrompts(), fetchCategories()]);
  });
  </script>
  
  <style scoped>
  .prompts-container {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .prompts-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .filter-container {
    display: flex;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
  }
  
  .search-input {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    width: 250px;
  }
  
  .category-select {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .favorite-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }
  
  .add-prompt-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    cursor: pointer;
  }
  
  .prompts-grid {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }
  
  .prompts-loading, .prompts-error {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
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
  
  .empty-state {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    text-align: center;
    color: #6b7280;
  }
  
  .create-prompt-btn {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
  }
  </style>