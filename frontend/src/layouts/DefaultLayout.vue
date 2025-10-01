<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar app flat color="white" class="mc-appbar">
      <v-app-bar-nav-icon
        class="d-md-none"
        @click.stop="drawer = !drawer"
      />
      <v-toolbar-title class="font-weight-bold">
        <span class="primary--text">MindCare+</span>
      </v-toolbar-title>

      <v-spacer />

      <v-btn color="red darken-1" dark class="text-none mr-2" @click="goCrisis">
        <v-icon left>mdi-alert</v-icon> Get Help Now
      </v-btn>

      <v-menu offset-y bottom>
        <template #activator="{ on, attrs }">
          <v-btn text class="text-none" v-bind="attrs" v-on="on">
            <v-icon left>mdi-account-circle</v-icon>
            <span class="d-none d-sm-inline">{{ userEmail || 'Account' }}</span>
            <v-chip
              v-if="plan"
              x-small
              label
              class="ml-2"
              :color="plan === 'premium' ? 'deep-purple accent-4' : 'grey lighten-3'"
              :text-color="plan === 'premium' ? 'white' : 'black'"
            >
              {{ plan }}
            </v-chip>
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item @click="goRoute('/dashboard')">
            <v-list-item-icon><v-icon>mdi-view-dashboard</v-icon></v-list-item-icon>
            <v-list-item-title>Dashboard</v-list-item-title>
          </v-list-item>
          <v-list-item @click="goRoute('/settings')">
            <v-list-item-icon><v-icon>mdi-cog</v-icon></v-list-item-icon>
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item>
          <v-divider class="my-1" />
          <v-list-item @click="logout">
            <v-list-item-icon><v-icon>mdi-logout</v-icon></v-list-item-icon>
            <v-list-item-title>Log out</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      app
      v-model="drawer"
      :permanent="$vuetify.breakpoint.mdAndUp"
      floating
      width="256"
      class="mc-drawer"
    >
      <v-list dense nav>
        <v-list-item two-line class="mb-2">
          <v-list-item-avatar color="primary" class="elevation-1">
            <v-icon dark>mdi-heart</v-icon>
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title class="font-weight-medium">MindCare+</v-list-item-title>
            <v-list-item-subtitle class="text--secondary">Wellness, your way</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>

        <v-divider class="mb-2"></v-divider>

        <v-list-item
          v-for="(item, i) in items"
          :key="i"
          :to="item.to"
          exact
          link
          @click="drawer = $vuetify.breakpoint.mdAndUp ? drawer : false"
        >
          <v-list-item-icon><v-icon>{{ item.icon }}</v-icon></v-list-item-icon>
          <v-list-item-title>{{ item.text }}</v-list-item-title>
          <v-spacer />
          <v-chip
            v-if="item.badge && showUpgradeBadge && plan !== 'premium'"
            x-small
            color="amber lighten-4"
            label
            class="text-uppercase"
          >
            pro
          </v-chip>
        </v-list-item>
      </v-list>

      <v-divider class="my-3" />

      <div class="px-4 py-2">
        <v-alert dense outlined type="info" border="left" class="mb-2">
          Logged in as <strong>{{ userEmail || 'guest' }}</strong>
        </v-alert>

        <v-btn
          v-if="plan !== 'premium'"
          block
          color="deep-purple accent-4"
          dark
          class="text-none"
          @click="goRoute('/upgrade')"
        >
          <v-icon left>mdi-star-circle</v-icon>
          Upgrade to Premium
        </v-btn>
      </div>
    </v-navigation-drawer>

    <!-- Main -->
    <v-main class="mc-main grey lighten-5">
      <!-- center all page content with a global container -->
      <div class="mc-container">
        <!-- optional page header slot -->
        <slot name="header"></slot>

        <slot />

        <!-- optional footer slot -->
        <slot name="footer"></slot>
      </div>
    </v-main>

    <!-- Footer -->
    <v-footer app padless color="white">
      <div class="mc-container py-2 text-caption grey--text text--darken-1">
        <div class="d-flex align-center">
          <div>&copy; {{ new Date().getFullYear() }} MindCare+. For education/demo only — not a medical device.</div>
          <v-spacer />
          <div>
            <a href="https://www.healthline.com/health/mental-health/hotlines" target="_blank" rel="noopener">Global helplines</a>
          </div>
        </div>
      </div>
    </v-footer>
  </v-app>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'DefaultLayout',
  data: () => ({
    drawer: true,
    showUpgradeBadge: true,
    items: [
      { text: 'Dashboard',    icon: 'mdi-view-dashboard',   to: '/dashboard' },
      { text: 'Chat',         icon: 'mdi-chat',             to: '/chat' },
      { text: 'Consultation', icon: 'mdi-account-heart',    to: '/consult' },
      { text: 'Resources',    icon: 'mdi-book-open-variant',to: '/resources' },
      { text: 'Check-ins',    icon: 'mdi-clipboard-check',  to: '/checkin' },
      { text: 'Analytics',    icon: 'mdi-chart-line',       to: '/analytics', badge: true },
    ],
  }),
  computed: {
    ...mapGetters(['me', 'userPlan']),
    userEmail () {
      return (this.me && this.me.email) || ''
    },
    plan () {
      return this.userPlan || 'free'
    },
  },
  created () {
    if (!this.$vuetify.breakpoint.mdAndUp) this.drawer = false
  },
  methods: {
    ...mapActions(['logout']),
    goRoute (to) { this.$router.push(to).catch(() => {}) },
    goCrisis () { this.$router.push('/crisis').catch(() => {}) },
    async logout () {
      await this.$store.dispatch('logout')
      this.$router.push('/login').catch(() => {})
    },
  },
}
</script>

<style scoped>
.text-none { text-transform: none; }

/* main surface spacing */
.mc-main { padding-top: 16px; }

/* global centered container (used in main + footer) */
.mc-container {
  max-width: 1120px;   /* tweak width to taste */
  margin: 0 auto;
  padding: 24px 16px;
}

/* keep drawer tidy */
.mc-drawer { border-right: 1px solid rgba(0,0,0,0.06); }

/* slim appbar on desktop */
.mc-appbar { border-bottom: 1px solid rgba(0,0,0,0.06); }
</style>