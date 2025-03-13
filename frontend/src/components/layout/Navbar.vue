<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom d-lg-none">
    <div class="container-fluid">
      <button
        class="navbar-toggler border-0"
        type="button"
        @click="$emit('toggle-sidebar')"
      >
        <i class="bi bi-list"></i>
      </button>
      <a class="navbar-brand mx-auto" href="#">
        <img src="@/assets/css/logo.svg" alt="AIHub" height="30">
      </a>
    </div>
  </nav>
</template>

<script setup>
// Определяем события
const emit = defineEmits(['toggle-sidebar']);
</script>

<style scoped>
.navbar {
  padding: 0.75rem 1rem;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.navbar-toggler:focus {
  box-shadow: none;
}
</style>