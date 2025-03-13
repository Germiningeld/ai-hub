import axios from 'axios';

// Получаем базовый URL API из переменных окружения или используем значение по умолчанию
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';

// Создаем экземпляр axios с базовыми настройками
const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'), // 30 секунд по умолчанию
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// Интерцептор запросов для добавления токена авторизации
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Интерцептор ответов для обработки ошибок
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // Глобальная обработка ошибок
    console.error('API Error:', error);
    
    // Обработка ошибок авторизации (401)
    if (error.response && error.response.status === 401) {
      // Если токен недействителен, удаляем его и перенаправляем на страницу логина
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    
    // Обработка ошибки превышения таймаута
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    }
    
    // Обработка ошибки сети
    if (!error.response) {
      console.error('Network error');
    }
    
    return Promise.reject(error);
  }
);

// Метод для добавления глобальных параметров запроса
export const addGlobalParam = (key, value) => {
  apiClient.defaults.params = {
    ...apiClient.defaults.params,
    [key]: value,
  };
};

// Метод для установки/обновления заголовка
export const setHeader = (key, value) => {
  apiClient.defaults.headers.common[key] = value;
};

// Полезные методы для работы с API
export const api = {
  /**
   * Выполнить GET запрос
   * @param {string} url - URL запроса
   * @param {Object} params - Параметры запроса
   * @param {Object} config - Дополнительная конфигурация
   * @returns {Promise} - Промис с результатом запроса
   */
  get: (url, params = {}, config = {}) => {
    return apiClient.get(url, { params, ...config });
  },
  
  /**
   * Выполнить POST запрос
   * @param {string} url - URL запроса
   * @param {Object} data - Данные запроса
   * @param {Object} config - Дополнительная конфигурация
   * @returns {Promise} - Промис с результатом запроса
   */
  post: (url, data = {}, config = {}) => {
    return apiClient.post(url, data, config);
  },
  
  /**
   * Выполнить PUT запрос
   * @param {string} url - URL запроса
   * @param {Object} data - Данные запроса
   * @param {Object} config - Дополнительная конфигурация
   * @returns {Promise} - Промис с результатом запроса
   */
  put: (url, data = {}, config = {}) => {
    return apiClient.put(url, data, config);
  },
  
  /**
   * Выполнить DELETE запрос
   * @param {string} url - URL запроса
   * @param {Object} config - Дополнительная конфигурация
   * @returns {Promise} - Промис с результатом запроса
   */
  delete: (url, config = {}) => {
    return apiClient.delete(url, config);
  },
  
  /**
   * Создать EventSource для потоковой передачи данных
   * @param {string} url - URL запроса
   * @param {Object} params - Параметры запроса
   * @returns {EventSource} - EventSource объект
   */
  createEventSource: (url, params = {}) => {
    const token = localStorage.getItem('auth_token');
    const urlObj = new URL(`${apiBaseUrl}${url}`, window.location.origin);
    
    // Добавляем токен авторизации в параметры URL
    if (token) {
      urlObj.searchParams.append('token', token);
    }
    
    // Добавляем остальные параметры
    Object.entries(params).forEach(([key, value]) => {
      urlObj.searchParams.append(key, value);
    });
    
    return new EventSource(urlObj.toString());
  }
};

export default apiClient;