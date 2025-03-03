import { defineStore } from 'pinia';
import { ref } from 'vue';
import { analyticsService } from '@/services/analyticsService';

export const useAnalyticsStore = defineStore('analytics', () => {
  const usageData = ref(null);
  const summary = ref(null);
  
  async function fetchUsageData(params = {}) {
    try {
      const data = await analyticsService.getUsageData(params);
      usageData.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching usage data:', error);
      throw error;
    }
  }
  
  async function fetchSummary() {
    try {
      const data = await analyticsService.getSummary();
      summary.value = data;
      return data;
    } catch (error) {
      console.error('Error fetching summary data:', error);
      throw error;
    }
  }
  
  return {
    usageData,
    summary,
    fetchUsageData,
    fetchSummary
  };
});