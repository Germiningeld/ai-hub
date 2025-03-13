import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Layouts
import MainLayout from '@/layouts/MainLayout.vue';

// Views
import LoginView from '@/views/LoginView.vue';
import ChatView from '@/views/ChatView.vue';
import ThreadDetailView from '@/views/ThreadDetailView.vue';
import PromptsView from '@/views/PromptsView.vue';
import AnalyticsView from '@/views/AnalyticsView.vue';
import SettingsView from '@/views/SettingsView.vue';
import ApiKeysSettingsView from '@/views/settings/ApiKeysSettingsView.vue';
import ModelSettingsView from '@/views/settings/ModelSettingsView.vue';
import ProfileSettingsView from '@/views/settings/ProfileSettingsView.vue';
import UISettingsView from '@/views/settings/UISettingsView.vue';

const routes = [
  {
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/chat',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'chat',
        component: ChatView
      },
      {
        path: ':id',
        name: 'thread-detail',
        component: ThreadDetailView,
        props: true
      }
    ]
  },
  {
    path: '/prompts',
    name: 'prompts',
    component: () => import('@/views/PromptsView.vue'),
    meta: { requiresAuth: true, layout: MainLayout }
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('@/views/AnalyticsView.vue'),
    meta: { requiresAuth: true, layout: MainLayout }
  },
  {
    path: '/settings',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'settings',
        redirect: '/settings/profile'
      },
      {
        path: 'profile',
        name: 'profile-settings',
        component: ProfileSettingsView
      },
      {
        path: 'api-keys',
        name: 'api-keys-settings',
        component: ApiKeysSettingsView
      },
      {
        path: 'models',
        name: 'model-settings',
        component: ModelSettingsView
      },
      {
        path: 'ui',
        name: 'ui-settings',
        component: UISettingsView
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/chat'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Защита маршрутов
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  // Проверяем, требуется ли аутентификация для маршрута
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  if (requiresAuth && !authStore.isLoggedIn) {
    // Если требуется аутентификация, но пользователь не авторизован
    next('/login');
  } else if (to.path === '/login' && authStore.isLoggedIn) {
    // Если пользователь уже авторизован и пытается перейти на страницу логина
    next('/chat');
  } else {
    // В остальных случаях разрешаем переход
    next();
  }
});

export default router;