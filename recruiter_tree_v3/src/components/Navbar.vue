<template>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <!-- <RouterLink class="nav-link" to="/">logo or smth</RouterLink> -->
        <!-- <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button> -->
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/">Home</RouterLink>
            </li>

            <li class="nav-item dropdown" :class="{ show: isDropdownOpen }">
              <button
                class="nav-link dropdown-toggle"
                :class="{ active: isRecruiterActive }"
                type="button"
                @click="isDropdownOpen = !isDropdownOpen"
              >
                Recruiter
              </button>

              <ul class="dropdown-menu" :class="{ show: isDropdownOpen }">
                <li>
                  <RouterLink class="dropdown-item" to="/personal_tree">Individual tree</RouterLink>
                </li>
                <li>
                  <RouterLink class="dropdown-item" to="/tree">Tree</RouterLink>
                </li>
              </ul>
            </li>

            <li class="nav-item">
              <RouterLink class="nav-link" to="/display-list">Display List</RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const isDropdownOpen = ref(false);

const recruiterRoutes = ['/tree', '/personal_tree']

const isRecruiterActive = computed(() =>
  recruiterRoutes.some(path => route.path.startsWith(path))
)

watch(() => route.path, () => {
  isDropdownOpen.value = false;
});

</script>

<style scoped>
    .router-link-active, :deep(.nav-link.active) {
        color: aqua;
    }
</style>