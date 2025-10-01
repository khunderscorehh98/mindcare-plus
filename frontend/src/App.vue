<!-- src/App.vue -->
<template>
  <v-app>
    <!-- Wrap every page in DefaultLayout -->
    <!-- <DefaultLayout /> -->
      <router-view />
  </v-app>
</template>

<script>
import DefaultLayout from './layouts/DefaultLayout.vue'

export default {
  name: 'App',
  components: {
    DefaultLayout,
  },
}
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>