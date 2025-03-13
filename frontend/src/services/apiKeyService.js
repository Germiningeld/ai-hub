import api from './api';

class ApiKeyService {
  /**
   * Получение списка API ключей пользователя
   * @returns {Promise} - Промис с результатом запроса
   */
  async getApiKeys() {
    try {
      return await api.get('/api-keys/');
    } catch (error) {
      throw this.handleError(error, 'Ошибка при получении списка API ключей');
    }
  }
  
  /**
   * Создание нового API ключа
   * @param {Object} keyData - Данные для создания ключа
   * @param {string} keyData.provider - Провайдер (openai, anthropic и т.д.)
   * @param {string} keyData.api_key - API ключ
   * @param {string} keyData.name - Название ключа (опционально)
   * @param {boolean} keyData.is_active - Активен ли ключ
   * @returns {Promise} - Промис с результатом запроса
   */
  async createApiKey(keyData) {
    try {
      return await api.post('/api-keys/', keyData);
    } catch (error) {
      throw this.handleError(error, 'Ошибка при создании API ключа');
    }
  }
  
  /**
   * Обновление API ключа
   * @param {number} keyId - ID ключа
   * @param {Object} keyData - Данные для обновления
   * @returns {Promise} - Промис с результатом запроса
   */
  async updateApiKey(keyId, keyData) {
    try {
      return await api.put(`/api-keys/${keyId}`, keyData);
    } catch (error) {
      throw this.handleError(error, 'Ошибка при обновлении API ключа');
    }
  }
  
  /**
   * Удаление API ключа
   * @param {number} keyId - ID ключа
   * @returns {Promise} - Промис с результатом запроса
   */
  async deleteApiKey(keyId) {
    try {
      return await api.delete(`/api-keys/${keyId}`);
    } catch (error) {
      throw this.handleError(error, 'Ошибка при удалении API ключа');
    }
  }
  
  /**
   * Проверка валидности API ключа
   * @param {string} provider - Провайдер
   * @param {string} apiKey - API ключ для проверки
   * @returns {Promise<boolean>} - Промис с результатом проверки
   */
  async validateApiKey(provider, apiKey) {
    try {
      const response = await api.post('/api-keys/validate', {
        provider,
        api_key: apiKey
      });
      
      return response.data.valid === true;
    } catch (error) {
      console.error('Error validating API key:', error);
      return false;
    }
  }
  
  /**
   * Получение списка доступных провайдеров
   * @returns {Array} - Массив объектов провайдеров
   */
  getAvailableProviders() {
    return [
      { 
        id: 'openai', 
        name: 'OpenAI (ChatGPT)', 
        description: 'Доступ к GPT-3.5-Turbo, GPT-4, GPT-4o и другим моделям',
        url: 'https://platform.openai.com/api-keys' 
      },
      { 
        id: 'anthropic', 
        name: 'Anthropic (Claude)', 
        description: 'Доступ к Claude 3 (Haiku, Sonnet, Opus)',
        url: 'https://console.anthropic.com/keys' 
      }
    ];
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
      if (error.response.data && error.response.data.error_message) {
        errorMessage = error.response.data.error_message;
      } else if (error.response.status === 401) {
        errorMessage = 'Необходима авторизация';
      } else if (error.response.status === 403) {
        errorMessage = 'Недостаточно прав для выполнения операции';
      } else if (error.response.status === 404) {
        errorMessage = 'API ключ не найден';
      }
    } else if (error.request) {
      errorMessage = 'Сервер не отвечает. Проверьте подключение к интернету.';
    }
    
    const customError = new Error(errorMessage);
    customError.originalError = error;
    return customError;
  }
}

export default new ApiKeyService();