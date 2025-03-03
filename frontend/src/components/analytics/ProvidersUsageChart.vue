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
    const labels = props.data.map(item => item.provider);
    const requestsData = props.data.map(item => item.requests);
    const tokensData = props.data.map(item => item.tokens);
    const costData = props.data.map(item => item.cost);
    
    // Цвета для провайдеров
    const providerColors = {
      'openai': 'rgba(16, 163, 127, 0.7)',  // Зеленый
      'anthropic': 'rgba(185, 128, 255, 0.7)',  // Фиолетовый
      'default': 'rgba(59, 130, 246, 0.7)'  // Синий
    };
    
    const backgroundColor = labels.map(label => 
      providerColors[label.toLowerCase()] || providerColors.default
    );
    
    // Уничтожить предыдущий график, если он существует
    if (chart) {
      chart.destroy();
    }
    
    // Создание нового графика
    chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [
          {
            data: costData,
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
            position: 'right',
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const index = context.dataIndex;
                return [
                  `Провайдер: ${labels[index]}`,
                  `Запросы: ${requestsData[index]} (${(requestsData[index] / requestsData.reduce((a, b) => a + b, 0) * 100).toFixed(1)}%)`,
                  `Токены: ${tokensData[index].toLocaleString()}`,
                  `Стоимость: $${costData[index].toFixed(2)} (${(costData[index] / costData.reduce((a, b) => a + b, 0) * 100).toFixed(1)}%)`
                ];
              }
            }
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