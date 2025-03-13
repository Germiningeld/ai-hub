<template>
    <div class="model-preference-form">
      <div v-if="preferences.length === 0" class="empty-state">
        <p>У вас пока нет настроенных моделей для этого провайдера.</p>
        <button @click="addNewPreference" class="add-preference-btn">
          Добавить настройку модели
        </button>
      </div>
      
      <div v-else class="preferences-list">
        <div v-for="preference in preferences" :key="preference.id" class="preference-card">
          <div class="preference-header">
            <div class="preference-title">
              <h4>{{ getModelName(preference.model) }}</h4>
              <span v-if="preference.is_default" class="default-badge">По умолчанию</span>
            </div>
            
            <div class="preference-actions">
              <button 
                v-if="!preference.is_default" 
                @click="setDefault(preference.id)" 
                class="action-btn"
                title="Сделать моделью по умолчанию"
              >
                🌟
              </button>
              <button 
                @click="editPreference(preference)" 
                class="action-btn"
                title="Редактировать"
              >
                ✏️
              </button>
              <button 
                @click="confirmDeletePreference(preference.id)" 
                class="action-btn delete-btn"
                title="Удалить"
              >
                🗑️
              </button>
            </div>
          </div>
          
          <div class="preference-details">
            <div class="preference-detail">
              <span class="detail-label">Максимум токенов:</span>
              <span class="detail-value">{{ preference.max_tokens }}</span>
            </div>
            
            <div class="preference-detail">
              <span class="detail-label">Температура:</span>
              <span class="detail-value">{{ preference.temperature }}</span>
            </div>
            
            <div class="preference-detail" v-if="preference.system_prompt">
              <span class="detail-label">Системный промпт:</span>
              <div class="system-prompt">{{ preference.system_prompt }}</div>
            </div>
          </div>
        </div>
        
        <button @click="addNewPreference" class="add-preference-btn">
          Добавить настройку модели
        </button>
      </div>
      
      <!-- Модальное окно для добавления/редактирования модели -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">
              {{ editing ? 'Редактировать настройку модели' : 'Добавить настройку модели' }}
            </h2>
            <button @click="closeModal" class="close-btn">×</button>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="savePreference">
              <div class="form-group">
                <label for="model">Модель</label>
                <select 
                  id="model" 
                  v-model="formData.model" 
                  required
                  :disabled="editing"
                >
                  <option value="">Выберите модель</option>
                  <option 
                    v-for="model in availableModels" 
                    :key="model.id" 
                    :value="model.id"
                  >
                    {{ model.name }}
                  </option>
                </select>
                
                <p v-if="selectedModelInfo" class="model-info">
                  {{ selectedModelInfo.description }}
                </p>
              </div>
              
              <div class="form-group">
                <label for="max-tokens">Максимум токенов</label>
                <input 
                  type="number" 
                  id="max-tokens" 
                  v-model.number="formData.max_tokens" 
                  min="1" 
                  max="100000" 
                  required
                />
                <p class="help-text">
                  Максимальное количество токенов, которое может сгенерировать модель за один запрос.
                </p>
              </div>
              
              <div class="form-group">
                <label for="temperature">Температура</label>
                <input 
                  type="range" 
                  id="temperature" 
                  v-model.number="formData.temperature" 
                  min="0" 
                  max="2" 
                  step="0.1"
                />
                <div class="range-value">{{ formData.temperature }}</div>
                <p class="help-text">
                  Контролирует случайность генерации. Более низкие значения делают ответы более детерминированными, более высокие — более творческими.
                </p>
              </div>
              
              <div class="form-group">
                <label for="system-prompt">Системный промпт (опционально)</label>
                <textarea 
                  id="system-prompt" 
                  v-model="formData.system_prompt" 
                  rows="4"
                  placeholder="Например: Ты опытный программист, специализирующийся на Python и JavaScript"
                ></textarea>
                <p class="help-text">
                  Задаёт основной контекст и роль для модели. Оставьте пустым для использования стандартного промпта.
                </p>
              </div>
              
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.is_default" />
                  <span>Использовать по умолчанию для {{ provider }}</span>
                </label>
              </div>
              
              <div class="form-actions">
                <button type="button" @click="closeModal" class="cancel-btn">Отмена</button>
                <button type="submit" class="save-btn">{{ editing ? 'Сохранить' : 'Добавить' }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  
  const props = defineProps({
    provider: {
      type: String,
      required: true
    },
    availableModels: {
      type: Array,
      default: () => []
    },
    preferences: {
      type: Array,
      default: () => []
    }
  });
  
  const emit = defineEmits(['save', 'delete', 'set-default']);
  
  const showModal = ref(false);
  const editing = ref(false);
  const formData = ref({
    provider: props.provider,
    model: '',
    max_tokens: 2000,
    temperature: 0.7,
    system_prompt: '',
    is_default: false
  });
  
  const selectedModelInfo = computed(() => {
    if (!formData.value.model) return null;
    return props.availableModels.find(model => model.id === formData.value.model);
  });
  
  const getModelName = (modelId) => {
    const model = props.availableModels.find(m => m.id === modelId);
    return model ? model.name : modelId;
  };
  
  const addNewPreference = () => {
    editing.value = false;
    formData.value = {
      provider: props.provider,
      model: '',
      max_tokens: 2000,
      temperature: 0.7,
      system_prompt: '',
      is_default: false
    };
    showModal.value = true;
  };
  
  const editPreference = (preference) => {
    editing.value = true;
    formData.value = { ...preference };
    showModal.value = true;
  };
  
  const closeModal = () => {
    showModal.value = false;
  };
  
  const savePreference = () => {
    emit('save', { ...formData.value });
    closeModal();
  };
  
  const confirmDeletePreference = (preferenceId) => {
    if (confirm('Вы уверены, что хотите удалить эту настройку модели?')) {
      emit('delete', preferenceId);
    }
  };
  
  const setDefault = (preferenceId) => {
    emit('set-default', preferenceId);
  };
  </script>
  
  <style scoped>
  .model-preference-form {
    margin-bottom: 2rem;
  }
  
  .empty-state {
    text-align: center;
    padding: 2rem;
    background-color: var(--background-color);
    border: 1px dashed var(--border-color);
    border-radius: 0.5rem;
    color: #6b7280;
  }
  
  .preferences-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .preference-card {
    padding: 1.25rem;
    background-color: var(--background-color);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
  }
  
  .preference-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }
  
  .preference-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .preference-title h4 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
  }
  
  .default-badge {
    padding: 0.25rem 0.5rem;
    background-color: rgba(16, 185, 129, 0.1);
    color: #065f46;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .preference-actions {
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
    cursor: pointer;
  }
  
  .action-btn:hover {
    opacity: 1;
  }
  
  .delete-btn:hover {
    color: #ef4444;
  }
  
  .preference-details {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .preference-detail {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .detail-label {
    min-width: 140px;
    font-weight: 500;
    color: #6b7280;
  }
  
  .system-prompt {
    flex: 1;
    padding: 0.75rem;
    background-color: rgba(0, 0, 0, 0.03);
    border-radius: 0.25rem;
    font-size: 0.875rem;
    white-space: pre-line;
    max-height: 100px;
    overflow-y: auto;
  }
  
  .add-preference-btn {
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background-color: rgba(59, 130, 246, 0.1);
    color: var(--primary-color);
    border: 1px dashed var(--primary-color);
    border-radius: 0.5rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
    text-align: center;
  }
  
  .add-preference-btn:hover {
    background-color: rgba(59, 130, 246, 0.2);
  }
  
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
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input[type="text"],
  input[type="number"],
  select,
  textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  input[type="range"] {
    width: calc(100% - 40px);
    margin-right: 0.5rem;
  }
  
  .range-value {
    display: inline-block;
    width: 30px;
    text-align: center;
  }
  
  .model-info {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
    font-style: italic;
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
    cursor: pointer;
  }
  
  .save-btn {
    padding: 0.75rem 1.5rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    font-weight: 500;
    cursor: pointer;
  }
  </style>