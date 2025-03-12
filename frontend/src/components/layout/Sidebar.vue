<template>
  <div
    class="sidebar d-flex flex-column justify-content-between flex-shrink-0"
    :class="{ 'collapsed': isCollapsed }"
    @click="handleSidebarClick"
  >
    <!-- Логотип без кнопки сворачивания -->
    <div class="sidebar-header d-flex align-items-center p-3">
      <div class="logo cursor-pointer" @click.stop="toggleSidebar">
        <img v-if="!isCollapsed" src="@/assets/css/logo.svg" alt="AIHub" height="30">
        <img v-else src="@/assets/css/logo-white.svg" alt="AIHub" height="30">
      </div>
    </div>

    <!-- Навигационное меню -->
    <div class="sidebar-menu">
      <ul class="nav flex-column">
        <li class="nav-item" v-for="item in menuItems" :key="item.path">
          <router-link
            :to="item.path"
            class="nav-link"
            :class="{ active: currentRoute === item.path }"
            :title="item.name"
          >
            <i class="bi" :class="item.icon"></i>
            <span v-if="!isCollapsed">{{ item.name }}</span>
          </router-link>
        </li>
      </ul>
    </div>

    <!-- Нижняя часть сайдбара с выходом -->
    <div class="sidebar-footer">
      <ul class="nav flex-column">
        <li class="nav-item">
          <a href="#" class="nav-link" @click.prevent="logout" :title="'Выход'">
            <i class="bi bi-box-arrow-left"></i>
            <span v-if="!isCollapsed">Выход</span>
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Определяем события
const emit = defineEmits(['toggle']);

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Определяем состояние сайдбара (по умолчанию свернут)
const isCollapsed = ref(true);

// Текущий маршрут
const currentRoute = computed(() => route.path);

// Элементы меню
const menuItems = [
  { name: 'Чат', path: '/chat', icon: 'bi-chat-dots' },
  // { name: 'Библиотека промптов', path: '/prompts', icon: 'bi-collection' },
  // { name: 'Аналитика', path: '/analytics', icon: 'bi-graph-up' },
  { name: 'Библиотека промптов', path: '/', icon: 'bi-collection' },
  { name: 'Аналитика', path: '/', icon: 'bi-graph-up' },
  { name: 'Настройки', path: '/settings', icon: 'bi-gear' },
];

// Загрузка состояния сайдбара из localStorage при монтировании
onMounted(() => {
  const savedState = localStorage.getItem('sidebar_collapsed');
  if (savedState !== null) {
    isCollapsed.value = JSON.parse(savedState);
  }
});

// Сохранение состояния сайдбара в localStorage при изменении
watch(isCollapsed, (newValue) => {
  localStorage.setItem('sidebar_collapsed', JSON.stringify(newValue));
});

// Функция переключения состояния сайдбара
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
  emit('toggle', isCollapsed.value);
};

// Обработчик клика по сайдбару (не по элементам меню)
const handleSidebarClick = (event) => {
  // Проверяем, что клик был по самому сайдбару, а не по элементам меню
  if (event.target === event.currentTarget || event.target.closest('.sidebar-header, .sidebar-menu, .sidebar-footer') === null) {
    toggleSidebar();
  }
};

// Функция выхода
const logout = async () => {
  try {
    await authStore.logout();
    router.push('/login');
  } catch (error) {
    console.error('Ошибка при выходе:', error);
  }
};
</script>
<style scoped>
.sidebar {
  width: 250px;
  background-color: #343a40;
  color: #fff;
  height: 100vh;
  overflow-y: auto;
  transition: width 0.3s;
  z-index: 1030;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 0.8rem 0;
}

.sidebar.collapsed .nav-link i {
  margin-right: 0;
}

.sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
}

.logo {
  cursor: pointer;
}

.sidebar-menu {
  flex-grow: 1;
  overflow-y: auto;
}

.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-link {
  padding: 0.8rem 1rem;
  color: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  transition: all 0.3s;
}

.nav-link i {
  font-size: 1.25rem;
  margin-right: 1rem;
  min-width: 20px;
  text-align: center;
}

.nav-link.active,
.nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.1);
}

/* Адаптивность для маленьких экранов */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .sidebar span {
    display: none;
  }

  .sidebar .nav-item {
    text-align: center;
  }
}

/* На мобильных устройствах сайдбар скрыт по умолчанию */
@media (max-width: 991.98px) {
  .sidebar {
    transform: translateX(-100%);
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
  }
  
  .sidebar.show {
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
}
</style>