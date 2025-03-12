<template>
    <div class="register-view">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-md-6 col-lg-5">
            <div class="card shadow-sm mt-5">
              <div class="card-body p-4">
                <div class="text-center mb-4">
                  <h2 class="fw-bold">Регистрация в AIHub</h2>
                  <p class="text-muted">
                    Создайте аккаунт для доступа к функциям платформы
                  </p>
                </div>
                
                <form @submit.prevent="handleRegister">
                  <div v-if="authStore.error" class="alert alert-danger" role="alert">
                    {{ authStore.error }}
                  </div>
                  
                  <div v-if="formValidationError" class="alert alert-warning" role="alert">
                    {{ formValidationError }}
                  </div>
                  
                  <div class="mb-3">
                    <label for="username" class="form-label">Имя пользователя</label>
                    <input 
                      type="text" 
                      id="username" 
                      v-model="username" 
                      class="form-control" 
                      placeholder="Введите имя пользователя" 
                      required
                      minlength="3"
                    >
                    <div class="form-text">Минимум 3 символа</div>
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
                  
                  <div class="mb-3">
                    <label for="password" class="form-label">Пароль</label>
                    <input 
                      type="password" 
                      id="password" 
                      v-model="password" 
                      class="form-control" 
                      placeholder="Придумайте пароль" 
                      required
                      minlength="8"
                      @input="checkPasswordsMatch"
                    >
                    <div class="form-text">Минимум 8 символов</div>
                  </div>
                  
                  <div class="mb-4">
                    <label for="confirmPassword" class="form-label">Подтверждение пароля</label>
                    <input 
                      type="password" 
                      id="confirmPassword" 
                      v-model="confirmPassword" 
                      class="form-control" 
                      :class="{ 'is-invalid': passwordMismatch, 'is-valid': confirmPassword && !passwordMismatch }"
                      placeholder="Подтвердите пароль" 
                      required
                      @input="checkPasswordsMatch"
                    >
                    <div class="invalid-feedback" v-if="passwordMismatch">
                      Пароли не совпадают
                    </div>
                  </div>
                  
                  <div class="mb-3 form-check">
                    <input 
                      type="checkbox" 
                      class="form-check-input" 
                      id="termsCheck" 
                      v-model="acceptTerms"
                      required
                    >
                    <label class="form-check-label" for="termsCheck">
                      Я согласен с <a href="#" @click.prevent="showTerms">условиями использования</a>
                    </label>
                  </div>
                  
                  <div class="d-grid gap-2">
                    <button 
                      type="submit" 
                      class="btn btn-primary btn-lg" 
                      :disabled="authStore.isLoading || passwordMismatch || !isFormValid"
                    >
                      <span v-if="authStore.isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      {{ authStore.isLoading ? 'Выполняется регистрация...' : 'Зарегистрироваться' }}
                    </button>
                  </div>
                </form>
                
                <div class="text-center mt-4">
                  <p>
                    Уже есть аккаунт? 
                    <router-link to="/login" class="fw-bold text-decoration-none">Войти</router-link>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const acceptTerms = ref(false);
const passwordMismatch = ref(false);
const formValidationError = ref('');

// Очищаем ошибки при монтировании компонента
onMounted(() => {
  authStore.clearError();
  // Убедимся, что состояние загрузки сброшено
  if (authStore.isLoading) {
    authStore.$patch({ loading: false });
  }
});

// Проверка совпадения паролей
const checkPasswordsMatch = () => {
  if (confirmPassword.value && password.value) {
    passwordMismatch.value = password.value !== confirmPassword.value;
  } else {
    passwordMismatch.value = false;
  }
};

// Проверка валидности формы
const isFormValid = computed(() => {
  return username.value.length >= 3 && 
         email.value.includes('@') && 
         password.value.length >= 8 && 
         password.value === confirmPassword.value &&
         acceptTerms.value;
});

// Отладочное свойство для отслеживания состояния формы
const formDebugState = computed(() => {
  return {
    usernameValid: username.value.length >= 3,
    emailValid: email.value.includes('@'),
    passwordValid: password.value.length >= 8,
    passwordsMatch: password.value === confirmPassword.value,
    termsAccepted: acceptTerms.value,
    isFormValid: isFormValid.value,
    passwordMismatch: passwordMismatch.value,
    storeLoading: authStore.isLoading || authStore.loading
  };
});

// Отслеживаем изменения полей формы
watch([username, email, password, confirmPassword, acceptTerms], () => {
  // При изменении любого поля проверяем совпадение паролей
  checkPasswordsMatch();
  
  // Логируем текущее состояние формы для отладки
  console.log('Form state:', formDebugState.value);
});

// Показать условия использования (заглушка)
const showTerms = () => {
  alert('Здесь будут отображены условия использования сервиса.');
};

const handleRegister = async () => {
  // Очищаем ошибки перед проверкой
  formValidationError.value = '';
  
  // Еще раз проверяем валидность перед отправкой
  if (!isFormValid.value) {
    if (password.value !== confirmPassword.value) {
      formValidationError.value = 'Пароли не совпадают';
    } else if (!acceptTerms.value) {
      formValidationError.value = 'Необходимо принять условия использования';
    } else if (username.value.length < 3) {
      formValidationError.value = 'Имя пользователя должно содержать минимум 3 символа';
    } else if (!email.value.includes('@')) {
      formValidationError.value = 'Введите корректный email';
    } else if (password.value.length < 8) {
      formValidationError.value = 'Пароль должен содержать минимум 8 символов';
    } else {
      formValidationError.value = 'Пожалуйста, заполните все поля корректно';
    }
    return;
  }
  
  try {
    const success = await authStore.register(username.value, email.value, password.value);
    
    if (success) {
      // Переход на страницу входа после успешной регистрации
      router.push({
        path: '/login',
        query: { registered: 'success', email: email.value }
      });
    }
  } catch (error) {
    formValidationError.value = 'Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.';
    console.error('Registration error:', error);
  }
};
  </script>
  
  <style scoped>
  .register-view {
    min-height: 100vh;
    display: flex;
    align-items: center;
    background-color: #f8f9fa;
    padding: 2rem 0;
  }
  </style>