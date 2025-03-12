<template>
    <div 
      class="modal fade" 
      :id="id" 
      tabindex="-1" 
      aria-labelledby="confirmationModalLabel" 
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="confirmationModalLabel">{{ title }}</h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            {{ message }}
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              data-bs-dismiss="modal"
            >
              Отмена
            </button>
            <button 
              type="button" 
              class="btn" 
              :class="confirmButtonClass" 
              @click="handleConfirm"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps, defineEmits } from 'vue';
  
  const props = defineProps({
    id: {
      type: String,
      default: 'confirmationModal'
    },
    title: {
      type: String,
      default: 'Подтверждение'
    },
    message: {
      type: String,
      default: 'Вы уверены, что хотите выполнить это действие?'
    },
    confirmText: {
      type: String,
      default: 'Подтвердить'
    },
    confirmButtonClass: {
      type: String,
      default: 'btn-primary'
    }
  });
  
  const emit = defineEmits(['confirm']);
  
  const handleConfirm = () => {
    emit('confirm');
    
    // Закрываем модальное окно
    if (typeof bootstrap !== 'undefined') {
      const modalEl = document.getElementById(props.id);
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) {
        modal.hide();
      }
    }
  };
  </script>