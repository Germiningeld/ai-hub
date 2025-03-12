<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue';
import { initializeScrollbars } from '@/utils/scrollbarUtil';

// Инициализируем скроллбары после монтирования приложения
onMounted(() => {
initializeScrollbars();
});
</script>

<style>
/* Импорт иконок Bootstrap */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");

/* Глобальные стили */
body {
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
color: #333;
background-color: #f8f9fa;
}

/* Улучшенные стили для Bootstrap */
.card {
border-radius: 0.5rem;
border: 1px solid rgba(0, 0, 0, 0.08);
box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.btn {
border-radius: 0.375rem;
font-weight: 500;
}

.btn-primary {
background-color: #4361ee;
border-color: #4361ee;
}

.btn-primary:hover {
background-color: #3a56d4;
border-color: #3a56d4;
}

/* Утилиты для работы с текстом и элементами */
.text-truncate-2 {
display: -webkit-box;
-webkit-line-clamp: 2;
-webkit-box-orient: vertical;
overflow: hidden;
}

.cursor-pointer {
cursor: pointer;
}

/* Анимации */
.fade-enter-active,
.fade-leave-active {
transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
opacity: 0;
}

/* Глобальные стили для скроллбаров */
::-webkit-scrollbar {
width: 6px;
height: 6px;
}

::-webkit-scrollbar-track {
background: transparent;
margin: 4px 0;
}

::-webkit-scrollbar-thumb {
background: rgba(67, 97, 238, 0.3);
border-radius: 10px;
transition: background 0.3s, opacity 0.5s;
opacity: 0;
}

:hover::-webkit-scrollbar-thumb,
::-webkit-scrollbar-thumb:hover {
opacity: 1;
background: rgba(67, 97, 238, 0.5);
}

::-webkit-scrollbar-thumb:active {
background: rgba(67, 97, 238, 0.7);
}

::-webkit-scrollbar-button {
display: none;
}

/* Firefox scrollbar styles */
* {
scrollbar-width: thin;
scrollbar-color: rgba(67, 97, 238, 0.3) transparent;
}

*:hover {
scrollbar-color: rgba(67, 97, 238, 0.5) transparent;
}

/* Класс для элементов с автоскрытием скроллбара */
.auto-hide-scrollbar::-webkit-scrollbar-thumb {
opacity: 0;
}

.auto-hide-scrollbar.scrolling::-webkit-scrollbar-thumb {
opacity: 1;
}
</style>