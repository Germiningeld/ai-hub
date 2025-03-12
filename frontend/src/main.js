import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'

// Импортируем Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Создаем экземпляр Pinia
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// Глобальная проверка аутентификации перед навигацией
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('auth_token') !== null;
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Если маршрут требует аутентификации, а пользователь не авторизован
    next('/');
  } else if ((to.path === '/login' || to.path === '/register' || to.path === '/') && isAuthenticated) {
    // Если пользователь уже авторизован и пытается перейти на страницу входа/регистрации или главную
    next('/chat');
  } else {
    // В остальных случаях разрешаем переход
    next();
  }
});

// Создаем и монтируем приложение
const app = createApp(App);
app.use(pinia);
app.use(router);
app.mount('#app')