import api from './api';

export default {
  // Получение списка доступных моделей
  getAvailableModels() {
    return api.get('/model_preferences/available');
  },

  // Получение настроек моделей пользователя
  getModelPreferences() {
    return api.get('/model_preferences/preferences');
  },

  // Получение настроек моделей по умолчанию
  getDefaultModelPreferences() {
    return api.get('/model_preferences/preferences/default');
  },

  // Создание настройки модели
  createModelPreference(preferenceData) {
    return api.post('/model_preferences/preferences', preferenceData);
  },

  // Обновление настройки модели
  updateModelPreference(preferenceId, preferenceData) {
    return api.put(`/model_preferences/preferences/${preferenceId}`, preferenceData);
  },

  // Удаление настройки модели
  deleteModelPreference(preferenceId) {
    return api.delete(`/model_preferences/preferences/${preferenceId}`);
  }
};