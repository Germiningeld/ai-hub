<template>
    <div class="modal-overlay" @click="closeModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ editing ? 'Редактировать промпт' : 'Новый промпт' }}</h2>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="savePrompt">
            <div class="form-group">
              <label for="prompt-title">Название</label>
              <input 
                type="text" 
                id="prompt-title" 
                v-model="formData.title" 
                required 
                placeholder="Введите название промпта"
              />
            </div>
            
            <div class="form-group">
              <label for="prompt-content">Содержание</label>
              <textarea 
                id="prompt-content" 
                v-model="formData.content" 
                required 
                placeholder="Введите текст промпта"
                rows="8"
              ></textarea>
              <p class="help-text">
                Используйте {переменные} в фигурных скобках для обозначения мест, которые нужно заполнить.
              </p>
            </div>
            
            <div class="form-group">
              <label for="prompt-description">Описание (опционально)</label>
              <textarea 
                id="prompt-description" 
                v-model="formData.description" 
                placeholder="Краткое описание промпта"
                rows="3"
              ></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="prompt-category">Категория</label>
                <select id="prompt-category" v-model="formData.category_id">
                  <option value="">Без категории</option>
                  <option 
                    v-for="category in categories" 
                    :key="category.id" 
                    :value="category.id"
                  >
                    {{ category.name }}
                  </option>
                </select>
              </div>
              
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.is_favorite" />
                  <span>Добавить в избранное</span>
                </label>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModal" class="cancel-btn">Отмена</button>
              <button type="submit" class="save-btn">{{ editing ? 'Сохранить' : 'Создать' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  
  const props = defineProps({
    editing: {
      type: Boolean,
      default: false
    },
    prompt: {
      type: Object,
      default: () => ({})
    },
    categories: {
      type: Array,
      default: () => []
    }
  });
  
  const emit = defineEmits(['close', 'save']);
  
  // Форма с данными
  const formData = ref({
    title: '',
    content: '',
    description: '',
    category_id: '',
    is_favorite: false
  });
  
  // Инициализация формы данными из пропса prompt, если это редактирование
  onMounted(() => {
    if (props.editing && props.prompt) {
      formData.value = {
        title: props.prompt.title || '',
        content: props.prompt.content || '',
        description: props.prompt.description || '',
        category_id: props.prompt.category_id || '',
        is_favorite: props.prompt.is_favorite || false
      };
    }
  });
  
  const closeModal = () => {
    emit('close');
  };
  
  const savePrompt = () => {
    emit('save', { ...formData.value });
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }
  
  .modal-container {
    background-color: var(--background-color);
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .modal-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6b7280;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  .form-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.25rem;
  }
  
  .form-row .form-group {
    flex: 1;
    margin-bottom: 0;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input[type="text"],
  textarea,
  select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: inherit;
  }
  
  .help-text {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
  }
  
  .checkbox-group {
    display: flex;
    align-items: center;
    margin-top: 1.5rem;
  }
  
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }
  
  .cancel-btn {
    padding: 0.75rem 1.5rem;
    background-color: #e5e7eb;
    color: #1f2937;
    border: none;
    border-radius: 0.25rem;
    font-weight: 500;
  }
  
  .save-btn {
    padding: 0.75rem 1.5rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    font-weight: 500;
  }
  </style>