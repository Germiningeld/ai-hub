<template>
  <div class="thread-list h-100">
    <!-- Поиск по тредам -->
    <div class="px-3 pt-3">
      <div class="input-group input-group-sm mb-2">
        <span class="input-group-text bg-light border-end-0">
          <i class="bi bi-search"></i>
        </span>
        <input
          type="text"
          class="form-control border-start-0"
          placeholder="Поиск бесед..."
          v-model="searchQuery"
        >
      </div>

      <!-- Фильтры по категориям -->
      <div class="mb-3">
        <select class="form-select form-select-sm" v-model="selectedCategory">
          <option value="">Все категории</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Тело списка тредов (скроллируемая область) -->
    <div class="thread-list-body">
      <!-- Загрузчик -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>

      <!-- Список тредов -->
      <div v-else-if="filteredThreads.length > 0">
        <ThreadItem
          v-for="thread in filteredThreads"
          :key="thread.id"
          :thread="thread"
          :is-active="activeThreadId === thread.id"
          @click="selectThread(thread.id, thread.title)"
          @context-menu="showContextMenu($event, thread)"
        />
      </div>

      <!-- Пустое состояние -->
      <div v-else class="text-center text-muted py-5">
        <i class="bi bi-chat-square-text" style="font-size: 2rem;"></i>
        <p class="mt-2">{{ searchQuery ? 'Ничего не найдено' : 'У вас еще нет бесед' }}</p>
        <button class="btn btn-sm btn-outline-primary" @click="$emit('create-thread')">
          Начать новую беседу
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import ThreadItem from './ThreadItem.vue';
import threadService from '@/services/threadService';
import categoryService from '@/services/categoryService';

// Эмиты событий
const emit = defineEmits(['select-thread', 'create-thread']);

// Состояние компонента
const loading = ref(true);
const threads = ref([]);
const categories = ref([]);
const searchQuery = ref('');
const selectedCategory = ref('');
const activeThreadId = ref(null);
const error = ref(null);

// Фильтрованный список тредов
const filteredThreads = computed(() => {
  let result = threads.value;
  
  // Фильтр по поиску
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(thread => 
      thread.title.toLowerCase().includes(query)
    );
  }
  
  // Фильтр по категории
  if (selectedCategory.value) {
    result = result.filter(thread => 
      thread.category_id === selectedCategory.value
    );
  }
  
  return result;
});

// Загрузка данных
onMounted(async () => {
  await loadThreads();
  await loadCategories();
});

// При изменении фильтров перезагружаем треды
watch([searchQuery, selectedCategory], () => {
  loadThreads();
});

// Функция загрузки тредов
const loadThreads = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // Параметры запроса
    const params = {
      limit: 50,
      search: searchQuery.value || undefined,
      category_id: selectedCategory.value || undefined,
      is_archived: false
    };
    
    const response = await threadService.getThreads(params);
    threads.value = response.data;
    
  } catch (err) {
    console.error('Ошибка при загрузке тредов:', err);
    error.value = 'Не удалось загрузить список бесед';
  } finally {
    loading.value = false;
  }
};

// Функция загрузки категорий
const loadCategories = async () => {
  try {
    const response = await categoryService.getCategories();
    categories.value = response.data;
  } catch (err) {
    console.error('Ошибка при загрузке категорий:', err);
  }
};

// Выбор треда
const selectThread = (threadId, title) => {
  activeThreadId.value = threadId;
  emit('select-thread', threadId, title);
};

// Обработка контекстного меню на треде
const showContextMenu = (event, thread) => {
  event.preventDefault();
  
  // Создаем и показываем контекстное меню
  const contextMenu = document.createElement('div');
  contextMenu.className = 'position-fixed bg-white shadow rounded py-1';
  contextMenu.style.zIndex = '1000';
  contextMenu.style.left = `${event.clientX}px`;
  contextMenu.style.top = `${event.clientY}px`;
  
  // Создаем пункты меню
  const menuItems = [
    { text: 'Закрепить', icon: 'bi-pin-angle', action: () => pinThread(thread.id) },
    { text: 'Переименовать', icon: 'bi-pencil', action: () => renameThread(thread.id) },
    { text: 'Архивировать', icon: 'bi-archive', action: () => archiveThread(thread.id) },
    { text: 'Удалить', icon: 'bi-trash', action: () => showDeleteConfirmation(thread) }
  ];
  
  // Добавляем пункты в меню
  menuItems.forEach(item => {
    const menuItem = document.createElement('div');
    menuItem.className = 'px-3 py-2 cursor-pointer d-flex align-items-center';
    menuItem.innerHTML = `<i class="bi ${item.icon} me-2"></i> ${item.text}`;
    menuItem.addEventListener('click', () => {
      document.body.removeChild(contextMenu);
      item.action();
    });
    menuItem.addEventListener('mouseover', () => {
      menuItem.classList.add('bg-light');
    });
    menuItem.addEventListener('mouseout', () => {
      menuItem.classList.remove('bg-light');
    });
    contextMenu.appendChild(menuItem);
  });
  
  // Добавляем меню в DOM
  document.body.appendChild(contextMenu);
  
  // Закрываем меню при клике вне его
  const closeMenu = (e) => {
    if (!contextMenu.contains(e.target)) {
      document.body.removeChild(contextMenu);
      document.removeEventListener('click', closeMenu);
    }
  };
  
  // Небольшая задержка, чтобы текущий клик не закрыл сразу меню
  setTimeout(() => {
    document.addEventListener('click', closeMenu);
  }, 100);
};

// Функции для действий контекстного меню
const pinThread = async (threadId) => {
  try {
    await threadService.updateThread(threadId, { is_pinned: true });
    await loadThreads(); // Перезагружаем список тредов
  } catch (error) {
    console.error('Ошибка при закреплении треда:', error);
  }
};

const renameThread = (threadId) => {
  const thread = threads.value.find(t => t.id === threadId);
  if (!thread) return;
  
  const newTitle = prompt('Введите новое название беседы:', thread.title);
  if (newTitle && newTitle.trim()) {
    threadService.updateThread(threadId, { title: newTitle.trim() })
      .then(() => loadThreads())
      .catch(error => console.error('Ошибка при переименовании треда:', error));
  }
};

const archiveThread = async (threadId) => {
  try {
    await threadService.updateThread(threadId, { is_archived: true });
    await loadThreads(); // Перезагружаем список тредов
  } catch (error) {
    console.error('Ошибка при архивировании треда:', error);
  }
};

// Упрощенное подтверждение удаления через alert
const showDeleteConfirmation = (thread) => {
  if (confirm(`Вы уверены, что хотите удалить беседу «${thread.title}»?`)) {
    deleteThread(thread.id);
  }
};

const deleteThread = async (threadId) => {
  try {
    await threadService.deleteThread(threadId);
    
    // Если удаляемый тред был активным, сбрасываем активный тред
    if (activeThreadId.value === threadId) {
      activeThreadId.value = null;
      emit('select-thread', null, '');
    }
    
    await loadThreads(); // Перезагружаем список тредов
  } catch (error) {
    console.error('Ошибка при удалении треда:', error);
    alert('Произошла ошибка при удалении беседы');
  }
};
</script>

<style scoped>
/* Контейнер списка тредов */
.thread-list {
  height: 100%;
  overflow: hidden;
  position: relative;
}

/* Блок поиска и фильтров */
.thread-list .px-3.pt-3 {
  position: absolute;
  top: 60px;
  left: 0;
  right: 0;
  z-index: 9;
  background-color: #fff;
}

/* Тело списка */
.thread-list-body {
  position: absolute;
  top: 150px;
  bottom: 0;
  left: 0;
  right: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.form-control:focus,
.form-select:focus {
  box-shadow: 0 0 0 0.15rem rgba(67, 97, 238, 0.25);
  border-color: #4361ee;
}

/* Стили для контекстного меню */
.cursor-pointer {
  cursor: pointer;
}
</style>