<template>
    <div class="app">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </div>
  </template>
  
  <script setup>
  import { onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  
  const router = useRouter();
  const authStore = useAuthStore();
  
  onMounted(async () => {
    // Проверяем, авторизован ли пользователь
    if (authStore.isLoggedIn) {
      try {
        await authStore.fetchUserInfo();
      } catch (error) {
        // Если токен недействителен, перенаправляем на логин
        authStore.logout();
        router.push('/login');
      }
    }
  });
  </script>
  
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  :root {
    --primary-color: #3b82f6;
    --secondary-color: #6366f1;
    --background-color: #ffffff;
    --text-color: #1f2937;
    --border-color: #e5e7eb;
  }
  
  .dark {
    --primary-color: #60a5fa;
    --secondary-color: #818cf8;
    --background-color: #111827;
    --text-color: #f9fafb;
    --border-color: #374151;
  }
  
  body {
    font-family: 'Inter', sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
    margin: 0;
    padding: 0;
    transition: background-color 0.3s ease;
  }
  
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  </style>