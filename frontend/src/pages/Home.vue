<template>
  <default-layout>
    <template v-slot:header>
      <v-row align="center" class="mb-6">
        <v-col cols="12" md="8">
          <h1 class="display-1 font-weight-bold primary--text">Welcome to MindCare+</h1>
          <p class="subtitle-1 grey--text text--darken-1">
            Your companion for mental well-being. Private, stigma-free, and available anytime.
          </p>
        </v-col>
        <v-col cols="12" md="4" class="text-md-right">
          <v-btn
            color="red darken-1"
            dark
            large
            class="mb-2"
            @click="$router.push('/chat')"
          >
            <v-icon left>mdi-chat</v-icon>
            Start Chatting
          </v-btn>
        </v-col>
      </v-row>
    </template>

    <!-- Features Grid -->
    <v-row>
      <v-col cols="12" md="6" lg="4" v-for="(f, i) in features" :key="i">
        <v-card class="rounded-xl hover-elevate" outlined @click="go(f.to)">
          <v-card-text class="d-flex flex-column align-center text-center py-6">
            <v-icon x-large color="primary" class="mb-3">{{ f.icon }}</v-icon>
            <h3 class="subtitle-1 font-weight-medium mb-2">{{ f.title }}</h3>
            <p class="text-body-2 grey--text">{{ f.desc }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upgrade Banner -->
    <v-alert
      v-if="plan !== 'premium'"
      type="info"
      border="left"
      prominent
      class="mt-8"
    >
      <div class="d-flex align-center justify-space-between flex-wrap">
        <div>
          <h3 class="subtitle-1 font-weight-bold">Unlock More with Premium</h3>
          <p class="mb-0 text-body-2">
            Access multiple chat sessions, book therapy consultations, and more.
          </p>
        </div>
        <v-btn color="deep-purple accent-4" dark @click="$router.push('/upgrade')">
          <v-icon left>mdi-star</v-icon>
          Upgrade Now
        </v-btn>
      </div>
    </v-alert>
  </default-layout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'Home',
  components: { DefaultLayout },
  computed: {
    ...mapGetters(['plan']),
  },
  data: () => ({
    features: [
      {
        title: 'AI Chat',
        desc: 'Confidential conversations with MindCare+ AI.',
        icon: 'mdi-chat',
        to: '/chat',
      },
      {
        title: 'Therapist Consultation',
        desc: 'Book sessions with licensed professionals.',
        icon: 'mdi-account-heart',
        to: '/consult',
      },
      {
        title: 'Resources',
        desc: 'Articles and guides tailored to your needs.',
        icon: 'mdi-book-open-variant',
        to: '/resources',
      },
      {
        title: 'Check-ins',
        desc: 'Track your mood and stress over time.',
        icon: 'mdi-clipboard-check',
        to: '/checkins',
      },
      {
        title: 'Analytics',
        desc: 'Visualize your well-being trends and progress.',
        icon: 'mdi-chart-line',
        to: '/analytics',
      },
    ],
  }),
  methods: {
    go(to) {
      this.$router.push(to).catch(() => {})
    },
  },
}
</script>

<style scoped>
.hover-elevate {
  transition: box-shadow 0.2s ease;
}
.hover-elevate:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
</style>