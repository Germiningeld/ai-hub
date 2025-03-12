<template>
    <div class="login-view">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-md-6 col-lg-5">
            <div class="card shadow-sm mt-5">
              <div class="card-body p-4">
                <div class="text-center mb-4">
                  <h2 class="fw-bold">Вход в AIHub</h2>
                  <p class="text-muted">
                    Войдите в систему для доступа к вашему аккаунту
                  </p>
                </div>
                
                <div v-if="registrationSuccess" class="alert alert-success" role="alert">
                  Регистрация прошла успешно! Теперь вы можете войти в систему.
                </div>
                
                <form @submit.prevent="handleLogin">
                  <div v-if="authStore.error" class="alert alert-danger" role="alert">
                    {{ authStore.error }}
                  </div>
                  
                  <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input 
                      type="email" 
                      id="email" 
                      v-model="email" 
                      class="form-control" 
                      placeholder="ваш@email.com" 
                      required
                    >
                  </div>
                  
                  <div class="mb-4">
                    <label for="password" class="form-label">Пароль</label>
                    <input 
                      type="password" 
                      id="password" 
                      v-model="password" 
                      class="form-control" 
                      placeholder="Введите пароль" 
                      required
                    >
                  </div>
                  
                  <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary btn-lg" :disabled="authStore.isLoading">
                      <span v-if="authStore.isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      {{ authStore.isLoading ? 'Выполняется вход...' : 'Войти' }}
                    </button>
                  </div>
                </form>
                
                <div class="text-center mt-4">
                  <p>
                    Еще нет аккаунта? 
                    <router-link to="/register" class="fw-bold text-decoration-none">Зарегистрироваться</router-link>
                  </p>
                </div>
              </div>
            </div>
            
            <div class="text-center mt-3">
              <router-link to="/" class="text-decoration-none">
                <i class="bi bi-arrow-left me-1"></i> Вернуться на главную
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  
  const router = useRouter();
  const route = useRoute();
  const authStore = useAuthStore();
  
  const email = ref('');
  const password = ref('');
  const registrationSuccess = ref(false);
  
  // Очищаем ошибки при монтировании компонента
  onMounted(() => {
    authStore.clearError();
    
    // Проверяем, был ли пользователь перенаправлен со страницы регистрации
    if (route.query.registered === 'success') {
      registrationSuccess.value = true;
      // Заполняем email, если он был передан
      if (route.query.email) {
        email.value = route.query.email;
      }
    }
  });
  
  const handleLogin = async () => {
    const success = await authStore.login(email.value, password.value);
    
    if (success) {
      // Перенаправляем на страницу чата после успешной авторизации
      router.push('/chat');
    }
  };
  </script>
  
  <style scoped>
  .login-view {
    min-height: 100vh;
    display: flex;
    align-items: center;
    background-color: #f8f9fa;
    padding: 2rem 0;
  }
  </style>