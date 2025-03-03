<template>
    <div class="modal-overlay" @click="closeModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">
            {{ editingKey ? 'Редактировать API ключ' : 'Добавить API ключ' }}
          </h2>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveApiKey">
            <div class="form-group">
              <label for="provider">Провайдер</label>
              <select 
                id="provider" 
                v-model="formData.provider" 
                :disabled="editingKey"
                required
              >
                <option value="">Выберите провайдера</option>
                <option 
                  v-for="provider in providers" 
                  :key="provider.id" 
                  :value="provider.id"
                >
                  {{ provider.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="name">Название (опционально)</label>
              <input 
                type="text" 
                id="name" 
                v-model="formData.name" 
                placeholder="Например: Мой ключ OpenAI"
              />
            </div>
            
            <div class="form-group">
              <label for="api-key">API Ключ</label>
              <div class="api-key-input">
                <input 
                  :type="showKey ? 'text' : 'password'" 
                  id="api-key" 
                  v-model="formData.api_key" 
                  required
                  placeholder="Введите ваш API ключ"
                />
                <button 
                  type="button" 
                  @click="showKey = !showKey" 
                  class="toggle-visibility-btn"
                >
                  {{ showKey ? '👁️' : '👁️‍🗨️' }}
                </button>
              </div>
              <p class="help-text">
                Ваш API ключ хранится безопасно и используется только для запросов к API провайдера.
              </p>
            </div>
            
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="formData.is_active" />
                <span>Активен</span>
              </label>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModal" class="cancel-btn">Отмена</button>
              <button type="submit" class="save-btn">{{ editingKey ? 'Сохранить' : 'Добавить' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  
  const props = defineProps({
    providers: {
      type: Array,
      default: () => []
    },
    selectedProvider: {
      type: String,
      default: null
    },
    editingKey: {
      type: Object,
      default: null
    }
  });
  
  const emit = defineEmits(['close', 'save']);
  
  // Форма с данными
  const formData = ref({
    provider: '',
    name: '',
    api_key: '',
    is_active: true
  });
  
  // Показать/скрыть ключ
  const showKey = ref(false);
  
  // Инициализация формы данными
  onMounted(() => {
    if (props.editingKey) {
      formData.value = {
        provider: props.editingKey.provider,
        name: props.editingKey.name || '',
        api_key: props.editingKey.api_key || '',
        is_active: props.editingKey.is_active !== false
      };
    } else if (props.selectedProvider) {
      formData.value.provider = props.selectedProvider;
    }
  });
  
  const closeModal = () => {
    emit('close');
  };
  
  const saveApiKey = () => {
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
    max-width: 500px;
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
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input[type="text"],
  input[type="password"],
  select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .api-key-input {
    display: flex;
    position: relative;
  }
  
  .api-key-input input {
    flex: 1;
    padding-right: 2.5rem;
  }
  
  .toggle-visibility-btn {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    color: #6b7280;
  }
  
  .help-text {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
  }
  
  .checkbox-group {
    display: flex;
    align-items: center;
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