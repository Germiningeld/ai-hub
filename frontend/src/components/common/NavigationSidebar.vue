<template>
    <div class="sidebar" :class="{ 'sidebar-collapsed': collapsed }">
      <div class="sidebar-header">
        <h1 class="logo">AIHub</h1>
        <button class="collapse-btn" @click="toggleCollapse">
          <span v-if="collapsed">›</span>
          <span v-else>‹</span>
        </button>
      </div>
      
      <nav class="nav-menu">
        <router-link to="/chat" class="nav-item" active-class="active">
          <span class="icon">💬</span>
          <span v-if="!collapsed" class="label">Чат</span>
        </router-link>
        
        <router-link to="/prompts" class="nav-item" active-class="active">
          <span class="icon">📝</span>
          <span v-if="!collapsed" class="label">Промпты</span>
        </router-link>
        
        <router-link to="/analytics" class="nav-item" active-class="active">
          <span class="icon">📊</span>
          <span v-if="!collapsed" class="label">Аналитика</span>
        </router-link>
        
        <router-link to="/settings" class="nav-item" active-class="active">
          <span class="icon">⚙️</span>
          <span v-if="!collapsed" class="label">Настройки</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <div v-if="!collapsed" class="user-info">
          <span>{{ user.username }}</span>
        </div>
        <button class="logout-btn" @click="logout">
          <span class="icon">🚪</span>
          <span v-if="!collapsed" class="label">Выйти</span>
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  
  const collapsed = ref(false);
  const authStore = useAuthStore();
  const router = useRouter();
  
  const user = computed(() => authStore.user || {});
  
  const toggleCollapse = () => {
    collapsed.value = !collapsed.value;
  };
  
  const logout = async () => {
    await authStore.logout();
    router.push('/login');
  };
  </script>
  
  <style scoped>
  .sidebar {
    width: 240px;
    background-color: #f3f4f6;
    color: #374151;
    height: 100vh;
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
    overflow: hidden;
  }
  
  .sidebar-collapsed {
    width: 64px;
  }
  
  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .logo {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
    white-space: nowrap;
  }
  
  .collapse-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.5rem;
  }
  
  .nav-menu {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 1rem 0;
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    color: inherit;
    text-decoration: none;
    transition: background-color 0.2s;
  }
  
  .nav-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .nav-item.active {
    background-color: rgba(59, 130, 246, 0.1);
    color: var(--primary-color);
  }
  
  .icon {
    font-size: 1.25rem;
    margin-right: 0.75rem;
  }
  
  .sidebar-collapsed .icon {
    margin-right: 0;
  }
  
  .label {
    white-space: nowrap;
  }
  
  .sidebar-footer {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
  }
  
  .user-info {
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .logout-btn {
    display: flex;
    align-items: center;
    background: none;
    border: none;
    cursor: pointer;
    color: #ef4444;
    padding: 0.5rem;
    width: 100%;
    text-align: left;
  }
  
  @media (max-width: 768px) {
    .sidebar {
      width: 100%;
      height: auto;
    }
    
    .sidebar-collapsed {
      width: 100%;
    }
  }
  </style>