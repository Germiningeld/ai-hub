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
              Здесь вы можете активировать модели и настроить их параметры для различных задач.
            </p>
          </div>

          <!-- Фильтры моделей -->
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="mb-0">Доступные модели</h5>

            <!-- Фильтр по провайдерам -->
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
                <li v-for="provider in providers" :key="provider.id">
                  <button
                    class="dropdown-item"
                    :class="{ 'active': selectedProviderFilter === provider.code }"
                    @click="selectedProviderFilter = provider.code"
                  >
                    {{ getProviderName(provider.code) }}
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Список провайдеров и их моделей -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>

      <div v-else>
        <div v-for="provider in filteredProviders" :key="provider.id" class="row mb-5">
          <div class="col-lg-10 col-xl-8">
            <div class="card">
              <div class="card-header bg-light">
              <h5 class="mb-0 d-flex align-items-center">
                <div class="provider-icon me-2" :style="{ 'background-color': getProviderColor(provider.code) }">
                  <i class="bi" :class="getProviderIcon(provider.code)"></i>
                </div>
                {{ getProviderName(provider.code) }}
              </h5>
            </div>

            <div class="card-body">
              <!-- Проверка наличия API ключа -->
              <div v-if="!hasApiKeyForProvider(provider.id)" class="alert alert-warning mb-3">
                <p class="mb-0">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  Для работы с этим провайдером необходимо
                  <router-link to="/settings/api-keys">добавить API ключ</router-link>.
                </p>
              </div>

              <!-- Список моделей провайдера -->
              <div v-for="model in provider.models" :key="model.id" class="model-card mb-3">
                <div :class="['card', isModelActive(model.id) ? 'border-primary' : 'border-light']">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                      <div class="flex-grow-1">
                        <div class="">{{ model.name }}</div>

                        <div v-if="isModelActive(model.id) && !expandedModels.includes(model.id)" class="mt-2 pt-2 border-top">
                        <div class="row ">
                          <div class="col-md-6 mb-1">
                            <span class="text-muted me-1">Максимум токенов:</span>
                            <strong>{{ modelSettingsMap[model.id]?.max_tokens }}</strong>
                          </div>
                          <div class="col-md-6 mb-1">
                            <span class="text-muted me-1">Температура:</span>
                            <strong>{{ modelSettingsMap[model.id]?.temperature }}</strong>
                          </div>
                        </div>
                        <!--
                        <div v-if="modelSettingsMap[model.id]?.system_prompt" class="mb-1">
                          <span class="text-muted me-1">Системный промпт:</span>
                          <span class="small">{{ truncateText(modelSettingsMap[model.id]?.system_prompt, 100) }}</span>
                        </div>
                        -->
                      </div>

                      </div>

                      <div class="model-actions">
  <!-- Переключатель активации модели -->
  <div class="form-check form-switch d-inline-block me-2">
    <input
      class="form-check-input"
      type="checkbox"
      :id="`model-${model.id}-toggle`"
      :checked="isModelActive(model.id)"
      @change="toggleModelActivation(model, provider)"
      :disabled="!hasApiKeyForProvider(provider.id)"
    >
    <label class="form-check-label" :for="`model-${model.id}-toggle`">
      {{ isModelActive(model.id) ? 'Активна' : 'Неактивна' }}
    </label>
  </div>

  <!-- Кнопка установки модели по умолчанию -->
  <button
    v-if="isModelActive(model.id)"
    :class="['btn btn-sm me-2', isModelDefault(model.id) ? 'btn-warning' : 'btn-outline-warning']"
    @click="toggleDefaultModel(model.id, provider.id)"
    title="Установить по умолчанию"
  >
    <i class="bi bi-star-fill"></i>
  </button>

  <!-- Кнопка настройки активной модели -->
  <button
    v-if="isModelActive(model.id)"
    class="btn btn-sm btn-outline-primary"
    @click="toggleModelSettings(model.id)"
    title="Настроить модель"
  >
    <i class="bi bi-gear"></i>
  </button>
</div>
                    </div>

                    <!-- Настройки модели (развернутая панель) -->
                    <div v-if="isModelActive(model.id) && expandedModels.includes(model.id)" class="model-settings-panel mt-3 pt-3 border-top">
                      <form @submit.prevent="saveModelSettings(model.id)">
                        <div class="row">
                          <!-- Максимум токенов -->
                          <div class="col-md-6 mb-3">
                            <label :for="`model-${model.id}-max-tokens`" class="form-label">Максимум токенов</label>
                            <input
                              type="number"
                              class="form-control"
                              :id="`model-${model.id}-max-tokens`"
                              v-model="modelSettingsMap[model.id].max_tokens"
                              min="100"
                              max="100000"
                              required
                            >
                            <div class="form-text">
                              Максимальное количество токенов для ответа
                            </div>
                          </div>

                          <!-- Температура -->
                          <div class="col-md-6 mb-3">
                            <label :for="`model-${model.id}-temperature`" class="form-label">Температура</label>
                            <div class="d-flex align-items-center gap-2">
                              <input
                                type="range"
                                class="form-range flex-grow-1"
                                :id="`model-${model.id}-temperature`"
                                min="0"
                                max="1"
                                step="0.1"
                                v-model="modelSettingsMap[model.id].temperature"
                              >
                              <span class="text-muted">{{ modelSettingsMap[model.id].temperature }}</span>
                            </div>
                            <div class="d-flex justify-content-between small text-muted">
                              <span>Точный</span>
                              <span>Творческий</span>
                            </div>
                          </div>
                        </div>

                        <!-- Системный промпт -->
                         <!--
                        <div class="mb-3">
                          <label :for="`model-${model.id}-system-prompt`" class="form-label">Системный промпт (необязательно)</label>
                          <textarea
                            :id="`model-${model.id}-system-prompt`"
                            class="form-control"
                            rows="3"
                            v-model="modelSettingsMap[model.id].system_prompt"
                            placeholder="Опишите роль и поведение ассистента..."
                          ></textarea>
                          <div class="form-text">
                            Системный промпт задаёт поведение и тон модели при взаимодействии
                          </div>
                        </div>
                      -->

                        <!-- Модель по умолчанию -->
                        <div class="form-check mb-3">
                          <input
                            class="form-check-input"
                            type="checkbox"
                            :id="`model-${model.id}-default`"
                            v-model="modelSettingsMap[model.id].is_default"
                          >
                          <label class="form-check-label" :for="`model-${model.id}-default`">
                            Использовать как модель по умолчанию для {{ getProviderName(provider.code) }}
                          </label>
                        </div>

                        <!-- Кнопки действий -->
                        <div class="d-flex gap-2">
                          <button type="submit" class="btn btn-primary">Сохранить настройки</button>
                          <button
                            type="button"
                            class="btn btn-outline-danger"
                            @click="confirmDeactivateModel(model.id)"
                          >
                            Деактивировать модель
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения деактивации -->
    <div class="modal fade" id="deactivateModelModal" tabindex="-1" aria-labelledby="deactivateModelModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deactivateModelModalLabel">Деактивация модели</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Вы уверены, что хотите деактивировать эту модель? Все ее настройки будут удалены.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="button" class="btn btn-danger" @click="deactivateModel">Деактивировать</button>
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
const providers = ref([]);
const selectedProviderFilter = ref('');
const expandedModels = ref([]);
const modelSettingsMap = ref({});
const selectedModelToDeactivate = ref(null);
let deactivateModal = null;

// Получаем хранилища
const modelStore = useModelStore();
const apiKeysStore = useApiKeysStore();

// Фильтрованные провайдеры
const filteredProviders = computed(() => {
  if (!selectedProviderFilter.value) {
    return providers.value;
  }

  return providers.value.filter(provider => provider.code === selectedProviderFilter.value);
});

// Монтирование компонента
onMounted(async () => {
  try {
    loading.value = true;
    await Promise.all([
      fetchProviders(),
      apiKeysStore.fetchApiKeys()
    ]);

    // Инициализация модального окна
    initDeactivateModal();
  } finally {
    loading.value = false;
  }
});

// Инициализация модального окна
const initDeactivateModal = () => {
  const modalEl = document.getElementById('deactivateModelModal');
  if (modalEl && typeof bootstrap !== 'undefined') {
    deactivateModal = new bootstrap.Modal(modalEl);
  }
};


// Функция для усечения длинного текста
const truncateText = (text, maxLength) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Переключение статуса модели по умолчанию
const toggleDefaultModel = async (modelId, providerId) => {
  try {
    loading.value = true;
    
    // Находим настройки модели
    const preference = modelStore.modelPreferences.find(pref => 
      pref.model_id === modelId
    );
    
    if (!preference) {
      showErrorMessage('Не найдены настройки модели');
      return;
    }
    
    // Если модель уже по умолчанию, ничего не делаем
    if (preference.is_default) {
      return;
    }
    
    // Находим все модели этого провайдера
    const providerModels = modelStore.modelPreferences.filter(pref =>
      pref.provider_id === providerId
    );
    
    // Снимаем статус "по умолчанию" с других моделей
    for (const pref of providerModels) {
      if (pref.is_default && pref.id !== preference.id) {
        await modelStore.updateModelPreference(pref.id, {
          ...pref,
          is_default: false
        });
        
        // Обновляем состояние в карте настроек
        if (modelSettingsMap.value[pref.model_id]) {
          modelSettingsMap.value[pref.model_id].is_default = false;
        }
      }
    }
    
    // Устанавливаем текущую модель по умолчанию
    await modelStore.updateModelPreference(preference.id, {
      ...preference,
      is_default: true
    });
    
    // Обновляем состояние в карте настроек
    if (modelSettingsMap.value[modelId]) {
      modelSettingsMap.value[modelId].is_default = true;
    }
    
    showSuccessMessage(`Модель ${modelStore.availableModels.find(m => m.id === modelId)?.name || modelId} установлена по умолчанию`);
  } catch (error) {
    console.error('Ошибка при установке модели по умолчанию:', error);
    showErrorMessage('Не удалось установить модель по умолчанию');
  } finally {
    loading.value = false;
  }
};


// Получение списка провайдеров с моделями
const fetchProviders = async () => {
  try {
    // Получаем список провайдеров с моделями
    await modelStore.fetchAvailableModels();

    // Группируем модели по провайдерам
    const providersData = {};

    modelStore.availableModels.forEach(model => {
      if (!providersData[model.provider_id]) {
        providersData[model.provider_id] = {
          id: model.provider_id,
          code: model.provider_code || 'unknown',
          models: []
        };
      }

      providersData[model.provider_id].models.push(model);
    });

    providers.value = Object.values(providersData);

    // Получаем настройки моделей пользователя
    await modelStore.fetchModelPreferences();

    // Создаем карту настроек для удобного доступа
    modelStore.modelPreferences.forEach(pref => {
      modelSettingsMap.value[pref.model_id] = {
        id: pref.id,
        max_tokens: pref.max_tokens,
        temperature: pref.temperature,
        system_prompt: pref.system_prompt || '',
        is_default: pref.is_default
      };
    });
  } catch (error) {
    console.error('Ошибка при загрузке моделей:', error);
    showErrorMessage('Не удалось загрузить список моделей');
  }
};

// Проверка наличия API ключа для провайдера
const hasApiKeyForProvider = (providerId) => {
  return apiKeysStore.getAllKeys.some(key =>
    key.provider_id === providerId && key.is_active
  );
};

// Проверка активности модели
const isModelActive = (modelId) => {
  return modelStore.modelPreferences.some(pref => pref.model_id === modelId);
};

// Проверка, является ли модель моделью по умолчанию
const isModelDefault = (modelId) => {
  const preference = modelStore.modelPreferences.find(pref => pref.model_id === modelId);
  return preference ? preference.is_default : false;
};

// Переключение активации модели
const toggleModelActivation = async (model, provider) => {
  const isActive = isModelActive(model.id);

  if (isActive) {
    // Деактивация модели - открываем модальное окно подтверждения
    confirmDeactivateModel(model.id);
  } else {
    // Активация модели - создаем настройки с дефолтными значениями
    try {
      loading.value = true;

      // Проверяем наличие API ключа
      if (!hasApiKeyForProvider(provider.id)) {
        showErrorMessage('Для активации модели необходимо добавить API ключ');
        return;
      }

      // Создаем базовые настройки для модели
      const preferenceData = {
        provider_id: provider.id,
        model_id: model.id,
        max_tokens: 2000,
        temperature: 0.7,
        system_prompt: '',
        is_default: false // По умолчанию не устанавливаем как дефолтную
      };

      // Проверяем, нет ли уже активных моделей этого провайдера
      const hasActiveModels = modelStore.modelPreferences.some(pref =>
        pref.provider_id === provider.id
      );

      // Если это первая активируемая модель для провайдера, делаем её активной по умолчанию
      if (!hasActiveModels) {
        preferenceData.is_default = true;
      }

      // Создаем настройку модели
      const response = await modelStore.createModelPreference(preferenceData);

      // Добавляем модель в карту настроек
      modelSettingsMap.value[model.id] = {
        id: response.id,
        max_tokens: preferenceData.max_tokens,
        temperature: preferenceData.temperature,
        system_prompt: preferenceData.system_prompt,
        is_default: preferenceData.is_default
      };

      // Автоматически раскрываем настройки новой модели
      expandedModels.value.push(model.id);

      showSuccessMessage(`Модель ${model.name} успешно активирована`);
    } catch (error) {
      console.error('Ошибка при активации модели:', error);
      showErrorMessage('Не удалось активировать модель');
    } finally {
      loading.value = false;
    }
  }
};

// Переключение отображения настроек модели
const toggleModelSettings = (modelId) => {
  const index = expandedModels.value.indexOf(modelId);
  if (index === -1) {
    expandedModels.value.push(modelId);
  } else {
    expandedModels.value.splice(index, 1);
  }
};

// Сохранение настроек модели
const saveModelSettings = async (modelId) => {
  try {
    loading.value = true;

    const settings = modelSettingsMap.value[modelId];
    if (!settings) return;

    // Находим текущие настройки модели
    const currentPreference = modelStore.modelPreferences.find(pref =>
      pref.model_id === modelId
    );

    if (!currentPreference) {
      showErrorMessage('Не найдены настройки модели');
      return;
    }

    // Если устанавливаем модель по умолчанию, убираем этот флаг у других моделей того же провайдера
    if (settings.is_default && !currentPreference.is_default) {
      // Сначала находим все модели этого провайдера
      const providerModels = modelStore.modelPreferences.filter(pref =>
        pref.provider_id === currentPreference.provider_id && pref.id !== currentPreference.id
      );

      // Если среди них есть дефолтная, снимаем с нее флаг
      for (const pref of providerModels) {
        if (pref.is_default) {
          await modelStore.updateModelPreference(pref.id, {
            ...pref,
            is_default: false
          });

          // Обновляем состояние в карте настроек, если эта модель есть в нашей карте
          if (modelSettingsMap.value[pref.model_id]) {
            modelSettingsMap.value[pref.model_id].is_default = false;
          }
        }
      }
    }

    // Обновляем настройки модели
    await modelStore.updateModelPreference(currentPreference.id, {
      provider_id: currentPreference.provider_id,
      model_id: currentPreference.model_id,
      max_tokens: parseInt(settings.max_tokens),
      temperature: parseFloat(settings.temperature),
      system_prompt: settings.system_prompt,
      is_default: settings.is_default
    });

    // Закрываем форму настроек после сохранения
    const index = expandedModels.value.indexOf(modelId);
    if (index !== -1) {
      expandedModels.value.splice(index, 1);
    }

    showSuccessMessage('Настройки модели успешно сохранены');
  } catch (error) {
    console.error('Ошибка при сохранении настроек:', error);
    showErrorMessage('Не удалось сохранить настройки модели');
  } finally {
    loading.value = false;
  }
};

// Открытие модального окна подтверждения деактивации
const confirmDeactivateModel = (modelId) => {
  selectedModelToDeactivate.value = modelId;

  if (deactivateModal) {
    deactivateModal.show();
  } else {
    // Резервный вариант, если модальное окно не инициализировано
    if (confirm('Вы уверены, что хотите деактивировать эту модель? Все ее настройки будут удалены.')) {
      deactivateModel();
    }
  }
};

// Деактивация модели
const deactivateModel = async () => {
  if (!selectedModelToDeactivate.value) return;

  try {
    loading.value = true;

    // Скрываем модальное окно
    if (deactivateModal) {
      deactivateModal.hide();
    }

    // Находим настройки модели
    const modelPreference = modelStore.modelPreferences.find(pref =>
      pref.model_id === selectedModelToDeactivate.value
    );

    if (!modelPreference) {
      showErrorMessage('Не найдены настройки модели');
      return;
    }

    // Удаляем настройки модели
    await modelStore.deleteModelPreference(modelPreference.id);

    // Удаляем модель из списка развернутых
    const index = expandedModels.value.indexOf(selectedModelToDeactivate.value);
    if (index !== -1) {
      expandedModels.value.splice(index, 1);
    }

    // Удаляем настройки из карты
    delete modelSettingsMap.value[selectedModelToDeactivate.value];

    // Если это была модель по умолчанию, и у этого провайдера есть другие модели,
    // устанавливаем первую из них как модель по умолчанию
    if (modelPreference.is_default) {
      const providerModels = modelStore.modelPreferences.filter(pref =>
        pref.provider_id === modelPreference.provider_id && pref.id !== modelPreference.id
      );

      if (providerModels.length > 0) {
        await modelStore.updateModelPreference(providerModels[0].id, {
          ...providerModels[0],
          is_default: true
        });

        // Обновляем состояние в карте настроек
        if (modelSettingsMap.value[providerModels[0].model_id]) {
          modelSettingsMap.value[providerModels[0].model_id].is_default = true;
        }
      }
    }

    showSuccessMessage('Модель успешно деактивирована');
  } catch (error) {
    console.error('Ошибка при деактивации модели:', error);
    showErrorMessage('Не удалось деактивировать модель');
  } finally {
    loading.value = false;
    selectedModelToDeactivate.value = null;
  }
};

// Вспомогательные функции

// Получение имени провайдера
const getProviderName = (providerCode) => {
  const providers = {
    'openai': 'OpenAI (ChatGPT)',
    'anthropic': 'Anthropic (Claude)'
  };

  return providers[providerCode] || providerCode;
};

// Получение цвета для провайдера
const getProviderColor = (providerCode) => {
  const colors = {
    'openai': '#10a37f', // Зеленый для OpenAI
    'anthropic': '#6b48ff'  // Фиолетовый для Anthropic
  };

  return colors[providerCode] || '#6c757d'; // Серый по умолчанию
};

// Получение иконки для провайдера
const getProviderIcon = (providerCode) => {
  const icons = {
    'openai': 'bi-stars',
    'anthropic': 'bi-robot'
  };

  return icons[providerCode] || 'bi-cpu';
};

// Уведомления (можно заменить на компонент уведомлений)
const showSuccessMessage = (message) => {
  alert(message); // В реальном приложении можно заменить на компонент уведомлений
};

const showErrorMessage = (message) => {
  alert(`Ошибка: ${message}`); // В реальном приложении можно заменить на компонент уведомлений
};

// Следим за изменениями в API ключах
watch(() => apiKeysStore.getAllKeys, () => {
  // Обновляем список провайдеров, для которых есть API ключи
  fetchProviders();
}, { deep: true });
</script>

<style scoped>
.provider-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.model-card {
  transition: all 0.3s ease;
}

.model-status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.model-settings-panel {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
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

/* Стили для иконки звезды */
.bi-star-fill.text-warning {
  color: #ffc107 !important;
}

.bi-star-fill.text-muted {
  color: #dee2e6 !important;
  opacity: 0.5;
}

/* Улучшенный стиль для карточек моделей */
.card {
  border-radius: 0.5rem;
  transition: all 0.2s ease-in-out;
}

.card.border-primary {
  box-shadow: 0 0 0 1px rgba(13, 110, 253, 0.25);
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Стили для переключателя */
.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.form-switch .form-check-input {
  width: 2.5em;
  margin-left: -2.8em;
}

/* Улучшения для мобильных устройств */
@media (max-width: 768px) {
  .model-actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
  }
}

/* Добавьте в секцию <style scoped> */
.btn-outline-warning {
  border-color: #ffc107;
  color: #ffc107;
}

.btn-outline-warning:hover {
  background-color: #ffc107;
  color: #212529;
}

.btn-warning {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #212529;
}
</style>