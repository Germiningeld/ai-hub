<template>
    <div 
      class="thread-item" 
      :class="{ 'active': active, 'archived': thread.is_archived }"
      @click="$emit('click')"
    >
      <div class="thread-content">
        <div class="thread-title">
          <span v-if="thread.is_pinned" class="pin-icon" title="Закрепленный тред">📌</span>
          {{ thread.title }}
        </div>
        <div class="thread-meta">
          <span class="thread-date">{{ formattedDate }}</span>
          <span v-if="thread.category" class="thread-category" :style="{ backgroundColor: thread.category.color + '33' }">
            {{ thread.category.name }}
          </span>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import dayjs from 'dayjs';
  
  const props = defineProps({
    thread: {
      type: Object,
      required: true
    },
    active: {
      type: Boolean,
      default: false
    }
  });
  
  const formattedDate = computed(() => {
    return thread.value && thread.value.last_message_at 
      ? dayjs(thread.value.last_message_at).format('DD.MM.YYYY HH:mm') 
      : '';
  });
  
  // Для предотвращения ошибки при доступе к thread
  const thread = computed(() => props.thread || {});
  </script>
  
  <style scoped>
  .thread-item {
    padding: 0.75rem;
    border-radius: 0.25rem;
    cursor: pointer;
    transition: background-color 0.2s;
    margin-bottom: 0.5rem;
    border-left: 3px solid transparent;
  }
  
  .thread-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .thread-item.active {
    background-color: rgba(59, 130, 246, 0.1);
    border-left-color: var(--primary-color);
  }
  
  .thread-item.archived {
    opacity: 0.7;
  }
  
  .thread-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .thread-title {
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }
  
  .pin-icon {
    font-size: 0.75rem;
  }
  
  .thread-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #6b7280;
  }
  
  .thread-category {
    padding: 0.125rem 0.375rem;
    border-radius: 9999px;
    font-size: 0.65rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100px;
  }
  </style>