<script setup>
import Navbar from './components/Navbar.vue'
</script>

<template>
  <Navbar />
  
  <!-- <p>
    <strong>Currently in:</strong> {{ $route.path }}
  </p> -->

  <main>
    <RouterView />
  </main>
</template>

<style scoped>

</style>
