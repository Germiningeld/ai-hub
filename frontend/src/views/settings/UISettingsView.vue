<template>
    <div class="ui-settings">
      <h2 class="section-title">Настройки интерфейса</h2>
      <p class="section-description">
        Адаптируйте интерфейс AIHub под свои предпочтения.
      </p>
      
      <div class="settings-sections">
        <div class="settings-section">
          <h3 class="subsection-title">Внешний вид</h3>
          
          <div class="setting-item">
            <div class="setting-info">
              <h4 class="setting-title">Тема</h4>
              <p class="setting-description">Выберите светлую или темную тему интерфейса.</p>
            </div>
            
            <div class="setting-control">
              <div class="theme-selector">
                <button 
                  class="theme-option" 
                  :class="{ 'active': selectedTheme === 'light' }" 
                  @click="setTheme('light')"
                >
                  <span class="theme-icon">☀️</span>
                  <span>Светлая</span>
                </button>
                
                <button 
                  class="theme-option" 
                  :class="{ 'active': selectedTheme === 'dark' }" 
                  @click="setTheme('dark')"
                >
                  <span class="theme-icon">🌙</span>
                  <span>Темная</span>
                </button>
                
                <button 
                  class="theme-option" 
                  :class="{ 'active': selectedTheme === 'system' }" 
                  @click="setTheme('system')"
                >
                  <span class="theme-icon">🖥️</span>
                  <span>Системная</span>
                </button>
              </div>
            </div>
          </div>
          
          <div class="setting-item">
            <div class="setting-info">
              <h4 class="setting-title">Размер шрифта</h4>
              <p class="setting-description">Отрегулируйте размер текста в интерфейсе.</p>
            </div>
            
            <div class="setting-control">
              <div class="font-size-selector">
                <button 
                  class="font-size-option" 
                  :class="{ 'active': fontSize === 'small' }" 
                  @click="setFontSize('small')"
                >
                  A<sub>-</sub>
                </button>
                
                <button 
                  class="font-size-option" 
                  :class="{ 'active': fontSize === 'medium' }" 
                  @click="setFontSize('medium')"
                >
                  A
                </button>
                
                <button 
                  class="font-size-option" 
                  :class="{ 'active': fontSize === 'large' }" 
                  @click="setFontSize('large')"
                >
                  A<sup>+</sup>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="settings-section">
          <h3 class="subsection-title">Поведение интерфейса</h3>
          
          <div class="setting-item">
            <div class="setting-info">
              <h4 class="setting-title">Автоматический переход к новым сообщениям</h4>
              <p class="setting-description">Автоматически прокручивать чат к новым сообщениям.</p>
            </div>
            
            <div class="setting-control">
              <label class="toggle-switch">
                <input type="checkbox" v-model="autoScroll">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          <div class="setting-item">
            <div class="setting-info">
              <h4 class="setting-title">Показывать метаданные сообщений</h4>
              <p class="setting-description">Отображать техническую информацию о сообщениях (токены, стоимость и т.д.).</p>
            </div>
            
            <div class="setting-control">
              <label class="toggle-switch">
                <input type="checkbox" v-model="showMessageMetadata">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          <div class="setting-item">
            <div class="setting-info">
              <h4 class="setting-title">Компактный режим</h4>
              <p class="setting-description">Уменьшает отступы и размеры элементов для отображения большего количества информации.</p>
            </div>
            
            <div class="setting-control">
              <label class="toggle-switch">
                <input type="checkbox" v-model="compactMode">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
        
        <div class="settings-section">
          <h3 class="subsection-title">Уведомления</h3>
          
          <div class="setting-item">
            <div class="setting-info">
              <h4 class="setting-title">Включить звуковые уведомления</h4>
              <p class="setting-description">Воспроизводить звук при получении нового сообщения.</p>
            </div>
            
            <div class="setting-control">
              <label class="toggle-switch">
                <input type="checkbox" v-model="soundNotifications">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          <div class="setting-item">
            <div class="setting-info">
              <h4 class="setting-title">Оповещения о достижении лимитов API</h4>
              <p class="setting-description">Уведомлять при приближении к установленным лимитам API ключей.</p>
            </div>
            
            <div class="setting-control">
              <label class="toggle-switch">
                <input type="checkbox" v-model="apiLimitAlerts">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <div class="settings-actions">
        <button @click="resetToDefaults" class="reset-button">Сбросить настройки</button>
        <button @click="saveSettings" class="save-button">Сохранить настройки</button>
      </div>
      
      <div v-if="saveSuccess" class="success-message">
        Настройки успешно сохранены!
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  
  // Настройки интерфейса
  const selectedTheme = ref('light');
  const fontSize = ref('medium');
  const autoScroll = ref(true);
  const showMessageMetadata = ref(true);
  const compactMode = ref(false);
  const soundNotifications = ref(false);
  const apiLimitAlerts = ref(true);
  const saveSuccess = ref(false);
  
  // Загрузка настроек из localStorage
  const loadSettings = () => {
    const settings = localStorage.getItem('ui-settings');
    if (settings) {
      const parsedSettings = JSON.parse(settings);
      selectedTheme.value = parsedSettings.theme || 'light';
      fontSize.value = parsedSettings.fontSize || 'medium';
      autoScroll.value = parsedSettings.autoScroll !== undefined ? parsedSettings.autoScroll : true;
      showMessageMetadata.value = parsedSettings.showMessageMetadata !== undefined ? parsedSettings.showMessageMetadata : true;
      compactMode.value = parsedSettings.compactMode || false;
      soundNotifications.value = parsedSettings.soundNotifications || false;
      apiLimitAlerts.value = parsedSettings.apiLimitAlerts !== undefined ? parsedSettings.apiLimitAlerts : true;
    }
    
    // Применяем тему
    applyTheme();
    
    // Применяем размер шрифта
    applyFontSize();
    
    // Применяем компактный режим
    applyCompactMode();
  };
  
  // Сохранение настроек
  const saveSettings = () => {
    const settings = {
      theme: selectedTheme.value,
      fontSize: fontSize.value,
      autoScroll: autoScroll.value,
      showMessageMetadata: showMessageMetadata.value,
      compactMode: compactMode.value,
      soundNotifications: soundNotifications.value,
      apiLimitAlerts: apiLimitAlerts.value
    };
    
    localStorage.setItem('ui-settings', JSON.stringify(settings));
    
    // Показываем сообщение об успешном сохранении
    saveSuccess.value = true;
    
    // Скрываем сообщение через 3 секунды
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  };
  
  // Сброс настроек на значения по умолчанию
  const resetToDefaults = () => {
    selectedTheme.value = 'light';
    fontSize.value = 'medium';
    autoScroll.value = true;
    showMessageMetadata.value = true;
    compactMode.value = false;
    soundNotifications.value = false;
    apiLimitAlerts.value = true;
    
    // Применяем настройки
    applyTheme();
    applyFontSize();
    applyCompactMode();
    
    // Сохраняем настройки
    saveSettings();
  };
  
  // Установка темы
  const setTheme = (theme) => {
    selectedTheme.value = theme;
    applyTheme();
  };
  
  // Применение темы
  const applyTheme = () => {
    let theme;
    
    if (selectedTheme.value === 'system') {
      // Определяем системную тему
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      theme = prefersDark ? 'dark' : 'light';
    } else {
      theme = selectedTheme.value;
    }
    
    // Применяем тему
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };
  
// Установка размера шрифта
const setFontSize = (size) => {
  fontSize.value = size;
  applyFontSize();
};

// Применение размера шрифта
const applyFontSize = () => {
  const rootElement = document.documentElement;
  
  // Удаляем предыдущие классы размера шрифта
  rootElement.classList.remove('font-small', 'font-medium', 'font-large');
  
  // Добавляем новый класс
  rootElement.classList.add(`font-${fontSize.value}`);
};

// Применение компактного режима
const applyCompactMode = () => {
  if (compactMode.value) {
    document.documentElement.classList.add('compact-mode');
  } else {
    document.documentElement.classList.remove('compact-mode');
  }
};

// Отслеживание изменения системной темы
onMounted(() => {
  loadSettings();
  
  // Добавляем слушатель изменения системной темы
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (selectedTheme.value === 'system') {
      applyTheme();
    }
  });
});
</script>

<style scoped>
.ui-settings {
  max-width: 800px;
}

.section-title {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.section-description {
  margin-bottom: 2rem;
  color: #6b7280;
}

.settings-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
}

.settings-section:last-child {
  border-bottom: none;
}

.subsection-title {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-info {
  flex: 1;
  margin-right: 2rem;
}

.setting-title {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 500;
}

.setting-description {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

/* Переключатели темы */
.theme-selector {
  display: flex;
  gap: 0.5rem;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background-color: var(--background-color);
  cursor: pointer;
}

.theme-option.active {
  border-color: var(--primary-color);
  background-color: rgba(59, 130, 246, 0.1);
}

.theme-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

/* Выбор размера шрифта */
.font-size-selector {
  display: flex;
  gap: 0.5rem;
}

.font-size-option {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background-color: var(--background-color);
  cursor: pointer;
}

.font-size-option.active {
  border-color: var(--primary-color);
  background-color: rgba(59, 130, 246, 0.1);
}

/* Переключатель */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e5e7eb;
  transition: .4s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--primary-color);
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.reset-button {
  padding: 0.75rem 1.5rem;
  background-color: #e5e7eb;
  color: #1f2937;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.save-button {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.success-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(16, 185, 129, 0.1);
  color: #065f46;
  border-radius: 0.25rem;
}
</style>