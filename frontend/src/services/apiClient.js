import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Добавляем перехватчик запросов для добавления токена аутентификации
apiClient.interceptors.request.use(
  config => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Добавляем перехватчик ответов для обработки ошибок аутентификации
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    const authStore = useAuthStore();
    
    if (error.response && error.response.status === 401) {
      // Если получен ответ 401 (Unauthorized), выходим из системы
      authStore.logout();
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;