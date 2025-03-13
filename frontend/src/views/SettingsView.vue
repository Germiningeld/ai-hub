<template>
    <div class="d-flex flex-row align-self-stretch h-100">
      <!-- Сайдбар -->
      <Sidebar @toggle="updateSidebarState" />
  
      <!-- Основной контент -->
      <div class="flex-grow-1 main-content h-100  overflow-y-auto">
        <div class="p-4 ">
          <h2 class="mb-4">Настройки</h2>
          
          <!-- Табы навигации -->
          <ul class="nav nav-tabs mb-4">
            <li class="nav-item">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'api-keys' }"
                @click="activeTab = 'api-keys'"
              >
                <i class="bi bi-key me-2"></i>API ключи
              </button>
            </li>
            <li class="nav-item">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'models' }"
                @click="activeTab = 'models'"
              >
                <i class="bi bi-robot me-2"></i>Модели
              </button>
            </li>
            <li class="nav-item">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'profile' }"
                @click="activeTab = 'profile'"
              >
                <i class="bi bi-person me-2"></i>Профиль
              </button>
            </li>
            <li class="nav-item">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'interface' }"
                @click="activeTab = 'interface'"
              >
                <i class="bi bi-sliders me-2"></i>Интерфейс
              </button>
            </li>
          </ul>
          
          <!-- Содержимое активного таба -->
          <div class="tab-content">
            <!-- API ключи -->
            <div v-if="activeTab === 'api-keys'" class="tab-pane active">
              <ApiKeySettings />
            </div>
            
            <!-- Настройки моделей -->
            <div v-if="activeTab === 'models'" class="tab-pane active">
              <ModelSettings />
            </div>
            
            <!-- Настройки профиля -->
            <div v-if="activeTab === 'profile'" class="tab-pane active">
              <ProfileSettings />
            </div>
            
            <!-- Настройки интерфейса -->
            <div v-if="activeTab === 'interface'" class="tab-pane active">
                <InterfaceSettings />
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
    
  <script setup>
  import { ref, onMounted } from 'vue';
  import Sidebar from '@/components/layout/Sidebar.vue';
  import ApiKeySettings from '@/components/settings/ApiKeySettings.vue';
  import ModelSettings from '@/components/settings/ModelSettings.vue';
  import ProfileSettings from '@/components/settings/ProfileSettings.vue';
  import InterfaceSettings from '@/components/settings/InterfaceSettings.vue';
  
  // Активный таб настроек
  const activeTab = ref('api-keys');
  
  // Состояние сайдбара (по умолчанию свернут)
  const isSidebarCollapsed = ref(true);
  
  // При монтировании загружаем состояние сайдбара и устанавливаем активный таб
  onMounted(() => {
    // Загрузка состояния сайдбара из localStorage при монтировании
    const savedState = localStorage.getItem('sidebar_collapsed');
    if (savedState !== null) {
      isSidebarCollapsed.value = JSON.parse(savedState);
    }
    
    // Устанавливаем таб из URL параметра, если есть
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab');
    if (tab && ['api-keys', 'models', 'profile', 'interface'].includes(tab)) {
      activeTab.value = tab;
    }
  });
  
  // Обновление состояния сайдбара на основе события из Sidebar
  const updateSidebarState = (newState) => {
    isSidebarCollapsed.value = newState;
    localStorage.setItem('sidebar_collapsed', JSON.stringify(newState));
  };
  </script>
    
  <style scoped>
  .main-content {
    transition: margin-left 0.3s;
    background-color: #f8f9fa;
  }
  
  .nav-tabs .nav-link {
    color: #495057;
    cursor: pointer;
  }
  
  .nav-tabs .nav-link.active {
    color: #4361ee;
    border-bottom-color: #4361ee;
  }
  
  .tab-pane {
    padding: 1rem 0;
  }
  </style>