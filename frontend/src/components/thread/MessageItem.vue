<template>
  <div
    class="message-item"
    :class="{
      'message-user': message.role === 'user',
      'message-assistant': message.role === 'assistant',
      'message-system': message.role === 'system',
      'message-loading': message.isLoading
    }"
  >
    <!-- Аватар и роль -->
    <div class="message-avatar" :class="`message-avatar-${message.role}`">
      <i class="bi" :class="avatarIcon"></i>
    </div>

    <!-- Контент сообщения -->
    <div class="message-content">
      <!-- Верхняя панель с информацией и действиями -->
      <div class="message-header d-flex align-items-center mb-1">
        <span class="message-role">{{ roleName }}</span>
        <span class="message-time ms-2 text-muted small">{{ formatTime(message.created_at) }}</span>

        <!-- Индикатор загрузки для сообщения ассистента -->
        <template v-if="message.isLoading">
          <div class="ms-2">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
              <span class="visually-hidden">Загрузка...</span>
            </div>
          </div>
        </template>

        <!-- Действия для сообщения -->
        <div
          v-if="!message.isLoading && message.role !== 'system'"
          class="message-actions ms-auto"
        >
          <button
            class="btn btn-sm btn-link p-0 me-2"
            @click="copyToClipboard"
            title="Копировать"
          >
            <i class="bi bi-clipboard"></i>
          </button>

          <button
            v-if="message.role === 'user'"
            class="btn btn-sm btn-link p-0 me-2"
            @click="editMessage"
            title="Редактировать"
          >
            <i class="bi bi-pencil"></i>
          </button>

          <button
            v-if="message.role === 'assistant'"
            class="btn btn-sm btn-link p-0 me-2"
            @click="saveAsPrompt"
            title="Сохранить как промпт"
          >
            <i class="bi bi-bookmark"></i>
          </button>

          <button
            v-if="message.role === 'assistant'"
            class="btn btn-sm btn-link p-0"
            @click="regenerateMessage"
            title="Перегенерировать"
          >
            <i class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
      </div>

      <!-- Текст сообщения с форматированием -->
      <div
        v-if="message.isLoading && message.content.trim() === ''"
        class="message-text message-text-loading"
      >
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>

        <button
          v-if="isStreamingMode"
          class="btn btn-sm btn-danger stop-generation-btn ms-3"
          @click="stopGeneration"
          title="Остановить генерацию"
        >
          <i class="bi bi-stop-fill"></i> Остановить
        </button>
      </div>
      <div
        v-else
        class="message-text"
        v-html="formattedContent"
      ></div>

      <!-- Метаданные для сообщений ассистента -->
      <div
        v-if="message.role === 'assistant' && messageTokens && !message.isLoading"
        class="message-meta mt-2 small text-muted"
      >
        <span>{{ messageTokens }} токенов</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, getCurrentInstance } from 'vue';

// Пропсы с улучшенной типизацией и значениями по умолчанию
const props = defineProps({
  message: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      role: 'system',
      content: '',
      created_at: new Date().toISOString(),
      isLoading: false
    })
  },
  model: {
    type: [String, Number],
    default: ''
  },
  isStreamingMode: Boolean
});

// Мемоизированные вычисляемые свойства
const avatarIcon = computed(() => {
  const roleIcons = {
    'user': 'bi-person-circle',
    'assistant': String(props.model).includes('gpt') ? 'bi-stars' : 'bi-robot',
    'system': 'bi-gear'
  };

  return roleIcons[props.message?.role] || 'bi-chat';
});

const roleName = computed(() => {
  const roleNames = {
    'user': 'Вы',
    'assistant': 'Ассистент',
    'system': 'Система'
  };

  return roleNames[props.message?.role] || 'Неизвестно';
});

const formattedContent = computed(() => {
  const content = props.message?.content || '';

  return content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
    .replace(/\n/g, '<br>');
});

const messageTokens = computed(() => {
  const {
    tokens_total,
    tokens,
    tokens_input,
    tokens_output
  } = props.message || {};

  return tokens_total
    || tokens
    || ((tokens_input || 0) + (tokens_output || 0))
    || null;
});

// Функции с перемещением общей логики наверх
const formatTime = (dateString) => {
  if (!dateString) return '';

  try {
    return new Date(dateString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return '';
  }
};

// Emit для остановки генерации
const emit = defineEmits(['stop-generation']);

// Методы с минимальной логикой
const copyToClipboard = () => {
  const content = props.message?.content || '';

  navigator.clipboard.writeText(content)
    .then(() => alert('Текст скопирован в буфер обмена'))
    .catch(err => alert('Не удалось скопировать текст: ' + err.message));
};

const editMessage = () => {
  alert('Функция редактирования будет доступна в ближайшее время');
};

const saveAsPrompt = () => {
  alert('Функция сохранения промпта будет доступна в ближайшее время');
};

const regenerateMessage = () => {
  const parentContext = getCurrentInstance().parent;

  if (parentContext?.regenerateMessage) {
    parentContext.regenerateMessage(props.message.id);
  } else {
    alert('Функция регенерации ответа будет доступна в ближайшее время');
  }
};

const stopGeneration = () => {
  emit('stop-generation', props.message.thread_id);
};
</script>

<style scoped>
/* Основные стили без изменений */
.message-item {
  display: flex;
  margin-bottom: 1.5rem;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-avatar-user {
  background-color: #f8f9fa;
  color: #495057;
}

.message-avatar-assistant {
  background-color: #4361ee;
  color: white;
}

.message-avatar-system {
  background-color: #ffd54f;
  color: #5f4b32;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}

.message-text-loading {
  min-height: 24px;
  display: flex;
  align-items: center;
}

.message-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.message-item:hover .message-actions {
  opacity: 1;
}

.message-meta {
  opacity: 0.7;
}

.btn-link {
  color: #6c757d;
  text-decoration: none;
}

.btn-link:hover {
  color: #4361ee;
}

/* Анимация печатающего индикатора без изменений */
.typing-indicator {
  display: inline-flex;
  align-items: center;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  margin: 0 2px;
  background-color: #4361ee;
  border-radius: 50%;
  display: inline-block;
  opacity: 0.7;
  animation: typing 1s infinite;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
  100% { transform: translateY(0px); }
}
</style>