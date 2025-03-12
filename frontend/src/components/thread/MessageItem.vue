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

      <!-- Текст сообщения с форматированием markdown (в реальности понадобится markdown-парсер) -->
      <div class="message-text" v-html="formattedContent"></div>

      <!-- Метаданные для сообщений ассистента -->
      <div v-if="message.role === 'assistant' && (message.tokens || message.cost)" class="message-meta mt-2 small text-muted">
        <span v-if="message.tokens">{{ message.tokens }} токенов</span>
        <span v-if="message.tokens && message.cost"> · </span>
        <span v-if="message.cost">{{ formatCost(message.cost) }}</span>
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
    required: true
  },
  model: {
    type: String,
    default: 'gpt-4o'
  }
});

// Определение иконки аватара в зависимости от роли
const avatarIcon = computed(() => {
  const icons = {
    'user': 'bi-person-circle',
    'assistant': props.model.includes('gpt') ? 'bi-stars' : 'bi-robot',
    'system': 'bi-gear'
  };
  return icons[props.message.role] || 'bi-chat';
});

// Определение отображаемого имени роли
const roleName = computed(() => {
  const names = {
    'user': 'Вы',
    'assistant': 'Ассистент',
    'system': 'Система'
  };
  return names[props.message.role] || 'Неизвестно';
});

// Форматированное содержимое (в реальном приложении здесь будет парсинг Markdown)
const formattedContent = computed(() => {
  // Заменяем переносы строк на <br> для простого форматирования
  // В реальном приложении здесь будет полноценный Markdown-парсинг
  return props.message.content.replace(/\n/g, '<br>');
});

// Форматирование времени
const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Форматирование стоимости
const formatCost = (cost) => {
  return `$${cost.toFixed(4)}`;
};

// Копирование текста сообщения в буфер обмена
const copyToClipboard = () => {
  navigator.clipboard.writeText(props.message.content)
    .then(() => {
      alert('Текст скопирован в буфер обмена');
    })
    .catch(err => {
      console.error('Ошибка при копировании текста:', err);
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