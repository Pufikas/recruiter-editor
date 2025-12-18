<template>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <!-- <RouterLink class="nav-link" to="/">logo or smth</RouterLink> -->
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/">Home</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/tree">Tree</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/display-list">Display List</RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
</template>

<style scoped>
    .router-link-active {
        color: aqua;
    }
</style>
