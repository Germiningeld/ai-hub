/**
 * Настраивает автоскрытие скроллбара для указанного элемента
 * @param {HTMLElement} element - DOM-элемент, для которого настраивается скроллбар
 * @param {Object} options - дополнительные опции
 * @param {number} options.showDelay - задержка перед показом скроллбара в мс (по умолчанию 0)
 * @param {number} options.hideDelay - задержка перед скрытием скроллбара в мс (по умолчанию 1500)
 */
export const setupAutoHideScrollbar = (element, options = {}) => {
    if (!element) return;
    
    // Настройки по умолчанию
    const settings = {
      showDelay: 0,
      hideDelay: 1500,
      ...options
    };
    
    // Добавляем базовый класс
    element.classList.add('auto-hide-scrollbar');
    
    // Таймер для скрытия скроллбара
    let scrollTimer;
    
    // Функция для показа скроллбара
    const showScrollbar = () => {
      clearTimeout(scrollTimer);
      
      // Если настроена задержка показа
      if (settings.showDelay > 0) {
        setTimeout(() => {
          element.classList.add('scrolling');
        }, settings.showDelay);
      } else {
        element.classList.add('scrolling');
      }
    };
    
    // Функция для скрытия скроллбара
    const hideScrollbar = () => {
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(() => {
        element.classList.remove('scrolling');
      }, settings.hideDelay);
    };
    
    // При скролле показываем скроллбар и сбрасываем таймер
    element.addEventListener('scroll', () => {
      showScrollbar();
      hideScrollbar();
    });
    
    // При наведении мыши на элемент показываем скроллбар
    element.addEventListener('mouseenter', showScrollbar);
    
    // При касании (для мобильных устройств)
    element.addEventListener('touchstart', showScrollbar);
    
    // При уходе мыши с элемента скрываем скроллбар
    element.addEventListener('mouseleave', hideScrollbar);
    
    // При окончании касания
    element.addEventListener('touchend', hideScrollbar);
  };
  
  /**
   * Инициализирует автоскрытие скроллбаров для всех подходящих элементов
   * Вызывайте эту функцию в App.vue в хуке onMounted
   */
  export const initializeScrollbars = () => {
    // Основные элементы приложения, которые имеют скроллбары
    const scrollableSelectors = [
      '.thread-list-body',
      '.message-list',
      '.chat-messages',
      '.prompt-list-container',
      '.settings-container'
    ];
    
    // Для каждого селектора находим все элементы и настраиваем скроллбар
    scrollableSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        setupAutoHideScrollbar(element);
      });
    });
  };
  
  /**
   * Настраивает скроллбары для компонента после его монтирования
   * Используйте эту функцию внутри onMounted отдельных компонентов
   * @param {string} selector - CSS-селектор элемента со скроллом
   */
  export const setupComponentScrollbar = (selector) => {
    setTimeout(() => {
      const element = document.querySelector(selector);
      if (element) {
        setupAutoHideScrollbar(element);
      }
    }, 100); // Небольшая задержка для гарантии, что DOM обновлен
  };
  
  export default {
    setupAutoHideScrollbar,
    initializeScrollbars,
    setupComponentScrollbar
  };