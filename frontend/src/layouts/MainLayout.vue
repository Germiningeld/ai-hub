<template>
    <div class="layout">
      <NavigationSidebar />
      <div class="content">
        <TopHeader />
        <main class="main-content">
          <slot></slot>
        </main>
      </div>
    </div>
  </template>
  
  <script setup>
  import NavigationSidebar from '@/components/common/NavigationSidebar.vue';
  import TopHeader from '@/components/common/TopHeader.vue';
  </script>
  
  <style scoped>
  .layout {
    display: flex;
    min-height: 100vh;
  }
  
  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .main-content {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
  }
  
  @media (max-width: 768px) {
    .layout {
      flex-direction: column;
    }
  }
  </style>