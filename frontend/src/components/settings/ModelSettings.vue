<template>
  <div class="model-settings">
    <div>
      <h3 class="mb-4">Настройки моделей искусственного интеллекта</h3>
      
      <div class="row mb-5">
        <div class="col-lg-10 col-xl-8">
          <!-- Информационный блок -->
          <div class="alert alert-info mb-4">
            <p class="mb-0">
              <i class="bi bi-info-circle me-2"></i>
              Здесь вы можете настроить параметры моделей искусственного интеллекта и создать 
              собственные пресеты для различных задач.
            </p>
          </div>

          <!-- Кнопка создания пресета (без обертки в card) -->
          <div v-if="!showPreferenceForm" class="mb-5">
            <button 
              class="btn btn-primary" 
              @click="showPreferenceForm = true"
            >
              <i class="bi bi-plus-circle me-2"></i>
              Создать новый пресет
            </button>
          </div>

          <!-- Форма добавления нового пресета -->
          <div v-if="showPreferenceForm" class="card mb-5">
            <div class="card-header bg-light d-flex justify-content-between align-items-center">
              <h5 class="mb-0">{{ editingPreference ? 'Редактирование пресета' : 'Добавление нового пресета' }}</h5>
              <button 
                class="btn btn-sm btn-outline-secondary" 
                @click="cancelForm"
                title="Отменить"
              >
                <i class="bi bi-x"></i>
              </button>
            </div>
            <div class="card-body">
              <form @submit.prevent="saveModelPreference">
                <!-- Основная информация о пресете -->
                <div class="mb-4">
                  <h6 class="form-section-title">Основная информация</h6>
                  
                  <!-- Выбор API ключа -->
                  <div class="mb-4">
                    <label for="apiKeySelect" class="form-label">API ключ</label>
                    <select 
                      id="apiKeySelect" 
                      class="form-select"
                      v-model="preferenceForm.api_key_id"
                      required
                    >
                      <option value="">Выберите API ключ</option>
                      <option 
                        v-for="key in activeApiKeys" 
                        :key="key.id" 
                        :value="key.id"
                      >
                        {{ key.name || key.provider }} ({{ getProviderName(key.provider) }})
                      </option>
                    </select>
                    <div class="form-text" v-if="!activeApiKeys.length">
                      У вас нет активных API ключей. <router-link to="/settings/api-keys">Добавьте API ключ</router-link> для работы с моделями.
                    </div>
                  </div>

                  <!-- Название и описание в одной строке -->
                  <div class="row">
                    <!-- Ввод названия модели (текстовое поле) -->
                    <div class="col-md-6 mb-4">
                      <label for="modelInput" class="form-label">Название модели</label>
                      <input 
                        type="text" 
                        class="form-control" 
                        id="modelInput"
                        v-model="preferenceForm.model"
                        placeholder="Например: gpt-4o, claude-3-opus и т.д."
                        required
                      >
                      <div class="form-text">
                        Точное название модели AI
                      </div>
                    </div>

                    <!-- Описание пресета -->
                    <div class="col-md-6 mb-4">
                      <label for="description" class="form-label">Описание пресета</label>
                      <input 
                        type="text" 
                        class="form-control" 
                        id="description"
                        v-model="preferenceForm.description"
                        placeholder="Например: Для технических задач"
                        required
                      >
                      <div class="form-text">
                        Понятное название для вашего пресета
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Параметры генерации -->
                <div class="mb-4">
                  <h6 class="form-section-title">Параметры генерации</h6>
                  
                  <div class="row">
                    <!-- Максимальное количество токенов (текстовое поле) -->
                    <div class="col-md-6 mb-4">
                      <label for="maxTokens" class="form-label">Максимальное количество токенов</label>
                      <input 
                        type="number" 
                        class="form-control" 
                        id="maxTokens"
                        v-model="preferenceForm.max_tokens"
                        min="100"
                        max="100000"
                        placeholder="2000"
                      >
                      <div class="form-text">
                        Ограничение длины ответа (по умолчанию: 2000)
                      </div>
                    </div>

                    <!-- Температура -->
                    <div class="col-md-6 mb-4">
                      <label for="temperature" class="form-label">Температура</label>
                      <div class="d-flex align-items-center gap-2">
                        <input 
                          type="range" 
                          class="form-range flex-grow-1" 
                          id="temperature" 
                          min="0" 
                          max="1" 
                          step="0.1" 
                          v-model="preferenceForm.temperature"
                        >
                        <span class="text-muted">{{ preferenceForm.temperature }}</span>
                      </div>
                      <div class="d-flex justify-content-between small text-muted">
                        <span>Точный</span>
                        <span>Творческий</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Системный промпт -->
                  <div class="mb-4">
                    <label for="systemPrompt" class="form-label">Системный промпт (необязательно)</label>
                    <textarea 
                      id="systemPrompt" 
                      class="form-control" 
                      rows="3" 
                      v-model="preferenceForm.system_prompt"
                      placeholder="Опишите роль и поведение ассистента..."
                    ></textarea>
                    <div class="form-text">
                      Системный промпт задаёт поведение и тон модели при взаимодействии
                    </div>
                  </div>
                </div>

                <!-- Стоимость использования модели -->
                <div class="mb-4">
                  <h6 class="form-section-title">Стоимость использования</h6>
                  <div class="cost-container p-3 border rounded mb-2">
                    <div class="row g-3">
                      <div class="col-md-4">
                        <label for="inputCost" class="form-label d-flex align-items-center">
                          <span class="me-1">Input</span>
                          <i class="bi bi-info-circle text-muted" title="Стоимость входных токенов"></i>
                        </label>
                        <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input 
                            type="number" 
                            class="form-control" 
                            id="inputCost"
                            v-model="preferenceForm.input_cost"
                            min="0"
                            step="0.001"
                            placeholder="0.00"
                          >
                        </div>
                      </div>
                      
                      <div class="col-md-4">
                        <label for="outputCost" class="form-label d-flex align-items-center">
                          <span class="me-1">Output</span>
                          <i class="bi bi-info-circle text-muted" title="Стоимость выходных токенов"></i>
                        </label>
                        <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input 
                            type="number" 
                            class="form-control" 
                            id="outputCost"
                            v-model="preferenceForm.output_cost"
                            min="0"
                            step="0.001"
                            placeholder="0.00"
                          >
                        </div>
                      </div>
                      
                      <div class="col-md-4">
                        <label for="cachedInputCost" class="form-label d-flex align-items-center">
                          <span class="me-1">Cached input</span>
                          <i class="bi bi-info-circle text-muted" title="Стоимость кешированных токенов"></i>
                        </label>
                        <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input 
                            type="number" 
                            class="form-control" 
                            id="cachedInputCost"
                            v-model="preferenceForm.cached_input_cost"
                            min="0"
                            step="0.001"
                            placeholder="0.00"
                          >
                        </div>
                      </div>
                    </div>
                    <div class="form-text mt-2">
                      Указывайте стоимость токенов для более точного учета расходов
                    </div>
                  </div>
                </div>

                <!-- Дополнительные настройки -->
                <div class="mb-4">
                  <h6 class="form-section-title">Дополнительные настройки</h6>
                  
                  <!-- По умолчанию -->
                  <div class="form-check mb-3">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="isDefault" 
                      v-model="preferenceForm.is_default"
                    >
                    <label class="form-check-label" for="isDefault">
                      Использовать как пресет по умолчанию для этого провайдера
                    </label>
                  </div>
                </div>

                <!-- Кнопки отправки формы -->
                <div class="d-flex gap-2 mt-4">
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="isSubmitting || !isFormValid"
                  >
                    <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    {{ editingPreference ? 'Сохранить изменения' : 'Создать пресет' }}
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary"
                    @click="cancelForm"
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Список существующих пресетов -->
      <div class="row mt-5">
        <div class="col-lg-10 col-xl-8">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="mb-0">Ваши пресеты моделей</h5>
            
            <!-- Фильтр по провайдерам (выпадающий список) -->
            <div v-if="providers.length > 1" class="dropdown">
              <button 
                class="btn btn-outline-primary dropdown-toggle" 
                type="button" 
                id="providerFilterDropdown" 
                data-bs-toggle="dropdown" 
                aria-expanded="false"
              >
                {{ selectedProviderFilter ? `Фильтр: ${getProviderName(selectedProviderFilter)}` : 'Все провайдеры' }}
              </button>
              <ul class="dropdown-menu" aria-labelledby="providerFilterDropdown">
                <li>
                  <button 
                    class="dropdown-item" 
                    :class="{ 'active': selectedProviderFilter === '' }" 
                    @click="selectedProviderFilter = ''"
                  >
                    Все провайдеры
                  </button>
                </li>
                <li v-for="provider in providers" :key="provider">
                  <button 
                    class="dropdown-item" 
                    :class="{ 'active': selectedProviderFilter === provider }" 
                    @click="selectedProviderFilter = provider"
                  >
                    {{ getProviderName(provider) }}
                  </button>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Загрузка...</span>
            </div>
          </div>

          <div v-else-if="!filteredModelPreferences.length" class="alert alert-secondary">
            <p class="mb-0 text-center">
              <i class="bi bi-cpu" style="font-size: 1.5rem;"></i>
              <br>
              {{ selectedProviderFilter ? `У вас пока нет сохранённых пресетов моделей для ${getProviderName(selectedProviderFilter)}.` : 'У вас пока нет сохранённых пресетов моделей.' }} 
              Создайте пресет для более удобной работы с разными типами задач.
            </p>
          </div>

          <!-- Горизонтальные карточки пресетов -->
          <div v-else>
            <div 
              v-for="preference in filteredModelPreferences" 
              :key="preference.id"
              class="card mb-3"
            >
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center">
                      <div class="model-icon me-3" :style="{ 'background-color': getProviderColor(preference.provider) }">
                        <i class="bi" :class="getProviderIcon(preference.provider)"></i>
                      </div>
                      <div>
                        <h5 class="mb-1">
                          {{ preference.description }}
                        </h5>
                        <div class="text-muted">
                          <span class="me-3">{{ getProviderName(preference.provider) }}</span>
                          <span class="me-3"><strong>Модель:</strong> {{ preference.model }}</span>
                          <span class="me-3"><strong>Токены:</strong> {{ preference.max_tokens }}</span>
                          <span><strong>Температура:</strong> {{ preference.temperature }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="mt-3">
                      <div v-if="preference.system_prompt" class="mb-2">
                        <small class="text-muted d-block">Системный промпт:</small>
                        <p class="small mb-0 text-truncate-2">{{ preference.system_prompt }}</p>
                      </div>
                      <div class="d-flex flex-wrap text-muted small mt-2">
                        <div class="me-3 mb-1">
                          <strong>Использований:</strong> {{ preference.use_count || 0 }}
                        </div>
                        <div class="me-3 mb-1">
                          <strong>Последнее использование:</strong> {{ formatDate(preference.last_used_at) }}
                        </div>
                        <div v-if="preference.input_cost" class="mb-1">
                          <strong>Стоимость ($):</strong> 
                          <span title="Input / Output / Cached">
                            {{ preference.input_cost }} / {{ preference.output_cost }} / {{ preference.cached_input_cost }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="model-actions">
                    <button
                      class="btn btn-sm btn-outline-primary me-2"
                      @click="editPreference(preference)"
                      title="Редактировать"
                    >
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button
                      class="btn btn-sm"
                      :class="preference.is_default ? 'btn-success' : 'btn-outline-success'"
                      @click="setAsDefault(preference)"
                      :disabled="preference.is_default"
                      title="Установить по умолчанию"
                    >
                      <i class="bi bi-star-fill"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger ms-2"
                      @click="confirmDeletePreference(preference)"
                      title="Удалить"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div class="modal fade" id="deletePreferenceModal" tabindex="-1" aria-labelledby="deletePreferenceModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deletePreferenceModalLabel">Удаление пресета</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Вы уверены, что хотите удалить пресет "{{ selectedPreference?.description }}"?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="button" class="btn btn-danger" @click="deletePreference">Удалить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useModelStore } from '@/stores/modelStore';
import { useApiKeysStore } from '@/stores/apiKeys';

// Состояние компонента
const loading = ref(true);
const isSubmitting = ref(false);
const showPreferenceForm = ref(false);
const editingPreference = ref(null);
const selectedPreference = ref(null);
const modelPreferences = ref([]);
const selectedProviderFilter = ref('');
let deleteModal = null;

// Получаем хранилище моделей и API ключей
const modelStore = useModelStore();
const apiKeysStore = useApiKeysStore();

// Начальное состояние формы с дефолтными значениями
const defaultFormState = {
  api_key_id: '',
  model: '',
  description: '',
  max_tokens: '2000', // Значение по умолчанию
  temperature: 0.7,
  system_prompt: '',
  is_default: false,
  input_cost: '',
  output_cost: '',
  cached_input_cost: ''
};

// Форма для создания/редактирования пресета модели
const preferenceForm = ref({...defaultFormState});

// Вычисляемое свойство для получения активных API ключей
const activeApiKeys = computed(() => {
  return apiKeysStore.getAllKeys.filter(key => key.is_active);
});

// Вычисляемое свойство для определения провайдера на основе выбранного API ключа
const selectedProvider = computed(() => {
  if (!preferenceForm.value.api_key_id) return null;
  
  const apiKey = apiKeysStore.getAllKeys.find(key => key.id === preferenceForm.value.api_key_id);
  return apiKey ? apiKey.provider : null;
});

// Список уникальных провайдеров из имеющихся пресетов
const providers = computed(() => {
  const providerSet = new Set(modelPreferences.value.map(pref => pref.provider));
  return [...providerSet];
});

// Фильтрованный список пресетов
const filteredModelPreferences = computed(() => {
  if (!selectedProviderFilter.value) {
    return modelPreferences.value;
  }
  
  return modelPreferences.value.filter(pref => pref.provider === selectedProviderFilter.value);
});

// Вычисляемое свойство для валидации формы
const isFormValid = computed(() => {
  return preferenceForm.value.api_key_id && 
         preferenceForm.value.model && 
         preferenceForm.value.description;
});

// Монтирование компонента
onMounted(async () => {
  await Promise.all([
    fetchModelPreferences(),
    apiKeysStore.fetchApiKeys()
  ]);
  
  // Инициализация модального окна для удаления
  initDeleteModal();
});

// Инициализация модального окна
const initDeleteModal = () => {
  const modalEl = document.getElementById('deletePreferenceModal');
  if (modalEl && typeof bootstrap !== 'undefined') {
    deleteModal = new bootstrap.Modal(modalEl);
  }
};

// Получение списка пресетов моделей
const fetchModelPreferences = async () => {
  try {
    loading.value = true;
    await modelStore.fetchModelPreferences();
    modelPreferences.value = modelStore.getModelPreferences;
  } catch (error) {
    console.error('Ошибка при загрузке пресетов моделей:', error);
    showErrorMessage('Не удалось загрузить пресеты моделей');
  } finally {
    loading.value = false;
  }
};

// Обновляем функцию saveModelPreference для лучшей обработки ошибок
const saveModelPreference = async () => {
  try {
    isSubmitting.value = true;
    
    // Если выбран API ключ, получаем информацию о провайдере
    if (preferenceForm.value.api_key_id) {
      const apiKey = apiKeysStore.getAllKeys.find(key => key.id === preferenceForm.value.api_key_id);
      if (apiKey) {
        preferenceForm.value.provider = apiKey.provider;
      }
    }
    
    // Преобразование полей в нужные типы данных
    const preferenceData = {
      ...preferenceForm.value,
      max_tokens: parseInt(preferenceForm.value.max_tokens),
      temperature: parseFloat(preferenceForm.value.temperature),
      input_cost: preferenceForm.value.input_cost ? parseFloat(preferenceForm.value.input_cost) : null,
      output_cost: preferenceForm.value.output_cost ? parseFloat(preferenceForm.value.output_cost) : null,
      cached_input_cost: preferenceForm.value.cached_input_cost ? parseFloat(preferenceForm.value.cached_input_cost) : null
    };
    
    if (editingPreference.value) {
      // Обновление существующего пресета
      await modelStore.updateModelPreference(editingPreference.value.id, preferenceData);
      showSuccessMessage('Пресет успешно обновлен');
    } else {
      // Создание нового пресета
      await modelStore.createModelPreference(preferenceData);
      showSuccessMessage('Пресет успешно создан');
    }
    
    // Обновляем список пресетов
    await fetchModelPreferences();
    
    // Сбрасываем форму
    resetForm();
  } catch (error) {
    console.error('Ошибка при сохранении пресета модели:', error);
    
    // Улучшенная обработка ошибок - извлекаем детали ошибки из ответа
    let errorMessage = 'Ошибка при сохранении пресета модели';
    
    // Для API-ошибок, извлекаем детальное сообщение
    if (error.response) {
      // Проверяем различные форматы ошибок API
      if (error.response.data) {
        if (error.response.data.detail) {
          // Часто серверы возвращают ошибку в поле detail
          errorMessage = error.response.data.detail;
        } else if (error.response.data.error_message) {
          // Или в поле error_message
          errorMessage = error.response.data.error_message;
        } else if (typeof error.response.data === 'string') {
          // Иногда ошибка может быть просто строкой
          errorMessage = error.response.data;
        } else if (error.response.data.message) {
          // Или в поле message
          errorMessage = error.response.data.message;
        }
      } else if (error.response.status) {
        // Если нет данных в ответе, но есть статус код
        switch(error.response.status) {
          case 400:
            errorMessage = 'Некорректные данные формы';
            break;
          case 401:
            errorMessage = 'Требуется авторизация';
            break;
          case 403:
            errorMessage = 'Доступ запрещен';
            break;
          case 404:
            errorMessage = 'Ресурс не найден';
            break;
          case 409:
            errorMessage = 'Конфликт данных';
            break;
          case 422:
            errorMessage = 'Ошибка валидации данных';
            break;
          case 500:
            errorMessage = 'Внутренняя ошибка сервера';
            break;
          default:
            errorMessage = `Ошибка сервера (${error.response.status})`;
        }
      }
    } else if (error.message) {
      // Если это ошибка JS, а не ответ API
      errorMessage = error.message;
    }
    
    // Показываем пользователю сообщение об ошибке
    showErrorMessage(errorMessage);
  } finally {
    isSubmitting.value = false;
  }
};

// Редактирование пресета
const editPreference = (preference) => {
  editingPreference.value = preference;
  
  // Заполняем форму данными выбранного пресета
  preferenceForm.value = {
    api_key_id: preference.api_key_id,
    model: preference.model,
    description: preference.description,
    max_tokens: preference.max_tokens.toString(),
    temperature: preference.temperature,
    system_prompt: preference.system_prompt || '',
    is_default: preference.is_default,
    input_cost: preference.input_cost !== null ? preference.input_cost.toString() : '',
    output_cost: preference.output_cost !== null ? preference.output_cost.toString() : '',
    cached_input_cost: preference.cached_input_cost !== null ? preference.cached_input_cost.toString() : ''
  };
  
  showPreferenceForm.value = true;
};

// Установка пресета по умолчанию
const setAsDefault = async (preference) => {
  try {
    loading.value = true;
    
    await modelStore.updateModelPreference(preference.id, {
      ...preference,
      is_default: true
    });
    
    // Обновляем список пресетов
    await fetchModelPreferences();
    
    showSuccessMessage(`Пресет "${preference.description}" установлен по умолчанию`);
  } catch (error) {
    console.error('Ошибка при установке пресета по умолчанию:', error);
    
    // Извлекаем детали ошибки из ответа
    let errorMessage = 'Ошибка при установке пресета по умолчанию';
    
    if (error.response && error.response.data) {
      if (error.response.data.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response.data.error_message) {
        errorMessage = error.response.data.error_message;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    showErrorMessage(errorMessage);
  } finally {
    loading.value = false;
  }
};

// Открытие модального окна для подтверждения удаления
const confirmDeletePreference = (preference) => {
  selectedPreference.value = preference;
  
  if (deleteModal) {
    deleteModal.show();
  } else {
    // Резервное подтверждение, если модальное окно не инициализировано
    if (confirm(`Вы уверены, что хотите удалить пресет "${preference.description}"?`)) {
      deletePreference();
    }
  }
};

// Удаление пресета
const deletePreference = async () => {
  if (!selectedPreference.value) return;
  
  try {
    loading.value = true;
    
    // Закрываем модальное окно
    if (deleteModal) {
      deleteModal.hide();
    }
    
    await modelStore.deleteModelPreference(selectedPreference.value.id);
    
    // Обновляем список пресетов
    await fetchModelPreferences();
    
    showSuccessMessage(`Пресет "${selectedPreference.value.description}" удален`);
  } catch (error) {
    console.error('Ошибка при удалении пресета:', error);
    
    // Извлекаем детали ошибки из ответа
    let errorMessage = 'Ошибка при удалении пресета';
    
    if (error.response && error.response.data) {
      if (error.response.data.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response.data.error_message) {
        errorMessage = error.response.data.error_message;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    showErrorMessage(errorMessage);
  } finally {
    loading.value = false;
    selectedPreference.value = null;
  }
};

// Отмена формы и сброс состояния
const cancelForm = () => {
  resetForm();
};

// Сброс формы
const resetForm = () => {
  preferenceForm.value = {...defaultFormState};
  editingPreference.value = null;
  showPreferenceForm.value = false;
};

// Вспомогательные функции

// Получение имени провайдера
const getProviderName = (providerId) => {
  const providers = {
    'openai': 'OpenAI (ChatGPT)',
    'anthropic': 'Anthropic (Claude)'
  };
  
  return providers[providerId] || providerId;
};

// Получение цвета для провайдера
const getProviderColor = (providerId) => {
  const colors = {
    'openai': '#10a37f', // Зеленый для OpenAI
    'anthropic': '#6b48ff'  // Фиолетовый для Anthropic
  };
  
  return colors[providerId] || '#6c757d'; // Серый по умолчанию
};

// Получение иконки для провайдера
const getProviderIcon = (providerId) => {
  const icons = {
    'openai': 'bi-stars',
    'anthropic': 'bi-robot'
  };
  
  return icons[providerId] || 'bi-cpu';
};

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return 'Не использовался';
  
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

// Уведомления (можно заменить на компонент уведомлений)
const showSuccessMessage = (message) => {
  alert(message); // В реальном приложении можно заменить на компонент уведомлений
};

const showErrorMessage = (message) => {
  alert(`Ошибка: ${message}`); // В реальном приложении можно заменить на компонент уведомлений
};

// Отслеживаем изменения выбранного API ключа
watch(() => preferenceForm.value.api_key_id, (newValue) => {
  if (newValue) {
    const apiKey = apiKeysStore.getAllKeys.find(key => key.id === newValue);
    if (apiKey) {
      // Можно предложить пользователю подходящую модель, но не устанавливать автоматически
      // В данном случае ничего не делаем, так как решено использовать текстовое поле
    }
  }
});
</script>

<style scoped>
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 3em;
}

/* Улучшенный стиль для range слайдера */
.form-range::-webkit-slider-thumb {
  background: #4361ee;
}
.form-range::-moz-range-thumb {
  background: #4361ee;
}
.form-range::-ms-thumb {
  background: #4361ee;
}

/* Стили для карточек моделей */
.card {
  border-radius: 0.5rem;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.badge.bg-primary {
  background-color: #4361ee !important;
}

/* Стили для иконок провайдеров */
.model-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.model-actions {
  display: flex;
  align-items: center;
  margin-left: 10px;
}

/* Стили для выпадающего списка фильтрации */
.dropdown-item.active {
  background-color: #4361ee;
}

/* Стили для групп полей формы */
.form-section-title {
  color: #4361ee;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

/* Стили для контейнера с полями стоимости */
.cost-container {
  background-color: #f8f9fa;
  border-color: #e9ecef !important;
}

/* Улучшения для мобильных устройств */
@media (max-width: 768px) {
  .model-actions {
    margin-top: 10px;
  }
}
</style>