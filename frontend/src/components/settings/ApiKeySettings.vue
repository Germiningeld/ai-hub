<template>
  <div class="api-key-settings">
    <!-- Статический заголовок -->
    <div class="api-key-header col-lg-10 col-xl-8">
      <h3 class="mb-4">Управление API ключами</h3>
      
      <!-- Описание и инструкции -->
      <div class="alert alert-info mb-4">
        <p class="mb-0">
          <i class="bi bi-info-circle me-2"></i>
          Для использования различных ИИ-моделей необходимо добавить соответствующие API ключи. 
          Ваши ключи хранятся в зашифрованном виде и используются только для запросов к выбранным API.
        </p>
      </div>
      
      <!-- Кнопка для отображения формы добавления ключа -->
      <div v-if="!showAddKeyForm" class="mb-4">
        <button 
          class="btn btn-primary" 
          @click="showAddKeyForm = true"
        >
          <i class="bi bi-plus-circle me-2"></i>
          Добавить новый API ключ
        </button>
      </div>
      
      <!-- Форма добавления ключа -->
      <div v-if="showAddKeyForm" class="card mb-4">
        <div class="card-header bg-light d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Добавить новый API ключ</h5>
          <button 
            class="btn btn-sm btn-outline-secondary" 
            @click="showAddKeyForm = false"
            title="Закрыть форму"
          >
            <i class="bi bi-x"></i>
          </button>
        </div>
        <div class="card-body">
          <form @submit.prevent="addApiKey">
            <div class="mb-3">
              <label for="keyProvider" class="form-label">Провайдер</label>
              <select 
                id="keyProvider" 
                name="provider"
                class="form-select" 
                v-model="newKey.provider"
                required
              >
                <option value="" disabled>Выберите провайдера</option>
                <option 
                  v-for="provider in availableProviders" 
                  :key="provider.id" 
                  :value="provider.id"
                >
                  {{ provider.name }}
                </option>
              </select>
              <div class="form-text" v-if="newKey.provider">
                {{ getProviderDescription(newKey.provider) }}
              </div>
            </div>
            
            <div class="mb-3">
              <label for="keyName" class="form-label">Название (опционально)</label>
              <input 
                type="text" 
                class="form-control" 
                id="keyName" 
                name="keyName"
                v-model="newKey.name" 
                placeholder="Например: Рабочий ключ OpenAI"
              >
            </div>
            
            <div class="mb-3">
              <label for="apiKey" class="form-label">API ключ</label>
              <input 
                type="text" 
                class="form-control" 
                id="apiKey" 
                name="api_key"
                v-model="newKey.api_key" 
                placeholder="Введите ваш API ключ"
                required
              >
              <div class="form-text">
                <a :href="getProviderKeyUrl(newKey.provider)" target="_blank" rel="noopener noreferrer">
                  Где получить API ключ?
                </a>
              </div>
            </div>
            
            <div class="form-check mb-3">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="keyActive" 
                name="is_active"
                v-model="newKey.is_active"
              >
              <label class="form-check-label" for="keyActive">
                Активировать ключ
              </label>
            </div>
            
            <div class="d-flex gap-2">
              <button 
                type="submit" 
                class="btn btn-primary" 
                :disabled="apiKeysStore.isLoading || !isFormValid"
              >
                <span v-if="apiKeysStore.isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                {{ apiKeysStore.isLoading ? 'Добавление...' : 'Добавить API ключ' }}
              </button>
              <button 
                type="button" 
                class="btn btn-outline-secondary" 
                @click="showAddKeyForm = false"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Прокручиваемый контейнер для списка ключей -->
    <div class="api-keys-container col-lg-10 col-xl-8">
      <div class="api-keys-list-scroll" ref="keysContainer">
        <!-- Заголовок списка ключей -->
        <h5 class="mb-3">Добавленные ключи</h5>
        
        <div v-if="apiKeysStore.isLoading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
        </div>
        
        <div v-else-if="apiKeys.length === 0" class="alert alert-secondary">
          <p class="mb-0 text-center">
            <i class="bi bi-key" style="font-size: 1.5rem;"></i>
            <br>
            У вас пока нет добавленных API ключей. Добавьте ключ для начала работы.
          </p>
        </div>
        
        <div v-else class="api-key-list">
          <!-- Обновление в карточке API ключа -->
          <div 
            v-for="key in apiKeys" 
            :key="key.id" 
            class="api-key-item card mb-3"
          >
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-1">{{ getProviderName(key.provider) }}</h6>
                  <p class="text-muted mb-0">
                    {{ key.name || 'Ключ без названия' }}
                    <span class="badge bg-light text-secondary ms-2">{{ key.provider_code }}</span>
                  </p>
                </div>
                <div class="key-actions">
                  <div class="form-check form-switch me-2 d-inline-block">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      :id="`key-active-${key.id}`" 
                      v-model="key.is_active"
                      @change="toggleKeyStatus(key.id, key.is_active)"
                    >
                    <label class="form-check-label" :for="`key-active-${key.id}`">
                      {{ key.is_active ? 'Активен' : 'Неактивен' }}
                    </label>
                  </div>
                  <button 
                    class="btn btn-sm btn-outline-danger" 
                    @click="confirmDeleteKey(key)"
                    title="Удалить ключ"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
              
              <div class="mt-2">
                <span class="api-key-value text-monospace">{{ key.api_key }}</span>
              </div>
              
              <div class="mt-2 small text-muted">
                <span>Добавлен: {{ formatDate(key.created_at) }}</span>
                <span v-if="key.updated_at !== key.created_at"> · Обновлен: {{ formatDate(key.updated_at) }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
    
    <!-- Модальное окно подтверждения удаления -->
    <div class="modal fade" id="deleteKeyModal" tabindex="-1" aria-labelledby="deleteKeyModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteKeyModalLabel">Удаление API ключа</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Вы уверены, что хотите удалить API ключ для {{ selectedKey ? getProviderName(selectedKey.provider) : '' }}?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteKey"
              data-bs-dismiss="modal"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import { useApiKeysStore } from '@/stores/apiKeys';
import { setupAutoHideScrollbar } from '@/utils/scrollbarUtil';

// Подключаем store для работы с API ключами
const apiKeysStore = useApiKeysStore();

// Ссылка на контейнер со списком ключей для скроллбара
const keysContainer = ref(null);

// Состояние компонента
const apiKeys = ref([]);
const newKey = ref({
  provider: '',
  name: '',
  api_key: '',
  is_active: true
});
const selectedKey = ref(null);
const showAddKeyForm = ref(false);
let deleteModal = null;

// Получаем список доступных провайдеров
const availableProviders = apiKeysStore.getAvailableProviders();

// Вычисляем валидность формы
const isFormValid = computed(() => {
  return newKey.value.provider && newKey.value.api_key;
});

// При монтировании компонента загружаем ключи и настраиваем скроллбар
onMounted(async () => {
  await fetchApiKeys();
  
  // Инициализируем скроллбар после загрузки данных
  nextTick(() => {
    if (keysContainer.value) {
      setupAutoHideScrollbar(keysContainer.value);
    }
    
    // Инициализируем модальное окно для удаления
    const modalEl = document.getElementById('deleteKeyModal');
    if (modalEl && typeof bootstrap !== 'undefined') {
      deleteModal = new bootstrap.Modal(modalEl);
    }
  });
});

// Загрузка API ключей
const fetchApiKeys = async () => {
  try {
    await apiKeysStore.fetchApiKeys();
    apiKeys.value = apiKeysStore.getAllKeys;
  } catch (error) {
    console.error('Ошибка при загрузке API ключей:', error);
  }
};

// Добавление нового API ключа
const addApiKey = async () => {
  try {
    // Проверяем, что форма заполнена корректно
    if (!isFormValid.value) return;
    
    await apiKeysStore.createApiKey(newKey.value);
    
    // Обновляем список ключей
    apiKeys.value = apiKeysStore.getAllKeys;
    
    // Очищаем форму
    newKey.value = {
      provider: '',
      name: '',
      api_key: '',
      is_active: true
    };
    
    // Скрываем форму после успешного добавления
    showAddKeyForm.value = false;
    
    // Показываем уведомление об успехе
    showSuccessMessage('API ключ успешно добавлен');
    
  } catch (error) {
    showErrorMessage('Ошибка при добавлении API ключа: ' + (error.message || 'Неизвестная ошибка'));
  }
};

// Переключение статуса активности ключа
const toggleKeyStatus = async (keyId, isActive) => {
  try {
    await apiKeysStore.toggleKeyStatus(keyId, isActive);
    
    // Обновляем список ключей
    apiKeys.value = apiKeysStore.getAllKeys;
    
    // Показываем уведомление об успехе
    showSuccessMessage(`API ключ ${isActive ? 'активирован' : 'деактивирован'}`);
    
  } catch (error) {
    showErrorMessage('Ошибка при изменении статуса ключа: ' + (error.message || 'Неизвестная ошибка'));
  }
};

// Открытие модального окна подтверждения удаления
const confirmDeleteKey = (key) => {
  selectedKey.value = key;
  
  // Показываем модальное окно
  if (deleteModal) {
    deleteModal.show();
  } else {
    // Если bootstrap модальное окно не инициализировано, используем простое подтверждение
    if (confirm(`Вы уверены, что хотите удалить API ключ для ${getProviderName(key.provider)}?`)) {
      deleteKey();
    }
  }
};

// Удаление API ключа
const deleteKey = async () => {
  if (!selectedKey.value) return;
  
  try {
    await apiKeysStore.deleteApiKey(selectedKey.value.id);
    
    // Обновляем список ключей
    apiKeys.value = apiKeysStore.getAllKeys;
    
    // Показываем уведомление об успехе
    showSuccessMessage('API ключ успешно удален');
    
  } catch (error) {
    showErrorMessage('Ошибка при удалении API ключа: ' + (error.message || 'Неизвестная ошибка'));
  } finally {
    selectedKey.value = null;
  }
};

// Получение названия провайдера по ID
const getProviderName = (providerId) => {
  const provider = availableProviders.find(p => p.id === providerId);
  return provider ? provider.name : providerId;
};

// Получение описания провайдера по ID
const getProviderDescription = (providerId) => {
  const provider = availableProviders.find(p => p.id === providerId);
  return provider ? provider.description : '';
};

// URL для получения API ключа провайдера
const getProviderKeyUrl = (providerId) => {
  const urls = {
    'openai': 'https://platform.openai.com/api-keys',
    'anthropic': 'https://console.anthropic.com/keys'
  };
  
  return urls[providerId] || '#';
};

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

// Упрощенные функции для уведомлений (можно заменить на более сложные)
const showSuccessMessage = (message) => {
  alert(message); // В реальном приложении здесь будет компонент уведомлений
};

const showErrorMessage = (message) => {
  alert(message); // В реальном приложении здесь будет компонент уведомлений
};
</script>

<style scoped>
.api-key-item:hover {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.api-key-value {
  background-color: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.key-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Улучшенный стиль для переключателя */
.form-check-input:checked {
  background-color: #4361ee;
  border-color: #4361ee;
}
</style>