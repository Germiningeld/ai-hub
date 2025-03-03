<template>
    <div class="settings-container">
      <div class="settings-sidebar">
        <nav class="settings-nav">
          <router-link 
            to="/settings/profile" 
            class="settings-nav-item" 
            active-class="active"
          >
            Профиль
          </router-link>
          <router-link 
            to="/settings/api-keys" 
            class="settings-nav-item" 
            active-class="active"
          >
            API ключи
          </router-link>
          <router-link 
            to="/settings/models" 
            class="settings-nav-item" 
            active-class="active"
          >
            Настройки моделей
          </router-link>
          <router-link 
            to="/settings/ui" 
            class="settings-nav-item" 
            active-class="active"
          >
            Настройки интерфейса
          </router-link>
        </nav>
      </div>
      
      <div class="settings-content">
        <router-view />
      </div>
    </div>
  </template>
  
  <style scoped>
  .settings-container {
    display: flex;
    height: 100%;
  }
  
  .settings-sidebar {
    width: 250px;
    border-right: 1px solid var(--border-color);
    padding: 1.5rem 0;
  }
  
  .settings-nav {
    display: flex;
    flex-direction: column;
  }
  
  .settings-nav-item {
    padding: 0.75rem 1.5rem;
    color: var(--text-color);
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: background-color 0.2s;
  }
  
  .settings-nav-item:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .settings-nav-item.active {
    background-color: rgba(59, 130, 246, 0.1);
    border-left-color: var(--primary-color);
    color: var(--primary-color);
  }
  
  .settings-content {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
  }
  
  @media (max-width: 768px) {
    .settings-container {
      flex-direction: column;
    }
  
    .settings-sidebar {
      width: 100%;
      border-right: none;
      border-bottom: 1px solid var(--border-color);
      padding: 1rem 0;
    }
  
    .settings-nav {
      flex-direction: row;
      overflow-x: auto;
      padding: 0 1rem;
    }
  
    .settings-nav-item {
      border-left: none;
      border-bottom: 3px solid transparent;
      white-space: nowrap;
    }
  
    .settings-nav-item.active {
      border-left-color: transparent;
      border-bottom-color: var(--primary-color);
    }
  }
  </style>