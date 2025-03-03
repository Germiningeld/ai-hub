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
    const labels = props.data.map(item => `${item.provider}: ${item.model}`);
    const requestsData = props.data.map(item => item.requests);
    const tokensData = props.data.map(item => item.tokens);
    const costData = props.data.map(item => item.cost);
    
    // Генерация цветов для графика
    const getColors = (count) => {
      const colors = [
        'rgba(59, 130, 246, 0.7)',  // Синий
        'rgba(16, 185, 129, 0.7)',  // Зеленый
        'rgba(249, 115, 22, 0.7)',  // Оранжевый
        'rgba(139, 92, 246, 0.7)',  // Фиолетовый
        'rgba(236, 72, 153, 0.7)',  // Розовый
        'rgba(245, 158, 11, 0.7)',  // Желтый
        'rgba(14, 165, 233, 0.7)'   // Голубой
      ];
      
      return Array(count).fill().map((_, i) => colors[i % colors.length]);
    };
    
    const backgroundColor = getColors(labels.length);
    
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
            backgroundColor: backgroundColor,
            borderColor: backgroundColor.map(color => color.replace('0.7', '1')),
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              afterLabel: function(context) {
                const index = context.dataIndex;
                return [
                  `Токены: ${tokensData[index].toLocaleString()}`,
                  `Стоимость: $${costData[index].toFixed(2)}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Модель'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Количество запросов'
            },
            beginAtZero: true
          }
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