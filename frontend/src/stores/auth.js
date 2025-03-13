import { defineStore } from 'pinia';
import authService from '@/services/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: localStorage.getItem('auth_token') !== null,
    loading: false,
    error: null
  }),
  
  getters: {
    currentUser: (state) => state.user,
    isLoading: (state) => state.loading,
    hasError: (state) => state.error !== null
  },
  
  actions: {
    async login(email, password) {
      this.loading = true;
      this.error = null;
      
      try {
        await authService.login(email, password);
        this.isAuthenticated = true;
        await this.fetchUserProfile();
        return true;
      } catch (error) {
        this.error = error.message;
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async register(username, email, password) {
      this.loading = true;
      this.error = null;
      
      try {
        await authService.register(username, email, password);
        return true;
      } catch (error) {
        this.error = error.message;
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchUserProfile() {
      if (!this.isAuthenticated) return;
      
      this.loading = true;
      
      try {
        const userData = await authService.getCurrentUser();
        this.user = userData;
      } catch (error) {
        this.error = error.message;
        console.error('Ошибка при получении профиля пользователя:', error);
      } finally {
        this.loading = false;
      }
    },
    
    logout() {
      authService.logout();
      this.user = null;
      this.isAuthenticated = false;
      this.error = null;
    },
    
    clearError() {
      this.error = null;
    }
  },
  
  // Сохраняем состояние авторизации в localStorage
  persist: {
    paths: ['isAuthenticated']
  }
});