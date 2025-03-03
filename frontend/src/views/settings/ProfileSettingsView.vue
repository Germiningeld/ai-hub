<template>
    <div class="profile-settings">
      <h2 class="section-title">Профиль</h2>
      <p class="section-description">
        Управление личной информацией и настройками учетной записи.
      </p>
      
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка данных профиля...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="fetchProfile" class="retry-button">Повторить</button>
      </div>
      
      <form v-else @submit.prevent="updateProfile" class="profile-form">
        <div class="form-section">
          <h3 class="subsection-title">Личная информация</h3>
          
          <div class="form-group">
            <label for="username">Имя пользователя</label>
            <input 
              type="text" 
              id="username" 
              v-model="profileData.username" 
              required
            />
          </div>
          
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              v-model="profileData.email" 
              required
            />
          </div>
        </div>
        
        <div class="form-section">
          <h3 class="subsection-title">Изменение пароля</h3>
          <p class="section-description">
            Оставьте поля пустыми, если не хотите изменять пароль.
          </p>
          
          <div class="form-group">
            <label for="current-password">Текущий пароль</label>
            <input 
              type="password" 
              id="current-password" 
              v-model="passwordData.current_password"
            />
          </div>
          
          <div class="form-group">
            <label for="new-password">Новый пароль</label>
            <input 
              type="password" 
              id="new-password" 
              v-model="passwordData.new_password"
            />
          </div>
          
          <div class="form-group">
            <label for="confirm-password">Подтверждение пароля</label>
            <input 
              type="password" 
              id="confirm-password" 
              v-model="passwordData.confirm_password"
            />
            <p v-if="passwordMismatch" class="error-message">
              Пароли не совпадают
            </p>
          </div>
        </div>
        
        <div class="form-actions">
          <button 
            type="submit" 
            class="save-button" 
            :disabled="saving || passwordMismatch || (passwordData.new_password && !passwordData.current_password)"
          >
            {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
        </div>
        
        <div v-if="updateSuccess" class="success-message">
          Профиль успешно обновлен!
        </div>
        
        <div v-if="updateError" class="error-message">
          {{ updateError }}
        </div>
      </form>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useAuthStore } from '@/stores/auth';
  
  const authStore = useAuthStore();
  
  const loading = ref(true);
  const error = ref(null);
  const saving = ref(false);
  const updateSuccess = ref(false);
  const updateError = ref(null);
  
  const profileData = ref({
    username: '',
    email: ''
  });
  
  const passwordData = ref({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const passwordMismatch = computed(() => {
    if (!passwordData.value.new_password && !passwordData.value.confirm_password) {
      return false;
    }
    return passwordData.value.new_password !== passwordData.value.confirm_password;
  });
  
  const fetchProfile = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const userData = await authStore.fetchUserInfo();
      profileData.value = {
        username: userData.username || '',
        email: userData.email || ''
      };
    } catch (err) {
      error.value = 'Ошибка при загрузке данных профиля. Попробуйте позже.';
      console.error('Error fetching profile:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const updateProfile = async () => {
    if (passwordMismatch.value) return;
    
    saving.value = true;
    updateSuccess.value = false;
    updateError.value = null;
    
    try {
      // Данные для обновления (базовая информация профиля)
      const updateData = {
        username: profileData.value.username,
        email: profileData.value.email
      };
      
      // Добавляем пароль, если он указан
      if (passwordData.value.new_password && passwordData.value.current_password) {
        updateData.password = passwordData.value.new_password;
        updateData.current_password = passwordData.value.current_password;
      }
      
      // Отправляем запрос на обновление
      await authStore.updateUser(updateData);
      
      // Сбрасываем поля пароля
      passwordData.value = {
        current_password: '',
        new_password: '',
        confirm_password: ''
      };
      
      updateSuccess.value = true;
      
      // Скрываем сообщение об успехе через 3 секунды
      setTimeout(() => {
        updateSuccess.value = false;
      }, 3000);
    } catch (err) {
      updateError.value = err.response?.data?.error_message || 'Ошибка при обновлении профиля. Попробуйте позже.';
      console.error('Error updating profile:', err);
    } finally {
      saving.value = false;
    }
  };
  
  onMounted(fetchProfile);
  </script>
  
  <style scoped>
  .profile-settings {
    max-width: 600px;
  }
  
  .section-title {
    margin-top: 0;
    margin-bottom: 0.75rem;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  .section-description {
    margin-bottom: 2rem;
    color: #6b7280;
  }
  
  .subsection-title {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  .form-section {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .form-section:last-of-type {
    border-bottom: none;
  }
  
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input[type="text"],
  input[type="email"],
  input[type="password"] {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .form-actions {
    margin-top: 2rem;
  }
  
  .save-button {
    padding: 0.75rem 1.5rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    font-weight: 500;
    cursor: pointer;
  }
  
  .save-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .success-message {
    margin-top: 1rem;
    padding: 0.75rem;
    background-color: rgba(16, 185, 129, 0.1);
    color: #065f46;
    border-radius: 0.25rem;
  }
  
  .error-message {
    margin-top: 0.5rem;
    color: #b91c1c;
  }
  
  .loading-state, .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
    color: #6b7280;
  }
  
  .loading-spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid var(--primary-color);
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .retry-button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
  }
  </style>