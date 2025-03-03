import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authService } from '@/services/authService';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const token = ref(localStorage.getItem('token') || null);
  
  const isLoggedIn = computed(() => !!token.value);
  
  async function login(email, password) {
    try {
      const response = await authService.login(email, password);
      token.value = response.access_token;
      localStorage.setItem('token', token.value);
      
      // Загружаем информацию о пользователе
      await fetchUserInfo();
      
      return user.value;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }
  
  async function fetchUserInfo() {
    try {
      const userData = await authService.getUserInfo();
      user.value = userData;
      return userData;
    } catch (error) {
      console.error('Error fetching user info:', error);
      throw error;
    }
  }
  
  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
  }
  
  function updateUser(userData) {
    user.value = { ...user.value, ...userData };
  }
  
  return { 
    user, 
    token, 
    isLoggedIn, 
    login, 
    logout, 
    fetchUserInfo, 
    updateUser 
  };
});