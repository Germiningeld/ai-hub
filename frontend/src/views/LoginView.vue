<template>
    <div class="login-container">
      <div class="login-form">
        <h1 class="logo">AIHub</h1>
        <h2 class="title">Вход в систему</h2>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              v-model="email" 
              required 
              placeholder="user@example.com"
            />
          </div>
          
          <div class="form-group">
            <label for="password">Пароль</label>
            <input 
              type="password" 
              id="password" 
              v-model="password" 
              required 
              placeholder="••••••••"
            />
          </div>
          
          <button 
            type="submit" 
            class="login-button" 
            :disabled="isLoading"
          >
            {{ isLoading ? 'Вход...' : 'Войти' }}
          </button>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  
  const router = useRouter();
  const authStore = useAuthStore();
  
  const email = ref('');
  const password = ref('');
  const error = ref('');
  const isLoading = ref(false);
  
  const login = async () => {
    error.value = '';
    isLoading.value = true;
    
    try {
      await authStore.login(email.value, password.value);
      router.push('/chat');
    } catch (err) {
      error.value = err.response?.data?.error_message || 'Ошибка при входе. Проверьте email и пароль.';
    } finally {
      isLoading.value = false;
    }
  };
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: var(--background-color);
  }
  
  .login-form {
    width: 100%;
    max-width: 400px;
    padding: 2rem;
    background-color: var(--background-color);
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .logo {
    text-align: center;
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: var(--primary-color);
  }
  
  .title {
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 600;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .login-button {
    width: 100%;
    padding: 0.75rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .login-button:hover {
    background-color: #2563eb;
  }
  
  .login-button:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
  }
  
  .error-message {
    padding: 0.75rem;
    margin-bottom: 1rem;
    background-color: #fee2e2;
    color: #b91c1c;
    border-radius: 0.25rem;
  }
  
  .dark .error-message {
    background-color: #7f1d1d;
    color: #fecaca;
  }
  </style>