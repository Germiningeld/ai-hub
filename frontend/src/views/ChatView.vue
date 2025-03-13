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
                    <div v-if="loading" class="text-center py-5">
                      <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Загрузка...</span>
                      </div>
                    </div>

                    <div v-else-if="!activeChatId || messages.length === 0" class="text-center text-muted py-5">
                      <i class="bi bi-chat-dots text-primary" style="font-size: 4rem;"></i>
                      <h4 class="mt-3">Начните новую беседу</h4>
                      <p class="text-muted mb-4">
                        Выберите существующую беседу или создайте новую
                      </p>
                    </div>

                    <MessageItem
                      v-else
                      v-for="(message, index) in messages"
                      :key="index"
                      :message="message"
                      :model="selectedModel"
                    />
                  </div>
                </div>

                <!-- Поле ввода всегда внизу -->
                <div v-if="activeChatId" class="mt-3">
                  <!-- Форма отправки сообщения -->
                  <div class="position-relative">
                    <textarea
                      class="form-control chat-textarea"
                      placeholder="Введите сообщение... (Enter для отправки, Shift+Enter для переноса строки)"
                      v-model="newMessage"
                      ref="messageInput"
                      rows="3"
                    ></textarea>

                    <!-- Кнопки внутри поля ввода -->
                    <div class="chat-input-buttons">
                      <button
                        v-if="newMessage.trim()"
                        class="btn btn-icon chat-input-send-btn"
                        @click="sendMessage"
                        :disabled="isSending"
                        title="Отправить сообщение"
                      >
                        <i class="bi" :class="isSending ? 'bi-hourglass-split' : 'bi-send-fill'"></i>
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
                      <div class="form-check form-switch d-flex align-items-center">
                        <input class="form-check-input me-1" type="checkbox" id="useContextTop" v-model="useContext">
                        <label class="form-check-label small" for="useContextTop">Контекст</label>
                      </div>
                    </div>

                    <!-- Аналитика справа -->
                    <div class="chat-analytics small text-muted px-2 d-flex gap-2">
                      <span><i class="bi bi-hash"></i> {{ messageCount }}</span>
                      <span><i class="bi bi-coin"></i> {{ formatCost(totalCost) }}</span>
                      <span><i class="bi bi-chat-square-text"></i> {{ totalTokens }}</span>
                    </div>
                  </div>

                  <!-- Настройки треда - появляются под контролами чата -->
                  <div v-if="showSettings" class="chat-settings p-3 border rounded shadow-sm mt-2">
                    <div class="row g-3">
                      <div class="col-md-6">
                        <label class="form-label small">Модель</label>
                        <select class="form-select form-select-sm" v-model="selectedModel">
                          <optgroup v-for="category in modelCategories" :label="category.name" :key="category.name">
                            <option 
                              v-for="model in category.models" 
                              :key="model.id" 
                              :value="model.id"
                            >
                              {{ model.name }}
                              <span v-if="model.badge" class="badge bg-primary ms-1">{{ model.badge }}</span>
                            </option>
                          </optgroup>
                        </select>
                        <div v-if="getSelectedModelDetails" class="small text-muted mt-1">
                          <div>Контекст: {{ formatContextSize(getSelectedModelDetails.contextLimit) }}</div>
                          <div>Стоимость: ${{ formatCost(estimateMessageCost(newMessage || 'Пример текста из 100 символов для оценки', selectedModel)) }} (оценка)</div>
                        </div>
                      </div>

                      <div class="col-md-6">
                        <label class="form-label small">Температура</label>
                        <input type="range" class="form-range" min="0" max="1" step="0.1" v-model="temperature">
                        <div class="d-flex justify-content-between small text-muted">
                          <span>Точный</span>
                          <span>{{ temperature }}</span>
                          <span>Творческий</span>
                        </div>
                      </div>

                      <div class="col-12">
                        <label class="form-label small">Системный промпт</label>
                        <textarea
                          class="form-control form-control-sm"
                          rows="2"
                          placeholder="Добавьте системный промпт..."
                          v-model="systemPrompt"
                        ></textarea>
                      </div>
                      
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

// Данные треда
const messageCount = ref(0);
const totalCost = ref(0);
const totalTokens = ref(0);

// Модели и их настройки
const availableModels = ref([]);
const modelCategories = ref([]); // Группировка моделей по категориям
const selectedModel = ref('');
const isLoadingModels = ref(false);
const modelLoadError = ref(null);
const modelDetails = ref({}); // Детальная информация о моделях

// Обработчик клавиш для textarea
const handleTextareaKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (newMessage.value.trim()) {
      sendMessage();
    }
  }
};

// Улучшенная загрузка доступных моделей с сервера
const loadAvailableModels = async () => {
  try {
    isLoadingModels.value = true;
    modelLoadError.value = null;
    
    const response = await modelService.getAvailableModels();
    availableModels.value = response.data.models || [];
    
    // Организуем модели по категориям/провайдерам для UI
    const categories = {};
    availableModels.value.forEach(model => {
      if (!categories[model.provider]) {
        categories[model.provider] = [];
      }
      categories[model.provider].push(model);
      
      // Сохраняем детали модели для быстрого доступа
      modelDetails.value[model.id] = {
        ...model,
        // Добавляем дополнительные параметры, если есть
        contextLimit: model.context_length || 8192,
        costInfo: model.pricing || { input: 0, output: 0 }
      };
    });
    
    // Преобразуем в формат для отображения в UI
    modelCategories.value = Object.keys(categories).map(provider => ({
      name: provider,
      models: categories[provider]
    }));
    
    // Проверяем, доступна ли текущая выбранная модель
    const isSelectedModelAvailable = availableModels.value.some(
      model => model.id === selectedModel.value
    );
    
    // Если выбранная модель недоступна, выбираем первую доступную
    if (!isSelectedModelAvailable && availableModels.value.length > 0) {
      selectedModel.value = availableModels.value[0].id;
    }
    
    // Сохраняем кэш моделей в localStorage для быстрой загрузки при следующем запуске
    localStorage.setItem('models_cache', JSON.stringify({
      timestamp: Date.now(),
      models: availableModels.value,
      categories: modelCategories.value,
      details: modelDetails.value
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
    loadThread(threadIdFromURL);
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
    loadThread(storedThreadId);
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
  
  // Удаляем обработчик изменения размера окна
  window.removeEventListener('resize', handleResize);
});

// Загрузка данных треда
const loadThread = async (threadId) => {
  loading.value = true;
  
  try {
    const response = await threadService.getThread(threadId);
    const thread = response.data;
    
    chatTitle.value = thread.title;
    messages.value = thread.messages || [];
    messageCount.value = thread.message_count || 0;
    isNewThread.value = false;
    
    // Считаем общую стоимость и токены
    if (messages.value.length > 0) {
      // Обновленное получение токенов, проверяем все возможные поля
      totalTokens.value = messages.value.reduce((sum, msg) => {
        // Используем tokens_total, если доступно, иначе пробуем другие поля
        if (msg.tokens_total) {
          return sum + msg.tokens_total;
        } else if (msg.tokens_input || msg.tokens_output) {
          return sum + (msg.tokens_input || 0) + (msg.tokens_output || 0);
        } else if (msg.tokens) {
          // Для обратной совместимости
          return sum + (msg.tokens || 0);
        }
        return sum;
      }, 0);
      
      totalCost.value = messages.value.reduce((sum, msg) => {
        if (msg.cost) {
          return sum + msg.cost;
        } else if (msg.meta_data && msg.meta_data.cost) {
          return sum + msg.meta_data.cost;
        }
        return sum;
      }, 0);
    }
    
    // Если есть сообщение системы, то устанавливаем его как системный промпт
    const systemMsg = messages.value.find(msg => msg.role === 'system');
    if (systemMsg) {
      systemPrompt.value = systemMsg.content;
    }
    
    // Устанавливаем выбранную модель
    if (thread.model) {
      selectedModel.value = thread.model;
      
      // Проверяем, доступна ли модель из треда
      const isModelAvailable = availableModels.value.some(
        model => model.id === thread.model
      );
      
      // Если модель недоступна, выбираем первую доступную
      if (!isModelAvailable && availableModels.value.length > 0) {
        selectedModel.value = availableModels.value[0].id;
      }
    }
    
  } catch (error) {
    console.error('Ошибка при загрузке треда:', error);
  } finally {
    loading.value = false;
    
    // Прокручиваем к последнему сообщению
    nextTick(() => {
      scrollToBottom();
    });
  }
};

// Обработчик выбора треда
const selectThread = async (threadId, title) => {
  // Обновляем URL с ID треда
  router.push({ query: { threadId } });
  
  activeChatId.value = threadId;
  chatTitle.value = title || 'Загрузка...';
  
  // Сохраняем ID в localStorage
  saveThreadIdToStorage(threadId);
  
  // Загружаем тред
  await loadThread(threadId);
  
  // Для существующего треда настройки скрыты
  showSettings.value = false;
  
  // На мобильных устройствах скрываем список тредов
  if (window.innerWidth < 768) {
    showThreadList.value = false;
  }
};

// Обработчик создания нового треда
const createNewThread = async () => {
  try {
    // Очищаем текущий тред и сообщения
    activeChatId.value = null;
    messages.value = [];
    newMessage.value = '';
    
    // Устанавливаем состояние нового треда
    chatTitle.value = 'Новая беседа';
    isNewThread.value = true;
    
    // Убедимся, что у нас есть доступные модели
    if (availableModels.value.length === 0) {
      await loadAvailableModels();
      if (availableModels.value.length === 0) {
        // Если нет доступных моделей, показываем сообщение об ошибке
        alert('Нет доступных моделей. Пожалуйста, добавьте API ключи в настройках.');
        return;
      }
    }
    
    // Используем доступную модель
    const modelToUse = availableModels.value.find(m => m.id === selectedModel.value) || 
                      availableModels.value[0];
    
    // Устанавливаем модель по умолчанию, если не выбрана
    if (!selectedModel.value && modelToUse) {
      selectedModel.value = modelToUse.id;
    }
    
    // Показываем настройки для нового треда
    showSettings.value = true;
    
    // Обновляем URL, удаляя параметр threadId
    router.push({ query: {} });
    
    // Сбрасываем счетчики
    messageCount.value = 0;
    totalTokens.value = 0;
    totalCost.value = 0;
    
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
    alert('Ошибка при подготовке нового треда: ' + (error.message || 'Неизвестная ошибка'));
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
    isSending.value = true;
    
    // Проверяем, нужно ли создать новый тред
    if (isNewThread.value) {
      // Создаем новый тред перед отправкой первого сообщения
      await createThreadOnServer();
    }
    
    // Создаем сообщение пользователя
    const userMessage = {
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
      // Не скрываем настройки автоматически после первого сообщения,
      // пользователь может сам их скрыть если захочет
    }
    
    // Получаем детали модели для передачи в запрос
    const modelInfo = getSelectedModelDetails.value;
    
    // Данные для запроса
    const requestData = {
      content: messageText,
      system_prompt: systemPrompt.value,
      temperature: parseFloat(temperature.value),
      max_tokens: parseInt(modelInfo.max_tokens || 2000)
    };
    
    // Отправляем запрос к API
    const response = await messageService.sendMessage(
      activeChatId.value,
      requestData,
      useContext.value
    );
    
    // Добавляем ответ ассистента в массив
    const assistantMessage = response.data;
    messages.value.push(assistantMessage);

    // Обновляем статистику
    messageCount.value = messages.value.length;

    // Обновленная обработка токенов
    if (assistantMessage.tokens_total) {
      totalTokens.value += assistantMessage.tokens_total;
    } else if (assistantMessage.tokens_input || assistantMessage.tokens_output) {
      totalTokens.value += (assistantMessage.tokens_input || 0) + (assistantMessage.tokens_output || 0);
    } else if (assistantMessage.tokens) {
      // Для обратной совместимости
      totalTokens.value += assistantMessage.tokens;
    }
    
    // Обработка стоимости
    if (assistantMessage.cost) {
      totalCost.value += assistantMessage.cost;
    } else if (assistantMessage.meta_data && assistantMessage.meta_data.cost) {
      totalCost.value += assistantMessage.meta_data.cost;
    }
    
  } catch (error) {
    console.error('Ошибка при отправке сообщения:', error);
    
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
      role: 'system',
      content: errorMessage,
      created_at: new Date().toISOString()
    });
    
    // Если мы пытались создать новый тред, но не удалось, возвращаем флаг isNewThread
    if (activeChatId.value === null) {
      isNewThread.value = true;
    }
    
  } finally {
    isSending.value = false;
    
    // Фокус на поле ввода после отправки
    nextTick(() => {
      if (messageInput.value) {
        messageInput.value.focus();
      }
      scrollToBottom();
    });
  }
};

// Создание треда на сервере
const createThreadOnServer = async () => {
  try {
    // Убедимся, что у нас есть выбранная модель
    if (!selectedModel.value && availableModels.value.length > 0) {
      selectedModel.value = availableModels.value[0].id;
    }
    
    // Получаем провайдера из модели
    const currentModel = availableModels.value.find(m => m.id === selectedModel.value);
    if (!currentModel) {
      throw new Error('Не удалось определить провайдера для выбранной модели');
    }
    
    // Данные для создания треда
    const threadData = {
      title: 'Новая беседа',
      provider: currentModel.provider,
      model: selectedModel.value,
      category_id: null,
      is_pinned: false,
      is_archived: false,
      initial_message: "",  // Не используем initial_message, т.к. отправим сообщение отдельно
      system_prompt: systemPrompt.value,
      max_tokens: parseInt(getSelectedModelDetails.value.max_tokens || 2000),
      temperature: parseFloat(temperature.value)
    };
    
    // Создаем тред на сервере
    const response = await threadService.createThread(threadData);
    const newThread = response.data;
    
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

// Форматирование стоимости
const formatCost = (cost) => {
  return `$${cost.toFixed(4)}`;
};

// Прокрутка к последнему сообщению
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// Обработчик изменения размера окна
const handleResize = () => {
  if (activeChatId.value && window.innerWidth < 768) {
    showThreadList.value = false;
  }
};

// Отслеживаем изменение размера окна для адаптивности
window.addEventListener('resize', handleResize);
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
  padding-right: 80px; /* Место для кнопок */
  resize: none;
  border-radius: 20px;
  transition: all 0.2s;
}

.chat-input-buttons {
 position: absolute;
 right: 10px;
 bottom: 10px;
 display: flex;
 gap: 5px;
}

.btn-icon {
 width: 32px;
 height: 32px;
 display: flex;
 align-items: center;
 justify-content: center;
 border-radius: 50%;
 padding: 0;
}

.chat-input-prompt-btn {
 color: #6c757d;
 background: none;
 border: none;
}

.chat-input-prompt-btn:hover {
 color: #4361ee;
 background-color: rgba(67, 97, 238, 0.1);
}

.chat-input-send-btn {
 color: #fff;
 background-color: #4361ee;
 border: none;
}

.chat-input-send-btn:hover {
 background-color: #3a56d4;
}

/* Стили для настроек чата */
.chat-settings {
  background-color: #fff;
}

/* Улучшенный стиль для статистики чата */
.chat-analytics {
  white-space: nowrap;
}

/* Стиль для карточек моделей в списке */
.model-badge {
  font-size: 0.7em;
  padding: 0.15em 0.4em;
  margin-left: 0.5em;
  vertical-align: middle;
}

/* Индикатор доступных возможностей модели */
.model-capabilities {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.25rem;
}

.capability-icon {
  width: 16px;
  height: 16px;
  opacity: 0.6;
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
</style>