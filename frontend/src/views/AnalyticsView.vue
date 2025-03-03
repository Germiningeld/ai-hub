<template>
    <div class="analytics-container">
      <div class="analytics-header">
        <div class="date-filter">
          <label for="date-range">Период:</label>
          <select id="date-range" v-model="dateRange" class="date-select">
            <option value="7">Последние 7 дней</option>
            <option value="30">Последние 30 дней</option>
            <option value="90">Последние 90 дней</option>
            <option value="custom">Выбрать период</option>
          </select>
          
          <div v-if="dateRange === 'custom'" class="custom-date-range">
            <input 
              type="date" 
              v-model="startDate" 
              class="date-input"
              :max="today"
            />
            <span>—</span>
            <input 
              type="date" 
              v-model="endDate" 
              class="date-input"
              :min="startDate"
              :max="today"
            />
            <button @click="fetchData" class="apply-btn">Применить</button>
          </div>
        </div>
      </div>
      
      <div class="analytics-content">
        <div v-if="loading" class="analytics-loading">
          <div class="loading-spinner"></div>
          <p>Загрузка данных...</p>
        </div>
        
        <div v-else-if="error" class="analytics-error">
          <p>{{ error }}</p>
          <button @click="fetchData" class="retry-button">Повторить</button>
        </div>
        
        <template v-else>
          <!-- Карточки с общей статистикой -->
          <div class="stats-cards">
            <div class="stats-card">
              <h3>Общие запросы</h3>
              <div class="stats-value">{{ summary.total_requests }}</div>
              <div class="stats-subtext">За выбранный период</div>
            </div>
            
            <div class="stats-card">
              <h3>Использовано токенов</h3>
              <div class="stats-value">{{ formatNumber(summary.total_tokens) }}</div>
              <div class="stats-subtext">За выбранный период</div>
            </div>
            
            <div class="stats-card">
              <h3>Общие затраты</h3>
              <div class="stats-value">${{ summary.total_cost.toFixed(2) }}</div>
              <div class="stats-subtext">За выбранный период</div>
            </div>
            
            <div class="stats-card savings-card">
              <h3>Экономия</h3>
              <div class="stats-value">${{ savings.toFixed(2) }}</div>
              <div class="stats-subtext">
                По сравнению с подпиской $20/месяц
              </div>
            </div>
          </div>
          
          <!-- График использования по дням -->
          <div class="chart-container">
            <h3>Дневное использование</h3>
            <DailyUsageChart :data="usageData.daily_usage" />
          </div>
          
          <!-- Использование по моделям -->
          <div class="chart-container">
            <h3>Использование по моделям</h3>
            <ModelsUsageChart :data="usageData.model_usage" />
          </div>
          
          <!-- Использование по провайдерам -->
          <div class="chart-container">
            <h3>Использование по провайдерам</h3>
            <ProvidersUsageChart :data="usageData.provider_summary" />
          </div>
        </template>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch } from 'vue';
  import dayjs from 'dayjs';
  import DailyUsageChart from '@/components/analytics/DailyUsageChart.vue';
  import ModelsUsageChart from '@/components/analytics/ModelsUsageChart.vue';
  import ProvidersUsageChart from '@/components/analytics/ProvidersUsageChart.vue';
  import { useAnalyticsStore } from '@/stores/analytics';
  
  const analyticsStore = useAnalyticsStore();
  
  const loading = ref(true);
  const error = ref(null);
  const dateRange = ref('30');
  const startDate = ref('');
  const endDate = ref('');
  
  const today = computed(() => dayjs().format('YYYY-MM-DD'));
  
  const usageData = computed(() => analyticsStore.usageData || {
    daily_usage: [],
    model_usage: [],
    provider_summary: []
  });
  
  const summary = computed(() => analyticsStore.summary || {
    total_requests: 0,
    total_tokens: 0,
    total_cost: 0
  });
  
  const savings = computed(() => {
    // Расчет экономии на основе периода и стоимости подписки $20/месяц
    const days = dayjs(usageData.value.end_date).diff(dayjs(usageData.value.start_date), 'day') + 1;
    const subscriptionCost = (days / 30) * 20; // Пропорциональная стоимость подписки
    return Math.max(0, subscriptionCost - summary.value.total_cost);
  });
  
  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };
  
  const fetchData = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      let params = {};
      
      if (dateRange.value === 'custom') {
        params = {
          start_date: startDate.value,
          end_date: endDate.value
        };
      } else {
        const days = parseInt(dateRange.value);
        params = {
          start_date: dayjs().subtract(days, 'day').format('YYYY-MM-DD'),
          end_date: today.value
        };
      }
      
      await analyticsStore.fetchUsageData(params);
      await analyticsStore.fetchSummary();
    } catch (err) {
      error.value = 'Ошибка при загрузке данных аналитики. Попробуйте позже.';
      console.error('Error fetching analytics data:', err);
    } finally {
      loading.value = false;
    }
  };
  
  // Инициализация дат для пользовательского периода
  onMounted(() => {
    startDate.value = dayjs().subtract(30, 'day').format('YYYY-MM-DD');
    endDate.value = today.value;
    fetchData();
  });
  
  // Наблюдение за изменением dateRange
  watch(dateRange, (newValue) => {
    if (newValue !== 'custom') {
      fetchData();
    }
  });
  </script>
  
  <style scoped>
  .analytics-container {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .analytics-header {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
  }
  
  .date-filter {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  
  .date-select {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .custom-date-range {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .date-input {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  .apply-btn {
    padding: 0.5rem 0.75rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
  }
  
  .analytics-content {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
  }
  
  .analytics-loading, .analytics-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
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
  
  .stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stats-card {
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.savings-card {
  background-color: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.stats-value {
  font-size: 2rem;
  font-weight: 600;
  margin: 0.5rem 0;
}

.stats-subtext {
  font-size: 0.875rem;
  color: #6b7280;
}

.chart-container {
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.25rem;
}
</style>