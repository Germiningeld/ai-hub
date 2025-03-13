<template>
    <div class="chart-wrapper">
      <div class="chart-container" ref="chartContainer"></div>
      <div v-if="!data || data.length === 0" class="no-data">
        Нет данных для отображения
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue';
  import Chart from 'chart.js/auto';
  
  const props = defineProps({
    data: {
      type: Array,
      default: () => []
    }
  });
  
  const chartContainer = ref(null);
  let chart = null;
  
  const initChart = () => {
    if (!chartContainer.value || !props.data || props.data.length === 0) return;
    
    const ctx = chartContainer.value.getContext('2d');
    
    // Подготовка данных
    const labels = props.data.map(item => item.date);
    const requestsData = props.data.map(item => item.requests);
    const tokensData = props.data.map(item => item.tokens);
    const costData = props.data.map(item => item.cost);
    
    // Уничтожить предыдущий график, если он существует
    if (chart) {
      chart.destroy();
    }
    
    // Создание нового графика
    chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Запросы',
            data: requestsData,
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
            borderColor: 'rgba(59, 130, 246, 1)',
            borderWidth: 1,
            yAxisID: 'y',
          },
          {
            label: 'Токены',
            data: tokensData,
            backgroundColor: 'rgba(16, 185, 129, 0.5)',
            borderColor: 'rgba(16, 185, 129, 1)',
            borderWidth: 1,
            yAxisID: 'y1',
          },
          {
            label: 'Стоимость ($)',
            data: costData,
            type: 'line',
            fill: false,
            backgroundColor: 'rgba(249, 115, 22, 0.5)',
            borderColor: 'rgba(249, 115, 22, 1)',
            borderWidth: 2,
            tension: 0.1,
            yAxisID: 'y2',
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Дата'
            }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: 'Запросы'
            },
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: {
              drawOnChartArea: false,
            },
            title: {
              display: true,
              text: 'Токены'
            },
          },
          y2: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: {
              drawOnChartArea: false,
            },
            title: {
              display: true,
              text: 'Стоимость ($)'
            },
          },
        }
      }
    });
  };
  
  // Инициализация графика при монтировании компонента
  onMounted(() => {
    initChart();
  });
  
  // Обновление графика при изменении данных
  watch(() => props.data, () => {
    initChart();
  }, { deep: true });
  </script>
  
  <style scoped>
  .chart-wrapper {
    position: relative;
    height: 400px;
    width: 100%;
  }
  
  .chart-container {
    height: 100%;
    width: 100%;
  }
  
  .no-data {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    color: #6b7280;
  }
  </style>