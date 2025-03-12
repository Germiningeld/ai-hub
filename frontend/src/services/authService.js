import apiClient from './api';

class AuthService {
  /**
   * Авторизация пользователя
   * @param {string} email - Email пользователя
   * @param {string} password - Пароль пользователя
   * @returns {Promise} - Промис с результатом авторизации
   */
  async login(email, password) {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password
      });
      
      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
      }
      
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Ошибка при входе в систему');
    }
  }
  
  /**
   * Регистрация нового пользователя
   * @param {string} username - Имя пользователя
   * @param {string} email - Email пользователя
   * @param {string} password - Пароль пользователя
   * @returns {Promise} - Промис с результатом регистрации
   */
  async register(username, email, password) {
    try {
      const response = await apiClient.post('/users/', {
        username,
        email,
        password
      });
      
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Ошибка при регистрации');
    }
  }
  
  /**
   * Получение информации о текущем пользователе
   * @returns {Promise} - Промис с информацией о пользователе
   */
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/users/me');
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Ошибка при получении информации о пользователе');
    }
  }
  
  /**
   * Выход из системы
   */
  logout() {
    localStorage.removeItem('auth_token');
  }
  
  /**
   * Проверка, авторизован ли пользователь
   * @returns {boolean} - Результат проверки
   */
  isAuthenticated() {
    return localStorage.getItem('auth_token') !== null;
  }
  
  /**
   * Обработка ошибок API
   * @param {Error} error - Объект ошибки
   * @param {string} defaultMessage - Сообщение по умолчанию
   * @returns {Error} - Обработанная ошибка
   */
  handleError(error, defaultMessage = 'Ошибка при выполнении запроса') {
    let errorMessage = defaultMessage;
    
    if (error.response) {
      // Сервер вернул ошибку
      if (error.response.data && error.response.data.error_message) {
        errorMessage = error.response.data.error_message;
      } else if (error.response.status === 401) {
        errorMessage = 'Необходима авторизация';
      } else if (error.response.status === 403) {
        errorMessage = 'Недостаточно прав для выполнения операции';
      } else if (error.response.status === 404) {
        errorMessage = 'Запрашиваемый ресурс не найден';
      } else if (error.response.status === 422) {
        errorMessage = 'Ошибка валидации данных';
      }
    } else if (error.request) {
      // Запрос не получил ответа
      errorMessage = 'Сервер не отвечает. Проверьте подключение к интернету.';
    }
    
    const customError = new Error(errorMessage);
    customError.originalError = error;
    return customError;
  }
}

export default new AuthService();