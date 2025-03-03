<template>
    <header class="header">
      <div class="header-left">
        <slot name="left"></slot>
      </div>
      <div class="header-center">
        <h2 class="page-title">{{ pageTitle }}</h2>
      </div>
      <div class="header-right">
        <ThemeToggle />
        <slot name="right"></slot>
      </div>
    </header>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { useRoute } from 'vue-router';
  import ThemeToggle from '@/components/common/ThemeToggle.vue';
  
  const route = useRoute();
  
  const pageTitle = computed(() => {
    const titles = {
      '/chat': 'Чат',
      '/prompts': 'Библиотека промптов',
      '/analytics': 'Аналитика использования',
      '/settings': 'Настройки'
    };
    
    return titles[route.path] || '';
  });
  </script>
  
  <style scoped>
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    background-color: var(--background-color);
  }
  
  .header-left,
  .header-right {
    display: flex;
    align-items: center;
  }
  
  .page-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
  }
  </style>