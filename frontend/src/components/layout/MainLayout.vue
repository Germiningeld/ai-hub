<template>
  <div class="d-flex">
    <!-- Сайдбар - на десктопе слева -->
    <Sidebar @toggle="updateSidebarState" />
    
    <!-- Основной контент страницы -->
    <div class="flex-grow-1 main-content" :class="{ 'content-collapsed': isSidebarCollapsed }">
      <!-- Мобильная навигация - видна только на маленьких экранах -->
      <Navbar @toggle-sidebar="toggleSidebar" />
      
      <!-- Контент без заголовка -->
      <div class="container-fluid p-0">
        <!-- Слот для контента страницы -->
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './Sidebar.vue';
import Navbar from './Navbar.vue';

const route = useRoute();

// Состояние сайдбара (по умолчанию свернут)
const isSidebarCollapsed = ref(true);

// Загрузка состояния сайдбара из localStorage при монтировании
onMounted(() => {
  const savedState = localStorage.getItem('sidebar_collapsed');
  if (savedState !== null) {
    isSidebarCollapsed.value = JSON.parse(savedState);
  }
});

// Обновление состояния на основе события из Sidebar
const updateSidebarState = (newState) => {
  isSidebarCollapsed.value = newState;
};

// Функция переключения состояния сайдбара для мобильной версии
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
  localStorage.setItem('sidebar_collapsed', JSON.stringify(isSidebarCollapsed.value));
};
</script>

<style scoped>
.main-content {
  min-height: 100vh;
  transition: margin-left 0.3s;
  background-color: #f8f9fa;
  margin-left: 70px; /* По умолчанию свернутый сайдбар */
}

.content-collapsed {
  margin-left: 70px;
}

/* На десктопе сдвигаем контент при развернутом сайдбаре */
@media (min-width: 992px) {
  .main-content:not(.content-collapsed) {
    margin-left: 250px;
  }
}

/* Адаптация для мобильных устройств */
@media (max-width: 991.98px) {
  .main-content, 
  .content-collapsed {
    margin-left: 0;
  }
}
</style>