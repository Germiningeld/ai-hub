<template>
  <div class="d-flex flex-row align-self-stretch h-100">
    <!-- Сайдбар -->
    <Sidebar @toggle="updateSidebarState" />

    <!-- Основной контент -->
    <div class="flex-grow-1 position-relative">

        <!-- Кнопка показать треды (видна только когда треды скрыты) -->
        <button
          v-if="!showThreadList"
          class="btn btn-sm btn-outline-secondary position-absolute d-none d-md-block"
          style="top: 16px; left: 16px; z-index: 100;"
          @click="showThreadList = true"
        >
          <i class="bi bi-layout-sidebar"></i>
        </button>

      <div class="row thread-layout h-100">
        <!-- Колонка с тредами -->
        <div
          v-if="showThreadList"
          class="col-sm-4 col-md-4 col-lg-3 col-threads"
        >
          <!-- Заголовок списка тредов -->
          <div class="thread-list-header d-flex align-items-center justify-content-between p-3 border-bottom">
            <div class="d-flex gap-1">
              <!-- Кнопка скрыть/показать треды -->
              <button 
                class="btn btn-sm btn-outline-secondary"
                @click="showThreadList = !showThreadList"
              >
                <i class="bi" :class="showThreadList ? 'bi-layout-sidebar-inset' : 'bi-layout-sidebar'"></i>
              </button>
            </div>
            <div class="d-flex gap-1">
              <button class="btn btn-sm btn-primary" @click="createNewThread">
                <i class="bi bi-plus-lg"></i> Новая
              </button>
              <button 
                class="btn btn-sm btn-outline-secondary d-md-none"
                @click="showThreadList = false"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </div>

          <!-- Контейнер списка -->
          <ThreadList
            @select-thread="selectThread"
            @create-thread="createNewThread"
          />
        </div>

        <!-- Колонка с основным контентом -->
        <div class="col message-list">
          <div class="d-flex justify-content-center h-100">
            <div class="col col-lg-8 d-flex flex-column h-100 py-3">
              <!-- Верхняя часть остается фиксированной -->
              <div class="mb-3 d-flex justify-content-between align-items-center">
                <div class="d-flex flex-column flex-md-row justify-content-between w-100">
                  <h5>{{ chatTitle }}</h5>
                </div>
              </div>

              <!-- Контейнер для сообщений и формы ввода -->
              <div class="d-flex flex-column h-100">
<!-- Список сообщений - скроллируемый -->
<div class="message-list-container position-relative flex-grow-1 overflow-hidden">
  <div
    class="message-list position-absolute top-0 start-0 end-0 bottom-0 overflow-auto auto-hide-scrollbar"
    ref="messagesContainer"
  >
    <!-- Состояние загрузки -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>

    <!-- Пустое состояние -->
    <div v-else-if="!activeChatId || messages.length === 0" class="text-center text-muted py-5">
      <i class="bi bi-chat-dots text-primary" style="font-size: 4rem;"></i>
      <h4 class="mt-3">Начните новую беседу</h4>
      <p class="text-muted mb-4">
        Выберите существующую беседу или создайте новую
      </p>
    </div>

    <!-- Список сообщений -->
    <template v-else>
      <div class="message-wrapper">
        <MessageItem 
          v-for="message in messages" 
          :key="message.id || `message-${message.created_at}`"
          :message="message"
          :model="String(selectedModel)"
          :isStreamingMode="useStreamingMode.value"
          @stop-generation="stopStreamGeneration"
        />
      </div>
    </template>
  </div>
</div>




                <!-- Поле ввода всегда внизу -->
                <div v-if="activeChatId || isNewThread" class="mt-3">
                  <!-- Форма отправки сообщения -->
                  <div class="position-relative">
  <!-- Кнопки сверху справа -->
  <div class="chat-top-buttons d-none">
    <button class="btn btn-icon chat-square-btn" title="Прикрепить файл">
      <i class="bi bi-paperclip"></i>
    </button>
    <button class="btn btn-icon chat-square-btn" title="Добавить эмодзи">
      <i class="bi bi-emoji-smile"></i>
    </button>
    <button class="btn btn-icon chat-square-btn" title="Дополнительные опции">
      <i class="bi bi-three-dots"></i>
    </button>
  </div>

  <textarea
    class="form-control chat-textarea"
    placeholder="Введите сообщение... (Enter для отправки, Shift+Enter для переноса строки)"
    v-model="newMessage"
    ref="messageInput"
    rows="3"
  ></textarea>

  <!-- Кнопка отправки внутри поля ввода -->
  <div class="chat-input-buttons">
    <button
      v-if="newMessage.trim()"
      class="btn btn-icon chat-input-send-btn"
      @click="sendMessage"
      :disabled="isSending"
      title="Отправить сообщение"
    >
      <i class="bi" :class="isSending ? 'bi-hourglass-split' : 'bi-arrow-up'"></i>
    </button>
  </div>
</div>                  
                  <!-- Инфа о чате -->
                  <div class="chat-controls d-flex justify-content-between align-items-center mt-2">
                    <div class="d-flex">

                      <!-- Настройки  -->
                      <i
                        class="bi bi-gear me-3"
                        style="font-size: 26px; cursor: pointer; color: #212529;"
                        @click="toggleSettings"
                      ></i>

                      <!-- Переключатель контекста -->
                       <!--
                      <div class="form-check form-switch d-flex align-items-center">
                        <input class="form-check-input me-1" type="checkbox" id="useContextTop" v-model="useContext">
                        <label class="form-check-label small" for="useContextTop">Контекст</label>
                      </div>
                    -->

                      <!-- Добавьте этот код в ChatView.vue в блок настроек -->
                       <!--
                      <div class="form-check form-switch d-flex align-items-center ms-3">
                        <input class="form-check-input me-1" type="checkbox" id="useStreamingMode" v-model="useStreamingMode">
                        <label class="form-check-label small" for="useStreamingMode">Потоковый режим</label>
                      </div>
                    -->

                    </div>

                    <!-- Аналитика справа -->
                    <div class="chat-analytics small text-muted px-2 d-flex gap-2">
                      <span><i class="bi bi-hash"></i> {{ messageCount }}</span>
                      <span><i class="bi bi-chat-square-text"></i> {{ totalTokens }}</span>
                    </div>
                  </div>

                  <!-- Настройки треда - появляются под контролами чата -->
<div v-if="showSettings" class="chat-settings p-3 border rounded shadow-sm mt-2">
  <div class="row g-3">
    <div class="col-md-6">
      <label class="form-label small">Модель</label>
      <select class="form-select form-select-sm" v-model="selectedModel" @change="handleModelChange">
        <optgroup v-for="category in modelCategories" :label="category.name" :key="category.name">
          <option 
            v-for="model in category.models" 
            :key="model.id" 
            :value="model.id"
          >
            {{ model.displayName }}
          </option>
        </optgroup>
      </select>
    </div>

    <div class="col-md-6">
      <label class="form-label small">Температура</label>
      <input 
  type="range" 
  class="form-range" 
  min="0" 
  max="1" 
  step="0.1" 
  v-model="temperature" 
  @change="handleTemperatureChange"
>
      <div class="d-flex justify-content-between small text-muted">
        <span>Точный</span>
        <span>{{ temperature }}</span>
        <span>Творческий</span>
      </div>
    </div>
    
    <div class="col-md-6">
      <label class="form-label small">Максимальная длина ответа (токены)</label>
      <input 
  type="number" 
  class="form-control form-control-sm" 
  v-model="maxTokens" 
  @change="handleMaxTokensChange"
  min="100" 
  step="100"
>
    </div>
<!--
    <div class="col-md-12">
      <label class="form-label small">Системный промпт</label>
      <textarea
  class="form-control form-control-sm"
  rows="3"
  placeholder="Добавьте системный промпт..."
  v-model="systemPrompt"
  @blur="handleSystemPromptChange"
></textarea>
    </div>
  -->
    <div v-if="modelLoadError" class="col-12">
      <div class="alert alert-warning small">
        Ошибка загрузки моделей: {{ modelLoadError }}
        <button class="btn btn-sm btn-outline-primary ms-2" @click="loadAvailableModels">
          Повторить
        </button>
      </div>
    </div>
  </div>
</div>




                  <!-- Быстрые промпты (опционально) -->
                  <div v-if="showPrompts" class="mt-2 p-2 border rounded shadow-sm">
                    <div class="prompt-list d-flex flex-wrap gap-2">
                      <button
                        v-for="(prompt, index) in quickPrompts"
                        :key="index"
                        class="btn btn-sm btn-outline-secondary"
                        @click="insertPrompt(prompt.content)"
                      >
                        {{ prompt.title }}
                      </button>
                      <button class="btn btn-sm btn-outline-primary" @click="openPromptLibrary">
                        <i class="bi bi-plus"></i> Еще
                      </button>
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
</template>










<script setup>
import { ref, watch, onMounted, nextTick, onBeforeUnmount, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Sidebar from '../components/layout/Sidebar.vue';
import ThreadList from '../components/thread/ThreadList.vue';
import MessageItem from '../components/thread/MessageItem.vue';
import { setupComponentScrollbar } from '@/utils/scrollbarUtil';

// Импортируем сервисы
import threadService from '@/services/threadService';
import messageService from '@/services/messageService';
import categoryService from '@/services/categoryService';
import modelService from '@/services/modelService';
import promptService from '@/services/promptService';

const router = useRouter();
const route = useRoute();

// ID активного чата
const activeChatId = ref(null);

// Видимость списка тредов (по умолчанию показан, но скрывается при выборе треда на мобильных)
const showThreadList = ref(true);

// Заголовок активного чата
const chatTitle = ref('');

// Состояние сайдбара
const isSidebarCollapsed = ref(true);

// Другие состояния
const loading = ref(false);
const messages = ref([]);
const showSettings = ref(false);
const isNewThread = ref(false);
const showPrompts = ref(false);
const newMessage = ref('');
const isSending = ref(false);
const useContext = ref(true);
const messagesContainer = ref(null);
const messageInput = ref(null);
const systemPrompt = ref('');
const quickPrompts = ref([]);
const categories = ref([]);
const temperature = ref(0.7);
const maxTokens = ref('2000');
const useStreamingMode = ref(false);

// Данные треда
const messageCount = ref(0);
const totalCost = ref(0);
const totalTokens = ref(0);

// Модели и их настройки
const availableModels = ref([]);
const modelCategories = ref([]); // Группировка моделей по категориям
const selectedModel = ref('');
const isLoadingModels = ref(false);
const selectedCategory = ref(1);
const modelLoadError = ref(null);
const modelDetails = ref({}); // Детальная информация о моделях
const currentProviderId = ref(null);
const modelCodeToIdMap = ref({});

// Обработчик клавиш для textarea
const handleTextareaKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (newMessage.value.trim()) {
      sendMessage();
    }
  }
};










// Обновленная функция handleModelChange
const handleModelChange = () => {
  if (!selectedModel.value) return;
  
  console.log("handleModelChange - selectedModel.value:", selectedModel.value);
  console.log("handleModelChange - availableModels:", availableModels.value.map(m => ({ 
    id: m.id, 
    code: m.code, 
    model_id: m.model_id 
  })));
  
  // Получаем информацию о выбранной модели
  const selectedModelData = availableModels.value.find(
    model => model.code === selectedModel.value
  );
  
  console.log("handleModelChange - найденная модель:", selectedModelData);
  
  if (!selectedModelData) {
    console.error('Выбранная модель не найдена в списке доступных моделей');
    throw new Error('Не удалось определить модель для отправки сообщения');
  }  
  
  // Обновляем currentProviderId
  currentProviderId.value = selectedModelData.provider_id;
  
  // Обновляем другие настройки из предпочтения
  temperature.value = selectedModelData.temperature || 0.7;
  
  // Если есть системный промпт в предпочтении, обновляем его
  if (selectedModelData.system_prompt !== null && selectedModelData.system_prompt !== undefined) {
    systemPrompt.value = selectedModelData.system_prompt;
  }
  
  console.log(`Выбрана модель: ${selectedModel.value}, ID предпочтения: ${selectedModelData.id}, провайдер ID: ${currentProviderId.value}`);
  
  // Если мы находимся в активном чате, обновляем настройки треда
  if (activeChatId.value && !isNewThread.value) {
    // Отправляем PUT запрос на обновление треда с выбранной моделью
    threadService.updateThread(activeChatId.value, {
      model_preference_id: selectedModelData.id,  // ID предпочтения
      model_id: selectedModelData.model_id,       // ID самой модели
      provider_id: selectedModelData.provider_id, // ID провайдера
      model_code: selectedModelData.code,         // Код модели
      provider_code: selectedModelData.provider_code, // Код провайдера
      max_tokens: selectedModelData.max_tokens,   // Максимум токенов
      temperature: parseFloat(temperature.value)  // Температура
    }).catch(error => {
      console.error('Ошибка при обновлении настроек треда:', error);
    });
  }
  
  // Если системный промпт изменился, возможно потребуется обновить
  if (activeChatId.value && messages.value.length > 0) {
    updateSystemPrompt().catch(error => {
      console.error('Ошибка при обновлении системного промпта:', error);
    });
  }
};


// Обработчик изменения температуры
const handleTemperatureChange = () => {
  if (!selectedModel.value) return;
  
  console.log("handleTemperatureChange - temperature:", temperature.value);
  
  // Получаем информацию о выбранной модели
  const selectedModelData = availableModels.value.find(
    model => model.code === selectedModel.value
  );
  
  if (!selectedModelData) {
    console.error('Выбранная модель не найдена в списке доступных моделей');
    return;
  }
  
  // Если мы находимся в активном чате, обновляем настройки треда
  if (activeChatId.value && !isNewThread.value) {
    // Отправляем PUT запрос на обновление треда с новой температурой
    threadService.updateThread(activeChatId.value, {
      temperature: parseFloat(temperature.value)
    }).catch(error => {
      console.error('Ошибка при обновлении температуры треда:', error);
    });
  }
};

// Обработчик изменения максимальных токенов
const handleMaxTokensChange = () => {
  if (!selectedModel.value) return;
  
  console.log("handleMaxTokensChange - maxTokens:", maxTokens.value);
  
  // Получаем информацию о выбранной модели
  const selectedModelData = availableModels.value.find(
    model => model.code === selectedModel.value
  );
  
  if (!selectedModelData) {
    console.error('Выбранная модель не найдена в списке доступных моделей');
    return;
  }
  
  // Если мы находимся в активном чате, обновляем настройки треда
  if (activeChatId.value && !isNewThread.value) {
    // Отправляем PUT запрос на обновление треда с новым максимальным количеством токенов
    threadService.updateThread(activeChatId.value, {
      max_tokens: parseInt(maxTokens.value)
    }).catch(error => {
      console.error('Ошибка при обновлении максимальных токенов треда:', error);
    });
  }
};

// Обработчик изменения системного промпта
const handleSystemPromptChange = () => {
  if (!selectedModel.value) return;
  
  console.log("handleSystemPromptChange - systemPrompt:", systemPrompt.value);
  
  // Получаем информацию о выбранной модели
  const selectedModelData = availableModels.value.find(
    model => model.code === selectedModel.value
  );
  
  if (!selectedModelData) {
    console.error('Выбранная модель не найдена в списке доступных моделей');
    return;
  }
  
  // Если мы находимся в активном чате, обновляем настройки треда
  if (activeChatId.value && !isNewThread.value) {
    // Отправляем PUT запрос на обновление треда с новым системным промптом
    threadService.updateThread(activeChatId.value, {
      system_prompt: systemPrompt.value
    }).catch(error => {
      console.error('Ошибка при обновлении системного промпта треда:', error);
    });
    
    // Обновляем системный промпт в сообщениях
    updateSystemPrompt().catch(error => {
      console.error('Ошибка при обновлении системного промпта в сообщениях:', error);
    });
  }
};

 

// Обновленная функция loadAvailableModels 
const loadAvailableModels = async () => {
  try {
    isLoadingModels.value = true;
    modelLoadError.value = null;
    
    // Теперь запрашиваем только model_preferences/preferences, так как он содержит все необходимые данные
    const preferencesResponse = await modelService.getModelPreferences();
    const userPreferences = preferencesResponse.data || [];
    
    console.log("Полученные предпочтения пользователя:", userPreferences);
    
    // Преобразуем предпочтения пользователя в формат для работы в UI
    availableModels.value = userPreferences.map(preference => {
      return {
        id: preference.id, // ID предпочтения
        model_id: preference.model_id,
        provider_id: preference.provider_id,
        code: preference.model_code, // Используем model_code из API
        name: preference.model_code, // Используем model_code как имя 
        provider_code: preference.provider_code,
        context_length: preference.context_length || 8192,
        max_tokens: preference.max_tokens || 2000,
        temperature: preference.temperature || 0.7,
        system_prompt: preference.system_prompt || '',
        is_default: preference.is_default || false
      };
    });

    console.log("loadAvailableModels - преобразованные модели:", availableModels.value);

    // Создаем карту соответствия model_code -> model_id
    modelCodeToIdMap.value = {};
    availableModels.value.forEach(model => {
      if (model.code && model.model_id) {
        modelCodeToIdMap.value[model.code] = model.model_id;
      }
    });
    
    console.log("loadAvailableModels - карта кодов моделей:", modelCodeToIdMap.value);

    // Организуем модели по provider_code для UI
    const categories = {};
    availableModels.value.forEach(model => {
      const providerCode = model.provider_code || 'unknown';
      
      if (!categories[providerCode]) {
        categories[providerCode] = [];
      }
      
      categories[providerCode].push({
        ...model,
        // Используем code как id для отображения в селекте
        id: model.code,
        // Показываем имя и выделяем модель по умолчанию
        displayName: model.name + (model.is_default ? ' (по умолчанию)' : '')
      });
      
      // Сохраняем детали модели для быстрого доступа
      modelDetails.value[model.code] = {
        ...model,
        contextLimit: model.context_length || 8192,
        providerId: model.provider_id,
        max_tokens: model.max_tokens || 2000,
        costInfo: model.pricing || { input: 0, output: 0 }
      };
    });
    
    // Преобразуем в формат для отображения в UI
    modelCategories.value = Object.keys(categories).map(providerCode => ({
      name: providerCode.toUpperCase(),
      models: categories[providerCode]
    }));
    
    // Находим модель по умолчанию
    const defaultModel = availableModels.value.find(model => model.is_default);
    
    // Устанавливаем выбранную модель (по умолчанию или первую доступную)
    if (!selectedModel.value || !availableModels.value.some(model => 
      model.code === selectedModel.value
    )) {
      if (defaultModel) {
        selectedModel.value = defaultModel.code;
        currentProviderId.value = defaultModel.provider_id;
      } else if (availableModels.value.length > 0) {
        selectedModel.value = availableModels.value[0].code;
        currentProviderId.value = availableModels.value[0].provider_id;
      }
    }
    
    // Сохраняем кэш моделей в localStorage для быстрой загрузки при следующем запуске
    localStorage.setItem('models_cache', JSON.stringify({
      timestamp: Date.now(),
      models: availableModels.value,
      categories: modelCategories.value,
      details: modelDetails.value,
      modelCodeToIdMap: modelCodeToIdMap.value
    }));
    
  } catch (error) {
    console.error('Ошибка при загрузке моделей:', error);
    modelLoadError.value = error.message || 'Не удалось загрузить список моделей';
    
    // Пробуем загрузить из кэша, если доступно
    const cachedModels = localStorage.getItem('models_cache');
    if (cachedModels) {
      try {
        const cache = JSON.parse(cachedModels);
        availableModels.value = cache.models || [];
        modelCategories.value = cache.categories || [];
        modelDetails.value = cache.details || {};
        modelCodeToIdMap.value = cache.modelCodeToIdMap || {};
        console.log('Модели загружены из кэша');
      } catch (cacheError) {
        console.error('Ошибка при загрузке моделей из кэша:', cacheError);
      }
    }
  } finally {
    isLoadingModels.value = false;
  }
};

// Добавляем вычисляемое свойство для получения деталей выбранной модели
const getSelectedModelDetails = computed(() => {
  if (!selectedModel.value || !modelDetails.value[selectedModel.value]) {
    return {
      name: 'Неизвестная модель',
      provider: 'unknown',
      contextLimit: 8192,
      costInfo: { input: 0, output: 0 }
    };
  }
  return modelDetails.value[selectedModel.value];
});

// Улучшенное определение провайдера по ID модели
const getProviderNameByModel = (modelId) => {
  // Ищем модель в детальной информации
  if (modelDetails.value[modelId]) {
    return modelDetails.value[modelId].provider;
  }
  
  // Ищем модель в списке доступных моделей
  const model = availableModels.value.find(m => m.id === modelId);
  if (model && model.provider) {
    return model.provider;
  }
  
  // Резервная логика для определения провайдера по ID модели
  const providerPrefixes = {
    'gpt-': 'OpenAI',
    'claude-': 'Anthropic',
    'gemini-': 'Google',
    'llama-': 'Meta',
    'mistral-': 'Mistral AI',
    'j2-': 'Anthropic',
    'command-': 'Cohere'
  };
  
  for (const prefix in providerPrefixes) {
    if (modelId.startsWith(prefix)) {
      return providerPrefixes[prefix];
    }
  }
  
  return 'неизвестного провайдера';
};

// Функция для оценки стоимости запроса
const estimateMessageCost = (messageText, model) => {
  if (!modelDetails.value[model]) {
    return 0;
  }
  
  const costInfo = modelDetails.value[model].costInfo;
  if (!costInfo) return 0;
  
  // Примерное количество токенов (4 символа ~ 1 токен)
  const estimatedTokens = Math.ceil(messageText.length / 4);
  
  // Примерная стоимость запроса (входные токены)
  return (estimatedTokens * costInfo.input) / 1000000; // Конвертация из цены за миллион токенов
};

// Форматирование размера контекста для удобного отображения
const formatContextSize = (tokens) => {
  if (tokens >= 1000000) {
    return `${(tokens / 1000000).toFixed(1)}M токенов`;
  } else if (tokens >= 1000) {
    return `${(tokens / 1000).toFixed(0)}K токенов`;
  }
  return `${tokens} токенов`;
};

// Загрузить настройки из localStorage
const loadStoredThreadId = () => {
  return localStorage.getItem('last_active_thread_id');
};

// Сохранить ID треда в localStorage
const saveThreadIdToStorage = (threadId) => {
  localStorage.setItem('last_active_thread_id', threadId);
};

// При загрузке компонента
onMounted(async () => {
  // Загружаем настройки из localStorage
  const savedState = localStorage.getItem('sidebar_collapsed');
  if (savedState !== null) {
    isSidebarCollapsed.value = JSON.parse(savedState);
  }

  // Пробуем быстро загрузить модели из кэша для мгновенного отображения
  const cachedModels = localStorage.getItem('models_cache');
  if (cachedModels) {
    try {
      const cache = JSON.parse(cachedModels);
      // Проверяем, не устарел ли кэш (например, старше 24 часов)
      const cacheAge = Date.now() - (cache.timestamp || 0);
      if (cacheAge < 24 * 60 * 60 * 1000) { // 24 часа
        availableModels.value = cache.models || [];
        modelCategories.value = cache.categories || [];
        modelDetails.value = cache.details || {};
        console.log('Модели предварительно загружены из кэша');
        
        // Если выбранная модель не установлена и есть доступные модели, устанавливаем первую
        if (!selectedModel.value && availableModels.value.length > 0) {
          selectedModel.value = availableModels.value[0].id;
        }
      }
    } catch (cacheError) {
      console.error('Ошибка при загрузке моделей из кэша:', cacheError);
    }
  }

  // Настраиваем скроллбар для контейнера сообщений
  if (messagesContainer.value) {
    setupComponentScrollbar('.message-list');
  }

  // Загружаем доступные модели
  await loadAvailableModels();

  // Загружаем категории
  try {
    const response = await categoryService.getCategories();
    categories.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке категорий:', error);
  }

  // Загружаем популярные промпты
  try {
    const response = await promptService.getPrompts({
      limit: 5,
      is_favorite: true
    });
    quickPrompts.value = response.data.map(prompt => ({
      title: prompt.title,
      content: prompt.content
    }));
  } catch (error) {
    console.error('Ошибка при загрузке промптов:', error);
  }
  
  // Проверяем наличие ID треда в URL или localStorage
  const threadIdFromURL = route.query.threadId;
  const storedThreadId = loadStoredThreadId();
  
  if (threadIdFromURL) {
    // Если ID треда есть в URL, загружаем его
    activeChatId.value = threadIdFromURL;
    await loadThread(threadIdFromURL);
    isNewThread.value = false;
    showSettings.value = false; // Для существующего треда настройки скрыты
    
    // Сохраняем ID в localStorage
    saveThreadIdToStorage(threadIdFromURL);
    
    // На мобильных устройствах скрываем список тредов
    if (window.innerWidth < 768) {
      showThreadList.value = false;
    }
  } else if (storedThreadId) {
    // Если нет в URL, но есть в localStorage, используем его
    activeChatId.value = storedThreadId;
    await loadThread(storedThreadId);
    isNewThread.value = false;
    showSettings.value = false; // Для существующего треда настройки скрыты
    
    // Обновляем URL
    router.push({ query: { threadId: storedThreadId } });
    
    // На мобильных устройствах скрываем список тредов
    if (window.innerWidth < 768) {
      showThreadList.value = false;
    }
  } else {
    // Если нет ни в URL, ни в localStorage, показываем пустой интерфейс
    chatTitle.value = 'Новая беседа';
    isNewThread.value = true;
    loading.value = false;
  }
  
  // Добавляем обработчик событий для textarea, если оно доступно
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.addEventListener('keydown', handleTextareaKeyDown);
    }
  });
  
});

// Удаляем обработчик события перед размонтированием компонента
onBeforeUnmount(() => {
  if (messageInput.value) {
    messageInput.value.removeEventListener('keydown', handleTextareaKeyDown);
  }
  
});





// Загрузка данных треда
const loadThread = async (threadId) => {
  if (!threadId) {
    console.error('Попытка загрузить тред с пустым ID');
    return;
  }
  
  loading.value = true;
  messages.value = []; // Очищаем сообщения перед загрузкой новых
  
  try {
    console.log(`Загрузка треда: ${threadId}`);
    const response = await threadService.getThread(threadId);
    const thread = response.data;
    
    console.log('Полученные данные треда:', thread);
    
    // Базовая информация о треде
    chatTitle.value = thread.title || 'Без названия';
    messageCount.value = thread.message_count || 0;
    isNewThread.value = false;
    
    // Гарантируем, что thread.messages - это массив
    if (!thread.messages) {
      console.warn('Тред не содержит сообщений или свойство messages отсутствует');
      thread.messages = [];
    } else if (!Array.isArray(thread.messages)) {
      console.error('thread.messages не является массивом:', thread.messages);
      thread.messages = [];
    }
    
    // Подготавливаем сообщения для отображения
    const preparedMessages = thread.messages.map(msg => {
      // Добавляем уникальный ID, если его нет
      if (!msg.id) {
        msg.id = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      }
      return msg;
    });
    
    // Присваиваем подготовленные сообщения
    messages.value = preparedMessages;
    
    // Подсчет только токенов (убираем подсчет стоимости)
    if (messages.value.length > 0) {
      // Обновленное получение токенов, проверяем все возможные поля
      totalTokens.value = messages.value.reduce((sum, msg) => {
        if (msg.tokens_total) {
          return sum + msg.tokens_total;
        } else if (msg.tokens_input || msg.tokens_output) {
          return sum + (msg.tokens_input || 0) + (msg.tokens_output || 0);
        } else if (msg.tokens) {
          return sum + (msg.tokens || 0);
        }
        return sum;
      }, 0);
    }
    
    // Ищем системный промпт - сообщение с ролью system
    const systemMsg = messages.value.find(msg => msg.role === 'system');
    if (systemMsg) {
      systemPrompt.value = systemMsg.content;
    } else {
      systemPrompt.value = ''; // Если нет системного сообщения, очищаем промпт
    }

    // Установка выбранной модели из данных треда
    if (thread.model_code) {
      // Используем model_code напрямую из треда
      selectedModel.value = thread.model_code;
      // Сохраняем provider_id для использования при запросах
      currentProviderId.value = thread.provider_id || null;
    } else {
      // Если model_code не найден, попробуем выбрать модель по умолчанию
      if (availableModels.value.length > 0) {
        const defaultModel = availableModels.value.find(m => m.is_default);
        if (defaultModel) {
          selectedModel.value = defaultModel.code;
          currentProviderId.value = defaultModel.provider_id || null;
        } else {
          selectedModel.value = availableModels.value[0].code;
          currentProviderId.value = availableModels.value[0].provider_id || null;
        }
      }
    }

    // Дополнительно убедимся, что selectedModel - строка
    if (selectedModel.value !== null && selectedModel.value !== undefined) {
      selectedModel.value = String(selectedModel.value);
    }
    console.log('Выбрана модель из треда:', selectedModel.value);
    
    // Получаем данные о выбранной модели
    const selectedModelData = availableModels.value.find(
      model => model.code === selectedModel.value
    );
    console.log('Данные о выбранной модели:', selectedModelData);

    // Установка max_tokens из данных треда
    if (thread.max_tokens) {
      maxTokens.value = String(thread.max_tokens);
    } else if (selectedModelData && selectedModelData.max_tokens) {
      // Если max_tokens нет в треде, но есть в данных модели
      maxTokens.value = String(selectedModelData.max_tokens);
    } else {
      // Значение по умолчанию
      maxTokens.value = '2000';
    }

    // Установка температуры из данных треда
    if (thread.temperature !== undefined && thread.temperature !== null) {
      temperature.value = thread.temperature;
    } else if (selectedModelData && selectedModelData.temperature !== undefined) {
      temperature.value = selectedModelData.temperature;
    } else {
      temperature.value = 0.7; // Значение по умолчанию
    }

    console.log('Установлено max_tokens:', maxTokens.value);
    console.log('Установлена температура:', temperature.value);

  } catch (error) {
    console.error('Ошибка при загрузке треда:', error);
    
    // Добавляем сообщение об ошибке
    messages.value = [{
      id: 'error-message',
      role: 'system',
      content: `Произошла ошибка при загрузке беседы: ${error.message || 'Неизвестная ошибка'}`,
      created_at: new Date().toISOString()
    }];
  } finally {
    loading.value = false;
    
    // Даём DOM время обновиться перед скроллом
    nextTick(() => {
      // Установим таймаут для надежности
      setTimeout(() => {
        scrollToBottom();
      }, 150);
    });
  }
};









// Обработчик выбора треда
const selectThread = async (threadId, title) => {
  // Проверка на валидность ID
  if (!threadId) {
    console.error('Попытка выбрать тред с недопустимым ID');
    return;
  }
  
  console.log(`Выбран тред: ${threadId}, ${title}`);
  
  // Обновляем URL с ID треда
  router.push({ query: { threadId } });
  
  activeChatId.value = threadId;
  chatTitle.value = title || 'Загрузка...';
  
  // Сохраняем ID в localStorage
  saveThreadIdToStorage(threadId);

  try {
    // Загружаем тред
    await loadThread(threadId);
    
    // Для существующего треда настройки скрыты
    showSettings.value = false;
    
    // На мобильных устройствах скрываем список тредов с задержкой,
    // чтобы DOM успел обновиться
    if (window.innerWidth < 768) {
      setTimeout(() => {
        showThreadList.value = false;
      }, 100);
    }
  } catch (error) {
    console.error("Ошибка при загрузке треда:", error);
  }
};

const createNewThread = async () => {
  try {
    console.log('Создание нового треда');
    
    // Очищаем текущий тред и сообщения
    activeChatId.value = null;
    messages.value = [];
    
    // ВСЕГДА показываем настройки при создании нового треда
    showSettings.value = true;
    
    // Устанавливаем состояние нового треда
    chatTitle.value = 'Новая беседа';
    isNewThread.value = true;
    
    // Сбрасываем счетчики
    messageCount.value = 0;
    totalTokens.value = 0;
    
    // Сбрасываем настройки к значениям по умолчанию
    temperature.value = 0.7;
    maxTokens.value = '2000';
    systemPrompt.value = '';
    newMessage.value = ''; // Очищаем поле ввода сообщения

    // Устанавливаем category_id по умолчанию
    selectedCategory.value = 1;

    // Убедимся, что у нас есть доступные модели
    if (availableModels.value.length === 0) {
      await loadAvailableModels();
    }
    
    // Используем модель по умолчанию
    const defaultModel = availableModels.value.find(m => m.is_default) || 
                         availableModels.value[0];
    
    if (defaultModel) {
      selectedModel.value = defaultModel.code;
      currentProviderId.value = defaultModel.provider_id;
    }
    
    // Обновляем URL, удаляя параметр threadId
    router.push({ query: {} });
    
    // На мобильных устройствах скрываем список тредов
    if (window.innerWidth < 768) {
      showThreadList.value = false;
    }
    
    // Фокус на поле ввода
    nextTick(() => {
      if (messageInput.value) {
        messageInput.value.focus();
        adjustTextAreaHeight();
      }
    });
    
  } catch (error) {
    console.error('Ошибка при создании треда:', error);
    alert('Произошла ошибка при подготовке нового треда');
  }
};

// Обновление состояния сайдбара
const updateSidebarState = (newState) => {
  isSidebarCollapsed.value = newState;
  localStorage.setItem('sidebar_collapsed', JSON.stringify(newState));
};

// Переключение настроек
const toggleSettings = () => {
  showSettings.value = !showSettings.value;
  showPrompts.value = false; // Закрываем промпты при открытии настроек
};

// Регулировка высоты текстового поля
const adjustTextAreaHeight = () => {
  if (!messageInput.value) return;
  
  // Сбрасываем высоту
  messageInput.value.style.height = 'auto';
  
  // Устанавливаем новую высоту в зависимости от содержимого
  const newHeight = Math.min(messageInput.value.scrollHeight, 150);
  messageInput.value.style.height = `${newHeight}px`;
};

// Отслеживаем изменения в поле ввода для регулировки высоты
watch(newMessage, () => {
  nextTick(() => {
    adjustTextAreaHeight();
  });
});

// Отправка сообщения
const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value) return;
  
  try {
    // Проверяем режим отправки (потоковый или обычный)
    if (useStreamingMode.value) {
      // Используем потоковый режим
      await sendMessageStream();
    } else {
      // Используем обычный режим
      await sendMessageRegular();
    }
  } catch (error) {
    console.error('Ошибка при отправке сообщения:', error);
    
    // Общая обработка ошибок для обоих режимов
    // Удаляем индикатор загрузки, если он есть
    const loadingIndex = messages.value.findIndex(msg => msg.isLoading === true);
    if (loadingIndex !== -1) {
      messages.value.splice(loadingIndex, 1);
    }
    
    // Проверяем тип ошибки
    let errorMessage = 'Произошла ошибка при получении ответа. Пожалуйста, попробуйте еще раз.';
    
    if (error.response && error.response.data && error.response.data.detail) {
      const detail = error.response.data.detail;
      
      if (detail.error_type === 'api_key_not_found') {
        errorMessage = `API ключ для провайдера ${getProviderNameByModel(selectedModel.value)} не найден. Пожалуйста, выберите другую модель или добавьте API ключ в настройках.`;
        
        // Перезагружаем список доступных моделей
        loadAvailableModels();
      } else if (detail.error_type === 'context_limit_exceeded') {
        // Ошибка превышения контекста
        errorMessage = `Превышен лимит контекста модели (${modelDetails.value[selectedModel.value]?.contextLimit || 'неизвестно'} токенов). Попробуйте использовать модель с большим контекстом или начать новый диалог.`;
      } else if (detail.error_type === 'rate_limit_exceeded') {
        // Превышен лимит запросов
        errorMessage = `Превышен лимит запросов к API провайдера. Пожалуйста, подождите некоторое время и попробуйте снова.`;
      } else if (detail.error_type === 'provider_error') {
        // Ошибка от провайдера API
        errorMessage = `Ошибка от провайдера API: ${detail.error_message || 'неизвестная ошибка'}`;
      }
    }
    
    // Добавляем уведомление об ошибке
    messages.value.push({
      id: `error-${Date.now()}`,
      role: 'system',
      content: errorMessage,
      created_at: new Date().toISOString()
    });
    
    // Если мы пытались создать новый тред, но не удалось, возвращаем флаг isNewThread
    if (activeChatId.value === null) {
      isNewThread.value = true;
    }
    
    // Прокручиваем до последнего сообщения
    await nextTick();
    scrollToBottom();
    
  } finally {
    isSending.value = false;
    
    // Фокус на поле ввода после отправки
    nextTick(() => {
      if (messageInput.value) {
        messageInput.value.focus();
      }
    });
  }
};

// Обычная отправка сообщения (не потоковая)
const sendMessageRegular = async () => {
  if (!newMessage.value.trim() || isSending.value) return;
  
  try {
    isSending.value = true;
    console.log('Отправка сообщения (обычный режим)...');
    
    // Проверяем, нужно ли создать новый тред
    if (isNewThread.value) {
      // Создаем новый тред перед отправкой первого сообщения
      await createThreadOnServer();
    }
    
    // Создаем сообщение пользователя
    const userMessage = {
      id: `temp-${Date.now()}`, // Временный ID для нового сообщения
      content: newMessage.value,
      role: "user",
      created_at: new Date().toISOString()
    };
    
    // Добавляем в локальный массив
    messages.value.push(userMessage);
    
    // Очищаем поле ввода
    const messageText = newMessage.value;
    newMessage.value = '';
    adjustTextAreaHeight();
    
    // Прокручиваем до последнего сообщения
    await nextTick();
    scrollToBottom();
    
    // После первого сообщения этот тред уже не считается новым
    if (isNewThread.value) {
      isNewThread.value = false;
    }
    
    // Проверяем, нужно ли обновить системный промпт
    await updateSystemPrompt();
    
    console.log("sendMessageRegular - selectedModel.value:", selectedModel.value);
    
    // Получаем информацию о выбранной модели
    const selectedModelData = availableModels.value.find(
      model => model.code === selectedModel.value
    );

    console.log("sendMessageRegular - найденная модель:", selectedModelData);

    if (!selectedModelData) {
      throw new Error('Выбранная модель не найдена в списке доступных моделей');
    }
    
    // Добавляем индикатор загрузки
    const loadingMessageId = `loading-${Date.now()}`;
    const loadingMessage = {
      id: loadingMessageId,
      role: 'assistant',
      content: 'Генерирую ответ...',
      created_at: new Date().toISOString(),
      isLoading: true
    };
    
    messages.value.push(loadingMessage);
    await nextTick();
    scrollToBottom();
    
    // Данные для запроса
    const requestData = {
      content: messageText,
      system_prompt: systemPrompt.value || selectedModelData.system_prompt || '',
      temperature: parseFloat(temperature.value || selectedModelData.temperature || 0.7),
      max_tokens: parseInt(maxTokens.value || selectedModelData.max_tokens || 2000),
      model_id: selectedModelData.model_id,
      provider_id: selectedModelData.provider_id,
      model_code: selectedModelData.code,
      provider_code: selectedModelData.provider_code,
      model_preference_id: selectedModelData.id, // ID предпочтения модели
      use_context: useContext.value
    };
    
    console.log('Отправка запроса к API:', requestData);
    
    // Отправляем запрос к API
    const response = await messageService.sendMessage(
      activeChatId.value,
      requestData,
      useContext.value
    );
    
    console.log('Получен ответ от API:', response.data);
    
    // Находим и удаляем индикатор загрузки
    const loadingIndex = messages.value.findIndex(msg => msg.id === loadingMessageId);
    if (loadingIndex !== -1) {
      messages.value.splice(loadingIndex, 1);
    }
    
    // Добавляем ответ ассистента в массив
    const assistantMessage = response.data;
    
    // Убедимся, что у сообщения есть ID
    if (!assistantMessage.id) {
      assistantMessage.id = `assistant-${Date.now()}`;
    }
    
    messages.value.push(assistantMessage);

    // Обновляем статистику
    messageCount.value = messages.value.length;

    // Обновленная обработка токенов (без стоимости)
    if (assistantMessage.tokens_total) {
      totalTokens.value += assistantMessage.tokens_total;
    } else if (assistantMessage.tokens_input || assistantMessage.tokens_output) {
      totalTokens.value += (assistantMessage.tokens_input || 0) + (assistantMessage.tokens_output || 0);
    } else if (assistantMessage.tokens) {
      // Для обратной совместимости
      totalTokens.value += assistantMessage.tokens;
    }
    
    // Обновляем заголовок треда, если это первое сообщение
    if (chatTitle.value === 'Новая беседа' && messageText.length > 0) {
      // Используем первые 30 символов сообщения пользователя как заголовок
      const newTitle = messageText.substring(0, 30) + (messageText.length > 30 ? '...' : '');
      chatTitle.value = newTitle;
      
      // Обновляем заголовок треда на сервере
      try {
        await threadService.updateThread(activeChatId.value, { title: newTitle });
      } catch (titleError) {
        console.error('Ошибка при обновлении заголовка треда:', titleError);
      }
    }
    
    // Прокручиваем до последнего сообщения
    await nextTick();
    scrollToBottom();
    
  } catch (error) {
    console.error('Ошибка при отправке сообщения в обычном режиме:', error);
    throw error; // Прокидываем ошибку выше для общей обработки
  }
};


// Функция для получения заголовка авторизации
const getAuthHeader = () => {
  // Получаем токен из localStorage или другого хранилища
  const token = localStorage.getItem('auth_token');
  if (token) {
    return {
      'Authorization': `Bearer ${token}`
    };
  }
  return {};
};




// Метод для обновления системного промпта
const updateSystemPrompt = async () => {
  // Если нет активного треда, ничего не делаем
  if (!activeChatId.value) return;
  
  try {
    // Ищем существующее системное сообщение
    const systemMessageIndex = messages.value.findIndex(msg => msg.role === 'system');
    
    // Если нет системного сообщения и есть системный промпт - создаем новое
    if (systemMessageIndex === -1 && systemPrompt.value) {
      // Определяем model_id и provider_id для нового системного сообщения
      const modelInfo = getSelectedModelDetails.value;
      let modelIdToSend = selectedModel.value;
      if (modelCodeToIdMap.value[selectedModel.value]) {
        modelIdToSend = modelCodeToIdMap.value[selectedModel.value];
      }
      
      // Создаем новое системное сообщение
      const newSystemMessage = {
        role: 'system',
        content: systemPrompt.value,
        created_at: new Date().toISOString(),
        model_code: selectedModel.value,
        model_id: modelIdToSend,
        provider_id: currentProviderId.value || modelInfo.providerId
      };
      
      // В реальном приложении здесь был бы API запрос на создание системного сообщения
      try {
        // Отправляем запрос на создание системного сообщения
        const response = await messageService.createSystemMessage(
          activeChatId.value, 
          {
            content: systemPrompt.value,
            model_id: modelIdToSend,
            provider_id: currentProviderId.value || modelInfo.providerId
          }
        );
        
        // Обновляем локальное сообщение идентификатором с сервера, если он вернулся
        if (response && response.data && response.data.id) {
          newSystemMessage.id = response.data.id;
        }
      } catch (error) {
        console.error('Ошибка при создании системного сообщения на сервере:', error);
      }
      
      // Добавляем сообщение в начало массива
      messages.value.unshift(newSystemMessage);
      
    } 
    // Если есть системное сообщение и его содержимое изменилось - обновляем
    else if (systemMessageIndex !== -1 && messages.value[systemMessageIndex].content !== systemPrompt.value) {
      // Копируем сообщение для обновления
      const updatedSystemMessage = { ...messages.value[systemMessageIndex] };
      const originalMessageId = updatedSystemMessage.id;
      updatedSystemMessage.content = systemPrompt.value;
      
      // В реальном приложении здесь был бы API запрос на обновление системного сообщения
      try {
        if (originalMessageId) {
          // Отправляем запрос на обновление системного сообщения
          await messageService.updateMessage(
            activeChatId.value,
            originalMessageId,
            { content: systemPrompt.value }
          );
        }
      } catch (error) {
        console.error('Ошибка при обновлении системного сообщения на сервере:', error);
      }
      
      // Обновляем сообщение в массиве
      messages.value[systemMessageIndex] = updatedSystemMessage;
    }
  } catch (error) {
    console.error('Ошибка при обновлении системного промпта:', error);
  }
};

// Обновленная функция createThreadOnServer
const createThreadOnServer = async () => {
  try {
    // Убедимся, что у нас есть выбранная модель
    if (!selectedModel.value && availableModels.value.length > 0) {
      const defaultModel = availableModels.value.find(model => model.is_default);
      selectedModel.value = defaultModel 
        ? defaultModel.code
        : availableModels.value[0].code;
    }
    
    // Получаем информацию о выбранной модели
    const selectedModelData = availableModels.value.find(
      model => model.code === selectedModel.value
    );
    
    if (!selectedModelData) {
      console.error('Выбранная модель не найдена в списке доступных моделей');
      throw new Error('Не удалось определить модель для нового треда');
    }
    
    // Данные для создания треда
    const threadData = {
      title: 'Новая беседа',
      provider_id: selectedModelData.provider_id,
      provider_code: selectedModelData.provider_code,
      model_id: selectedModelData.model_id,
      model_code: selectedModelData.code,
      model_preferences_id: selectedModelData.id,
      category_id: selectedCategory.value,
      is_pinned: false,
      is_archived: false,
      system_prompt: systemPrompt.value || selectedModelData.system_prompt || '',
      max_tokens: parseInt(selectedModelData.max_tokens || 2000),
      temperature: parseFloat(temperature.value || selectedModelData.temperature || 0.7)
    };
    
    console.log('Создание треда с данными:', threadData);
    
    // Создаем тред на сервере
    const response = await threadService.createThread(threadData);
    const newThread = response.data;
    
    console.log('Получен ответ:', newThread);
    
    // Устанавливаем ID активного треда
    activeChatId.value = newThread.id;
    chatTitle.value = newThread.title;
    
    // Сохраняем ID в localStorage
    saveThreadIdToStorage(newThread.id);
    
    // Обновляем URL с ID треда
    router.push({ query: { threadId: newThread.id } });
    
    console.log(`Создан новый тред с ID: ${newThread.id}`);
    return newThread;
    
  } catch (error) {
    console.error('Ошибка при создании треда на сервере:', error);
    throw error;
  }
};




// Вставка промпта в поле ввода
const insertPrompt = (promptText) => {
  newMessage.value = promptText;
  showPrompts.value = false;
  
  // Фокус на поле ввода
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.focus();
      adjustTextAreaHeight();
    }
  });
};

// Открытие библиотеки промптов
const openPromptLibrary = () => {
  router.push('/prompts');
};


// Прокрутка к последнему сообщению
const scrollToBottom = () => {
  if (messagesContainer.value) {
    console.log('Выполняем прокрутку к последнему сообщению');
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  } else {
    console.warn('Контейнер сообщений не найден');
  }
};




</script>









<style scoped>
/* Базовые стили для сетки */
.thread-layout {
  --bs-gutter-x: 0;
  width: 100%;
  margin: 0;
}

/* Колонка с тредами */
.col-threads {
  max-width: 460px;
  padding: 0;
  border-right: 1px solid #dee2e6;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* Заголовок списка */
.thread-list-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  background-color: #fff;
}

/* Список сообщений - скроллируемый */
.message-list-container {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
}

.message-list {
  background-color: #f8f9fa;
  padding: 1rem;
}

/* Стилизация поля ввода с кнопками внутри */
.position-relative {
  position: relative;
}

.chat-textarea {
  padding-right: 50px;
  resize: none;
  border-radius: 12px;
}

/* Позиционирование кнопок в верхней части textarea */
.chat-input-buttons {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Стиль для кнопки отправки */
.chat-input-send-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-color: #0d6efd;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  transition: background-color 0.2s;
}

.chat-input-send-btn:hover {
  background-color: #0b5ed7;
}

.chat-input-send-btn:disabled {
  background-color: #9fc3fe;
  cursor: not-allowed;
}

/* Стили для настроек чата */
.chat-settings {
  background-color: #fff;
}

/* Стиль для статистики чата */
.chat-analytics {
  white-space: nowrap;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .col-threads {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 100%;
    z-index: 1040;
    background-color: #fff;
  }
}

.stop-generation-btn {
  margin-left: 10px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.75rem;
}

.stop-generation-btn:hover {
  background-color: #c82333;
}
</style>