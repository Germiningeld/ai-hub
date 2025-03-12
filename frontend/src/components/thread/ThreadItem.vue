<template>
  <div
    class="thread-item p-3 border-bottom cursor-pointer position-relative"
    :class="{ 'active': isActive, 'pinned': thread.is_pinned }"
    @click="$emit('click')"
    @contextmenu="$emit('context-menu', $event)"
  >
    <div class="d-flex align-items-start">
      <!-- Индикатор модели и категории -->
      <div class="thread-icon me-2 flex-shrink-0" :style="{ 'background-color': categoryColor }">
        <i class="bi" :class="modelIcon"></i>
      </div>

      <!-- Информация о треде -->
      <div class="flex-grow-1 min-width-0 overflow-hidden">
        <!-- Контейнер заголовка и счетчика -->
        <div class="position-relative mb-1">
          <!-- Контейнер для текста заголовка с градиентом -->
          <div class="title-container position-relative overflow-hidden pe-5">
            <div class="title-text fw-bold fs-6 text-nowrap text-truncate">
              <i v-if="thread.is_pinned" class="bi bi-pin-angle me-1 text-primary"></i>
              {{ thread.title }}
            </div>
          </div>
        </div>

        <!-- Превью последнего сообщения -->
        <p class="mb-1 text-truncate-2 small text-muted">
          {{ thread.last_message }}
        </p>

        <!-- Время последнего сообщения -->
        <small class="text-muted d-block">{{ formatDate(thread.last_message_at) }}</small>
      </div>
    </div>

    <!-- Счетчик сообщений (абсолютное позиционирование) -->
    <div class="message-count-container position-absolute top-0 end-0 mt-3 me-3">
      <small class="message-count">{{ thread.message_count }}</small>
    </div>
  </div>
</template>

<script setup>

import { computed } from 'vue';

// Пропсы
const props = defineProps({
  thread: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  }
});

// Эмиты
defineEmits(['click', 'context-menu']);

// Вычисляемые свойства
const categoryColor = computed(() => {
  return props.thread.category?.color || '#6c757d';
});

const modelIcon = computed(() => {
  const modelMap = {
    'gpt-4': 'bi-stars',
    'gpt-4o': 'bi-stars',
    'gpt-3.5-turbo': 'bi-robot',
    'claude-3': 'bi-robot',
    'claude-3-opus': 'bi-robot',
    'claude-3-sonnet': 'bi-robot'
  };
  
  const model = props.thread.model?.toLowerCase() || '';
  
  for (const key in modelMap) {
    if (model.includes(key)) {
      return modelMap[key];
    }
  }
  
  return 'bi-chat';
});

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) {
    // Сегодня - показываем время
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else if (diffInDays === 1) {
    // Вчера
    return 'Вчера';
  } else if (diffInDays < 7) {
    // В пределах недели - показываем день недели
    const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    return days[date.getDay()];
  } else {
    // Более недели назад - показываем дату
    return date.toLocaleDateString();
  }
};
</script>

<style scoped>
.thread-item {
  transition: background-color 0.2s;
}

.thread-item:hover {
  background-color: rgba(67, 97, 238, 0.05);
}

.thread-item.active {
  background-color: rgba(67, 97, 238, 0.1);
  border-left: 3px solid #4361ee;
  padding-left: calc(1rem - 3px) !important;
}

.thread-item.pinned {
  background-color: rgba(67, 97, 238, 0.05);
  border-left: 3px solid #4361ee;
  padding-left: calc(1rem - 3px) !important;
}

.thread-icon {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  min-height: 32px !important;
  flex: 0 0 32px !important;
  border-radius: 50%; /* Меняем на круглую форму как в ChatArea */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.thread-icon .bi {
  color: white;
  font-size: 16px;
}

/* Контейнер для заголовка */
.title-container {
  max-width: 100%;
}

/* Текст заголовка */
.title-text {
  max-width: 100%;
}

/* Улучшаем стиль иконок, как в ChatArea */
.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  padding: 0;
}

/* Обновляем стиль счетчика сообщений */
.message-count {
  color: #6c757d;
  font-size: 0.75rem;
  background-color: rgba(67, 97, 238, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
  min-width: 26px;
  text-align: center;
}

/* Улучшенный стиль для закрепленных тредов */
.thread-item.pinned {
  background-color: rgba(67, 97, 238, 0.05);
  border-left: 3px solid #4361ee;
  padding-left: calc(1rem - 3px) !important;
}

/* Иконка закрепления */
.bi-pin-angle {
  color: #4361ee;
}

/* Улучшенное обрезание текста для двух строк */
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 2.8em;
  word-break: break-word;
  padding-right: 40px;
}

.cursor-pointer {
  cursor: pointer;
}
</style>