<template>
    <button class="theme-toggle" @click="toggleTheme" title="Переключить тему">
      <span v-if="isDark">☀️</span>
      <span v-else>🌙</span>
    </button>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue';
  
  const isDark = ref(false);
  
  const toggleTheme = () => {
    isDark.value = !isDark.value;
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
    applyTheme();
  };
  
  const applyTheme = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };
  
  onMounted(() => {
    const savedTheme = localStorage.getItem('theme');
    isDark.value = savedTheme === 'dark';
    applyTheme();
  });
  
  watch(isDark, applyTheme);
  </script>
  
  <style scoped>
  .theme-toggle {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0.5rem;
    border-radius: 0.25rem;
    transition: background-color 0.2s;
  }
  
  .theme-toggle:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .dark .theme-toggle:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
  </style>