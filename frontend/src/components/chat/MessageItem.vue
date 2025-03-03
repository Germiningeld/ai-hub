<template>
    <div class="message" :class="messageClass">
      <div class="message-header">
        <div class="message-role">{{ displayRole }}</div>
        <div class="message-time">{{ formattedTime }}</div>
      </div>
      
      <div class="message-content" v-html="formattedContent"></div>
      
      <div v-if="showMetadata && message.meta_data" class="message-metadata">
        <div class="token-info">
          <span>Токены: {{ message.tokens || message.meta_data.tokens?.total_tokens || 'N/A' }}</span>
          <span v-if="message.meta_data.cost">Стоимость: ${{ message.meta_data.cost.toFixed(5) }}</span>
        </div>
        <div v-if="message.meta_data.with_context !== undefined" class="context-info">
          <span>{{ message.meta_data.with_context ? 'С контекстом' : 'Без контекста' }}</span>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import dayjs from 'dayjs';
  import { marked } from 'marked';
  import 'prismjs';
  import 'prismjs/components/prism-javascript';
  import 'prismjs/components/prism-python';
  import 'prismjs/components/prism-bash';
  import 'prismjs/components/prism-json';
  import 'prismjs/themes/prism.css';
  
  const props = defineProps({
    message: {
      type: Object,
      required: true
    },
    showMetadata: {
      type: Boolean,
      default: true
    }
  });
  
  // Настройка marked для использования Prism для подсветки синтаксиса
  marked.setOptions({
    highlight: function(code, lang) {
      if (Prism.languages[lang]) {
        return Prism.highlight(code, Prism.languages[lang], lang);
      }
      return code;
    }
  });
  
  const messageClass = computed(() => {
    return `message-${props.message.role}`;
  });
  
  const displayRole = computed(() => {
    const roles = {
      'system': 'Система',
      'user': 'Вы',
      'assistant': 'Ассистент'
    };
    
    return roles[props.message.role] || props.message.role;
  });
  
  const formattedTime = computed(() => {
    return dayjs(props.message.created_at).format('DD.MM.YYYY HH:mm');
  });
  
  const formattedContent = computed(() => {
    if (!props.message.content) return '';
    
    // Используем marked для рендеринга Markdown, если сообщение от ассистента
    if (props.message.role === 'assistant') {
      return marked(props.message.content);
    }
    
    // Для сообщений пользователя и системы просто заменяем переносы строк на <br>
    return props.message.content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
      .replace(/\n/g, '<br>');
  });
  </script>
  
  <style scoped>
  .message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .message-user {
    background-color: rgba(59, 130, 246, 0.1);
  }
  
  .message-assistant {
    background-color: var(--background-color);
    border: 1px solid var(--border-color);
  }
  
  .message-system {
    background-color: rgba(107, 114, 128, 0.1);
    font-style: italic;
  }
  
  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }
  
  .message-role {
    font-weight: 600;
  }
  
  .message-time {
    color: #6b7280;
  }
  
  .message-content {
    white-space: pre-wrap;
    line-height: 1.5;
  }
  
  .message-content :deep(pre) {
    background-color: #f3f4f6;
    padding: 1rem;
    border-radius: 0.25rem;
    overflow-x: auto;
    margin: 1rem 0;
  }
  
  .dark .message-content :deep(pre) {
    background-color: #374151;
  }
  
  .message-content :deep(code) {
    font-family: 'Courier New', Courier, monospace;
  }
  
  .message-content :deep(p) {
    margin: 0.75rem 0;
  }
  
  .message-content :deep(ul), .message-content :deep(ol) {
    margin: 0.75rem 0;
    padding-left: 1.5rem;
  }
  
  .message-content :deep(h1), .message-content :deep(h2), .message-content :deep(h3),
  .message-content :deep(h4), .message-content :deep(h5), .message-content :deep(h6) {
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  .message-metadata {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px dashed var(--border-color);
    font-size: 0.75rem;
    color: #6b7280;
  }
  
  .token-info {
    display: flex;
    justify-content: space-between;
  }
  
  .context-info {
    margin-top: 0.25rem;
  }
  </style>