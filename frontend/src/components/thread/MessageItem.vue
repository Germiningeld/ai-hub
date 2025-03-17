<template>
  <div
    class="message-item"
    :class="{
      'message-user': message.role === 'user',
      'message-assistant': message.role === 'assistant',
      'message-system': message.role === 'system'
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

        <!-- Действия для сообщения (видимы при наведении) -->
        <div class="message-actions ms-auto" v-if="message.role !== 'system'">
          <button class="btn btn-sm btn-link p-0 me-2" @click="copyToClipboard">
            <i class="bi bi-clipboard"></i>
          </button>

          <button
            v-if="message.role === 'user'"
            class="btn btn-sm btn-link p-0 me-2"
            @click="editMessage"
          >
            <i class="bi bi-pencil"></i>
          </button>

          <button
            v-if="message.role === 'assistant'"
            class="btn btn-sm btn-link p-0 me-2"
            @click="saveAsPrompt"
          >
            <i class="bi bi-bookmark"></i>
          </button>

          <button
            v-if="message.role === 'assistant'"
            class="btn btn-sm btn-link p-0"
            @click="regenerateMessage"
          >
            <i class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
      </div>

      <!-- Текст сообщения с форматированием -->
      <div class="message-text" v-html="formattedContent"></div>

      <!-- Метаданные для сообщений ассистента (только токены, убираем цену) -->
      <div 
        v-if="message.role === 'assistant' && messageTokens" 
        class="message-meta mt-2 small text-muted"
      >
        <span>{{ messageTokens }} токенов</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue';

// Пропсы
const props = defineProps({
  message: {
    type: Object,
    required: true,
    default: () => ({
      id: 'default',
      role: 'system',
      content: '',
      created_at: new Date().toISOString()
    })
  },
  model: {
    type: [String, Number], // Поддерживаем как строку, так и число
    default: ''
  }
});

// Определение иконки аватара в зависимости от роли
const avatarIcon = computed(() => {
  const role = props.message?.role || 'system';
  const model = String(props.model || ''); // Преобразуем в строку
  
  const icons = {
    'user': 'bi-person-circle',
    'assistant': typeof model === 'string' && model.includes('gpt') ? 'bi-stars' : 'bi-robot',
    'system': 'bi-gear'
  };
  
  return icons[role] || 'bi-chat';
});

// Определение отображаемого имени роли
const roleName = computed(() => {
  const role = props.message?.role || 'system';
  
  const names = {
    'user': 'Вы',
    'assistant': 'Ассистент',
    'system': 'Система'
  };
  
  return names[role] || 'Неизвестно';
});

// Форматированное содержимое (обработка текста для отображения)
const formattedContent = computed(() => {
  const content = props.message?.content || '';
  
  // Базовая обработка переносов строк
  return content.replace(/\n/g, '<br>');
});

// Получение токенов из разных полей модели
const messageTokens = computed(() => {
  const msg = props.message || {};
  
  // Пробуем получить токены из разных полей модели
  if (msg.tokens_total) {
    return msg.tokens_total;
  } else if (msg.tokens) {
    return msg.tokens;
  } else if (msg.tokens_input || msg.tokens_output) {
    return (msg.tokens_input || 0) + (msg.tokens_output || 0);
  }
  return null;
});

// Форматирование времени
const formatTime = (dateString) => {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    console.error('Ошибка при форматировании времени:', e);
    return '';
  }
};

// Копирование текста сообщения в буфер обмена
const copyToClipboard = () => {
  const content = props.message?.content || '';
  
  navigator.clipboard.writeText(content)
    .then(() => {
      alert('Текст скопирован в буфер обмена');
    })
    .catch(err => {
      console.error('Ошибка при копировании текста:', err);
      alert('Не удалось скопировать текст: ' + err.message);
    });
};

// Редактирование сообщения (только для пользовательских сообщений)
const editMessage = () => {
  // Здесь будет логика редактирования сообщения
  alert('Функция редактирования будет доступна в ближайшее время');
};

// Сохранение ответа ассистента как промпта
const saveAsPrompt = () => {
  // Здесь будет логика сохранения в библиотеку промптов
  alert('Функция сохранения промпта будет доступна в ближайшее время');
};

// Повторная генерация ответа ассистента
const regenerateMessage = () => {
  // Здесь будет логика регенерации ответа
  alert('Функция регенерации ответа будет доступна в ближайшее время');
};
</script>

<style scoped>
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

/* Стилизация кнопок действий */
.btn-link {
  color: #6c757d;
  text-decoration: none;
}

.btn-link:hover {
  color: #4361ee;
}
</style>