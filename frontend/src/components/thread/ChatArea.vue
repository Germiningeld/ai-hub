<template>
  <div class="chat-area h-100 d-flex flex-column">
    <!-- Управление настройками и контекстом -->
    <div class="chat-controls d-flex justify-content-between p-3">
      <button
        class="btn btn-sm btn-outline-secondary"
        @click="showSettings = !showSettings"
      >
        <i class="bi bi-gear"></i>
        <span class="d-none d-md-inline ms-1">Настройки</span>
      </button>
      
      <div class="form-check form-switch d-flex align-items-center">
        <input class="form-check-input me-2" type="checkbox" id="useContextTop" v-model="useContext">
        <label class="form-check-label small" for="useContextTop">Использовать контекст</label>
      </div>
    </div>
 
    <!-- Настройки треда - скрыты по умолчанию -->
    <div v-if="showSettings" class="chat-settings p-3 border-bottom">
      <div class="row g-3">
        <!-- Выбор провайдера и модели -->
        <div class="col-md-6">
          <label class="form-label small">Провайдер</label>
          <select class="form-select form-select-sm" v-model="selectedProvider" @change="handleProviderChange">
            <option value="">Выберите провайдера</option>
            <option 
              v-for="provider in availableProviders" 
              :key="provider.id" 
              :value="provider.id"
              :disabled="!apiKeysStore.hasActiveKeyForProvider(provider.id)"
            >
              {{ provider.name }} {{ !apiKeysStore.hasActiveKeyForProvider(provider.id) ? '(нет ключа)' : '' }}
            </option>
          </select>
          
          <!-- Предупреждение если нет ключа -->
          <div v-if="selectedProvider && !apiKeysStore.hasActiveKeyForProvider(selectedProvider)" 
               class="alert alert-warning mt-2 p-2 small">
            <i class="bi bi-exclamation-triangle me-1"></i>
            Для этого провайдера нет активного API ключа. 
            <router-link to="/settings" class="alert-link">Добавить ключ</router-link>
          </div>
        </div>
        
        <div class="col-md-6">
          <label class="form-label small">Модель</label>
          <select class="form-select form-select-sm" v-model="selectedModel" :disabled="!modelsForProvider.length">
            <option value="" disabled>Выберите модель</option>
            <option 
              v-for="model in modelsForProvider" 
              :key="model.id" 
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
          <div v-if="selectedModel" class="form-text small">
            {{ getModelDescription(selectedModel) }}
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
        
        <div class="col-md-6">
          <label class="form-label small">Максимальная длина ответа</label>
          <select class="form-select form-select-sm" v-model="maxTokens">
            <option value="500">Короткий ответ (~500 токенов)</option>
            <option value="1000">Средний ответ (~1000 токенов)</option>
            <option value="2000">Подробный ответ (~2000 токенов)</option>
            <option value="4000">Развёрнутый ответ (~4000 токенов)</option>
          </select>
        </div>
        
        <div class="col-12">
          <label class="form-label small">Системный промпт</label>
          <textarea 
            class="form-control form-control-sm" 
            rows="2"
            placeholder="Добавьте системный промпт (если требуется)..."
            v-model="systemPrompt"
          ></textarea>
        </div>
      </div>
      
      <!-- Аналитика треда (убрали данные о цене) -->
      <div v-if="threadCreated" class="chat-analytics mt-3 p-3 rounded bg-light">
        <div class="row g-2 small">
          <div class="col-auto">
            <i class="bi bi-hash"></i> {{ messageCount }} сообщений
          </div>
          <div class="col-auto">
            <i class="bi bi-chat-square-text"></i> {{ totalTokens }} токенов
          </div>
        </div>
      </div>
      
      <div class="d-flex mt-3">
        <button class="btn btn-sm btn-primary" @click="applySettings">
          <i class="bi bi-check"></i> Применить
        </button>
        
        <button class="btn btn-sm btn-outline-secondary ms-2" @click="showSettings = false">
          <i class="bi bi-x"></i> Закрыть
        </button>
      </div>
    </div>
    
 
    <!-- Область сообщений -->
    <div class="chat-messages flex-grow-1 p-0" ref="messagesContainer">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      
      <div v-else-if="messages.length === 0" class="text-center text-muted py-5">
        <p>Начните общение с ассистентом</p>
      </div>
      
      <div v-else class="message-list p-3">
        <MessageItem 
          v-for="(message, index) in messages" 
          :key="index"
          :message="message"
          :model="selectedModel"
        />
      </div>
    </div>
    
    <!-- Поле ввода сообщения -->
    <div class="chat-input-container p-3">
      
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
    </div>
  </div>
 </template>


 <script setup>
 import { ref, onMounted, onUpdated, watch, nextTick, onBeforeUnmount, computed } from 'vue';
 import { useRouter } from 'vue-router';
 import MessageItem from './MessageItem.vue';
 import modelService from '@/services/modelService';
 import apiKeyService from '@/services/apiKeyService';
 import { useApiKeysStore } from '@/stores/apiKeys';
 
 // Добавляем доступ к хранилищу API ключей
 const apiKeysStore = useApiKeysStore();
 const router = useRouter();
 
 // Пропсы
 const props = defineProps({
  threadId: {
    type: String,
    required: true
  }
 });
 
 // Эмиты
 const emit = defineEmits(['close']);
 
 // Состояние компонента
 const loading = ref(true);
 const messages = ref([]);
 const newMessage = ref('');
 const isSending = ref(false);
 const showSettings = ref(false);
 const showPrompts = ref(false);
 const selectedModel = ref('');
 const temperature = ref(0.7);
 const systemPrompt = ref('');
 const useContext = ref(true);
 const messagesContainer = ref(null);
 const messageInput = ref(null);
 const threadCreated = ref(false);
 
 // Добавляем новые состояния
 const selectedProvider = ref('');
 const modelsForProvider = ref([]);
 const maxTokens = ref('2000');
 
 // Данные треда (заглушка, будет получено из API)
 const messageCount = ref(0);
 const totalCost = ref(0);
 const totalTokens = ref(0);
 const isPinned = ref(false);
 
 // Доступные провайдеры
 const availableProviders = apiKeyService.getAvailableProviders();
 
 // Обработчик клавиш для textarea
 const handleTextareaKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (newMessage.value.trim()) {
      sendMessage();
    }
  }
 };
 

 // Функция для обновления списка моделей при изменении провайдера
 const handleProviderChange = () => {
  if (!selectedProvider.value) {
    modelsForProvider.value = [];
    return;
  }
  
  // Если для выбранного провайдера нет активного ключа API
  if (!apiKeysStore.hasActiveKeyForProvider(selectedProvider.value)) {
    modelsForProvider.value = [];
    return;
  }
  
  // Обновляем список моделей для выбранного провайдера
  modelsForProvider.value = allModelsMap.value[selectedProvider.value] || [];
  
  // Выбираем первую модель из списка, если список не пуст
  if (modelsForProvider.value.length > 0) {
    selectedModel.value = modelsForProvider.value[0].id;
  } else {
    selectedModel.value = '';
  }
 };
 
 // Получение описания модели
 const getModelDescription = (modelId) => {
  if (!selectedProvider.value) {
    // Ищем модель в общем списке, если провайдер не выбран
    for (const provider in allModelsMap.value) {
      const model = allModelsMap.value[provider].find(m => m.id === modelId);
      if (model) return model.description;
    }
    return '';
  }
  
  const models = allModelsMap.value[selectedProvider.value] || [];
  const model = models.find(m => m.id === modelId);
  
  return model ? model.description : '';
 };
 
 // Загрузка данных
 onMounted(async () => {
  try {
    // Загрузка API ключей
    await apiKeysStore.fetchApiKeys();
    
    // Определение доступного провайдера и модели по умолчанию
    if (apiKeysStore.hasActiveKeyForProvider('openai')) {
      selectedProvider.value = 'openai';
      modelsForProvider.value = allModelsMap.value['openai'] || [];
      selectedModel.value = 'gpt-4o'; // По умолчанию выбираем GPT-4o для OpenAI
    } else if (apiKeysStore.hasActiveKeyForProvider('anthropic')) {
      selectedProvider.value = 'anthropic';
      modelsForProvider.value = allModelsMap.value['anthropic'] || [];
      selectedModel.value = 'claude-3-opus'; // По умолчанию выбираем Claude 3 Opus для Anthropic
    }
    
    // Если у нас есть существующий тред
    if (props.threadId && props.threadId !== 'new') {
      await loadExistingThread();
    } else {
      // Новый тред ещё не создан
      threadCreated.value = false;
      loading.value = false;
      
      // Установим пустое значение для системного промпта
      systemPrompt.value = '';
    }
    
    // Фокус на поле ввода после загрузки
    nextTick(() => {
      if (messageInput.value) {
        // Добавляем обработчик событий для textarea
        messageInput.value.addEventListener('keydown', handleTextareaKeyDown);
        messageInput.value.focus();
        adjustTextAreaHeight();
      }
    });
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error);
    loading.value = false;
  }
 });
 
 // Загрузка существующего треда
 const loadExistingThread = async () => {
   try {
     // Симуляция запроса к API для получения данных треда
     await new Promise(resolve => setTimeout(resolve, 500));
     
     // Отметим, что тред создан
     threadCreated.value = true;
     
     // Устанавливаем данные треда (в реальном приложении получаем с сервера)
     messageCount.value = 12;
     totalCost.value = 0.024;
     totalTokens.value = 1245;
     isPinned.value = true;
     
     // Загрузка истории сообщений
     messages.value = [
      {
        role: 'user',
        content: 'Как оптимизировать JOIN операции для больших таблиц в PostgreSQL?',
        created_at: '2024-03-16T10:30:45.123456'
      },
      {
        role: 'assistant',
        content: 'Для оптимизации JOIN операций с большими таблицами в PostgreSQL рекомендую следующие подходы:\n\n' +
                '1. **Правильно расставьте индексы**:\n   - Создайте индексы на столбцах соединения\n   - Используйте составные индексы для часто используемых условий WHERE\n\n' +
                '2. **Выбирайте правильный тип JOIN**:\n   - INNER JOIN обычно работает быстрее LEFT JOIN\n   - Рассмотрите возможность использования HASH JOIN для равенства условий\n\n' +
                '3. **Анализируйте планы выполнения запросов**:\n   - Используйте EXPLAIN ANALYZE для понимания, как PostgreSQL выполняет ваш запрос\n   - Ищите узкие места и последовательные сканы\n\n' +
                '3. **Анализируйте планы выполнения запросов**:\n   - Используйте EXPLAIN ANALYZE для понимания, как PostgreSQL выполняет ваш запрос\n   - Ищите узкие места и последовательные сканы\n\n' +
                '3. **Анализируйте планы выполнения запросов**:\n   - Используйте EXPLAIN ANALYZE для понимания, как PostgreSQL выполняет ваш запрос\n   - Ищите узкие места и последовательные сканы\n\n' +
                '3. **Анализируйте планы выполнения запросов**:\n   - Используйте EXPLAIN ANALYZE для понимания, как PostgreSQL выполняет ваш запрос\n   - Ищите узкие места и последовательные сканы\n\n' +
                'Хотите, чтобы я рассмотрел конкретный пример запроса?',
        created_at: '2024-03-16T10:31:20.987654',
        tokens: 258,
        cost: 0.006
      }
     ];
     
     // Определяем провайдера по выбранной модели и устанавливаем модель
     initializeProviderAndModel();
     
     loading.value = false;
   } catch (error) {
     console.error('Ошибка при загрузке существующего треда:', error);
     loading.value = false;
   }
 };
 
 // Инициализация провайдера и модели на основе текущих настроек
 const initializeProviderAndModel = () => {
  // Определяем провайдера по выбранной модели
  if (selectedModel.value) {
    // OpenAI модели
    if (selectedModel.value.includes('gpt')) {
      selectedProvider.value = 'openai';
    } 
    // Claude модели
    else if (selectedModel.value.includes('claude')) {
      selectedProvider.value = 'anthropic';
    }
    
    // Обновляем список моделей
    handleProviderChange();
  }
 };
 
 // Применение настроек
const applySettings = async () => {
  try {
    // Получаем информацию о выбранной модели
    const selectedModelData = availableModels.value.find(
      model => model.code === selectedModel.value
    );
    
    if (!selectedModelData) {
      console.error('Выбранная модель не найдена в списке доступных моделей');
      throw new Error('Не удалось определить модель для применения настроек');
    }
    
    // Подготавливаем данные для обновления
    const settingsData = {
      provider_id: selectedModelData.provider_id,
      provider_code: selectedModelData.provider_code,
      model_id: selectedModelData.model_id,
      model_code: selectedModelData.code,
      model_preference_id: selectedModelData.id,
      temperature: parseFloat(temperature.value),
      max_tokens: parseInt(maxTokens.value),
      system_prompt: systemPrompt.value
    };
    
    console.log('Применение настроек:', settingsData);
    
    // Если у нас активный тред, обновляем его настройки
    if (activeChatId.value) {
      await threadService.updateThread(activeChatId.value, settingsData);
      console.log('Настройки треда успешно обновлены');
      
      // Обновляем системный промпт в сообщениях, если треда существует
      if (!isNewThread.value) {
        await updateSystemPrompt();
      }
    }
    
    // Обновляем предпочтения модели пользователя
    if (selectedModelData.id) {
      const preferenceData = {
        temperature: parseFloat(temperature.value),
        max_tokens: parseInt(maxTokens.value),
        system_prompt: systemPrompt.value
      };
      
      await modelService.updateModelPreference(selectedModelData.id, preferenceData);
      console.log('Предпочтения модели успешно обновлены');
    }
    
    // Закрываем панель настроек
    showSettings.value = false;
    
    // Уведомляем пользователя об успешном обновлении
    alert('Настройки успешно применены');
    
  } catch (error) {
    console.error('Ошибка при применении настроек:', error);
    alert(`Ошибка при обновлении настроек: ${error.message || 'Неизвестная ошибка'}`);
  }
};
 
 // Удаляем обработчик события перед размонтированием компонента
 onBeforeUnmount(() => {
  if (messageInput.value) {
    messageInput.value.removeEventListener('keydown', handleTextareaKeyDown);
  }
  
  // Удаляем обработчик изменения размера окна
  window.removeEventListener('resize', handleResize);
});
 
 // Прокрутка к последнему сообщению при изменении списка сообщений
 onUpdated(() => {
  scrollToBottom();
 });
 
 // Регулировка высоты текстового поля
 const adjustTextAreaHeight = () => {
  if (!messageInput.value) return;
  
  // Сбрасываем высоту
  messageInput.value.style.height = 'auto';
  
  // Устанавливаем новую высоту в зависимости от содержимого
  const newHeight = Math.min(messageInput.value.scrollHeight, 150);
  messageInput.value.style.height = `${newHeight}px`;
 };
 
 // Переменные для debounce
let temperatureUpdateTimeout;
let systemPromptUpdateTimeout;
let maxTokensUpdateTimeout;

 // Отслеживаем изменения в поле ввода для регулировки высоты
 watch(newMessage, () => {
  nextTick(() => {
    adjustTextAreaHeight();
  });
 });
 
// Добавляем наблюдатели для отслеживания изменений настроек
// Наблюдаем за изменением провайдера
watch(selectedProvider, handleProviderChange);
 
 // Наблюдаем за изменением температуры
watch(temperature, () => {
  // Используем debounce для предотвращения частых запросов
  clearTimeout(temperatureUpdateTimeout);
  temperatureUpdateTimeout = setTimeout(() => {
    handleTemperatureChange();
  }, 500); // Задержка 500мс
});

 // Наблюдаем за изменением системного промта
watch(systemPrompt, () => {
  // Используем debounce для предотвращения частых запросов
  clearTimeout(systemPromptUpdateTimeout);
  systemPromptUpdateTimeout = setTimeout(() => {
    handleSystemPromptChange();
  }, 1000); // Задержка 1с для более долгого ввода
});

 // Наблюдаем за изменением провайдера
watch(maxTokens, () => {
  // Используем debounce для предотвращения частых запросов
  clearTimeout(maxTokensUpdateTimeout);
  maxTokensUpdateTimeout = setTimeout(() => {
    handleMaxTokensChange();
  }, 500); // Задержка 500мс
});

 // Отправка сообщения
 const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value) return;
  
  try {
    isSending.value = true;
    
    // Проверяем, создан ли тред
    if (!threadCreated.value) {
      // Создаем новый тред перед отправкой первого сообщения
      await createThread();
    }
    
    // Добавляем сообщение пользователя
    const userMessage = {
      role: 'user',
      content: newMessage.value,
      created_at: new Date().toISOString()
    };
    
    messages.value.push(userMessage);
    
    // Очищаем поле ввода
    const messageText = newMessage.value;
    newMessage.value = '';
    adjustTextAreaHeight();
    
    // Прокручиваем до последнего сообщения
    await nextTick();
    scrollToBottom();
    
    // Данные для запроса
    const requestData = {
      content: messageText,
      system_prompt: systemPrompt.value,
      temperature: temperature.value,
      max_tokens: parseInt(maxTokens.value)
    };
    
    // Имитация запроса к API (в реальном приложении здесь будет вызов API)
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Получаем ответ (заглушка)
    const botResponse = {
      role: 'assistant',
      content: 'Это демонстрационный ответ ассистента. Здесь будет реальный ответ от выбранной модели на ваш запрос.',
      created_at: new Date().toISOString(),
      tokens: 25,
      cost: 0.0005
    };
    
    // Добавляем ответ ассистента
    messages.value.push(botResponse);
    
    // Обновляем статистику треда
    messageCount.value += 2; // +2: вопрос и ответ
    totalTokens.value += botResponse.tokens;
    totalCost.value += botResponse.cost;
    
  } catch (error) {
    console.error('Ошибка при отправке сообщения:', error);
    
    // Проверяем тип ошибки
    let errorMessage = 'Произошла ошибка при получении ответа. Пожалуйста, попробуйте еще раз.';
    
    if (error.response && error.response.data && error.response.data.detail) {
      const detail = error.response.data.detail;
      
      if (detail.error_type === 'api_key_not_found') {
        const providerName = selectedProvider.value === 'openai' ? 'OpenAI' : 
                             selectedProvider.value === 'anthropic' ? 'Anthropic' : selectedProvider.value;
        errorMessage = `API ключ для провайдера ${providerName} не найден. Пожалуйста, добавьте API ключ в настройках.`;
      }
    }
    
    // Добавляем уведомление об ошибке
    messages.value.push({
      role: 'system',
      content: errorMessage,
      created_at: new Date().toISOString()
    });
    
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

 // Создание нового треда
 const createThread = async () => {
   // Проверяем наличие API ключа для текущего провайдера
   const currentProvider = selectedModel.value.includes('gpt') ? 'openai' : 
                          selectedModel.value.includes('claude') ? 'anthropic' : '';
  
   if (currentProvider && !apiKeysStore.hasActiveKeyForProvider(currentProvider)) {
     throw new Error(`Для провайдера ${currentProvider} нет активного API ключа.`);
   }
   
   // Здесь будет отправка запроса на создание треда
   // В реальном приложении вызов API для создания треда
   
   // Отмечаем, что тред создан
   threadCreated.value = true;
   
   // Сбрасываем счетчики
   messageCount.value = 0;
   totalTokens.value = 0;
   totalCost.value = 0;
   
   // В реальном приложении здесь будет ID треда, полученный от сервера
   return { id: 'new-thread-id' };
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
  
  // Обновляем настройки предпочтения модели пользователя
  if (selectedModelData.id) {
    modelService.updateModelPreference(selectedModelData.id, {
      temperature: parseFloat(temperature.value)
    }).catch(error => {
      console.error('Ошибка при обновлении предпочтения модели:', error);
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
    // Обновляем системный промпт в сообщениях, если треда существует
    updateSystemPrompt().catch(error => {
      console.error('Ошибка при обновлении системного промпта:', error);
    });
    
    // Отправляем PUT запрос на обновление треда с новым системным промптом
    threadService.updateThread(activeChatId.value, {
      system_prompt: systemPrompt.value
    }).catch(error => {
      console.error('Ошибка при обновлении системного промпта треда:', error);
    });
  }
  
  // Обновляем настройки предпочтения модели пользователя
  if (selectedModelData.id) {
    modelService.updateModelPreference(selectedModelData.id, {
      system_prompt: systemPrompt.value
    }).catch(error => {
      console.error('Ошибка при обновлении предпочтения модели:', error);
    });
  }
};

// Обработчик изменения максимальной длины ответа
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
  
  // Преобразуем значение в число
  const maxTokensValue = parseInt(maxTokens.value);
  
  // Если мы находимся в активном чате, обновляем настройки треда
  if (activeChatId.value && !isNewThread.value) {
    // Отправляем PUT запрос на обновление треда с новым значением max_tokens
    threadService.updateThread(activeChatId.value, {
      max_tokens: maxTokensValue
    }).catch(error => {
      console.error('Ошибка при обновлении максимальной длины ответа треда:', error);
    });
  }
  
  // Обновляем настройки предпочтения модели пользователя
  if (selectedModelData.id) {
    modelService.updateModelPreference(selectedModelData.id, {
      max_tokens: maxTokensValue
    }).catch(error => {
      console.error('Ошибка при обновлении предпочтения модели:', error);
    });
  }
};



 </script>
 
 <style scoped>
 .chat-area {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  overflow: hidden;
  height: 100%;
 }
 
 .chat-messages {
  overflow-y: auto;
  background-color: #f8f9fa;
 }
 
 .chat-analytics {
  background-color: rgba(67, 97, 238, 0.05);
  border-radius: 0.25rem;
 }
 
 .message-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
 }
 
 
 /* Стилизация поля ввода с кнопками внутри */
 .position-relative {
  position: relative;
 }
 
 .chat-textarea {
  padding-right: 80px; /* Место для кнопок */
  resize: none;
  overflow-y: auto;
  border-radius: 20px;
  transition: all 0.2s;
 }
 
 .chat-input-buttons {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
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
  background: none;
  border: none;
 }
 
 .chat-input-prompt-btn {
  color: #6c757d;
 }
 
 .chat-input-prompt-btn:hover {
  color: #4361ee;
  background-color: rgba(67, 97, 238, 0.1);
 }
 
 .chat-input-send-btn {
  color: #fff;
  background-color: #4361ee;
 }
 
 .chat-input-send-btn:hover {
  background-color: #3a56d4;
 }
 
 .chat-controls {
  background-color: #fff;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
 }
 
 /* Стилизация переключателя контекста */
 .form-check-input:checked {
  background-color: #4361ee;
  border-color: #4361ee;
 }
 
 /* Стилизация ползунка температуры */
 .form-range::-webkit-slider-thumb {
  background: #4361ee;
 }
 .form-range::-moz-range-thumb {
  background: #4361ee;
 }
 .form-range::-ms-thumb {
  background: #4361ee;
 }
 </style>