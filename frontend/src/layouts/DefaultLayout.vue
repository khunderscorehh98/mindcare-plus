<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar app flat color="white">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" class="d-sm-none" />
      <v-toolbar-title class="font-weight-bold">
        <span class="primary--text">MindCare+</span>
      </v-toolbar-title>

      <v-spacer />

      <!-- Get Help Now -->
      <v-btn
        color="red darken-1"
        class="mr-2"
        dark
        @click="goCrisis"
      >
        <v-icon left>mdi-alert</v-icon>
        Get Help Now
      </v-btn>

      <!-- User menu -->
      <v-menu offset-y bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn text v-bind="attrs" v-on="on" class="text-none">
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
          link
          exact
          @click="drawer = $vuetify.breakpoint.mdAndUp ? drawer : false"
        >
          <v-list-item-icon><v-icon>{{ item.icon }}</v-icon></v-list-item-icon>
          <v-list-item-title>{{ item.text }}</v-list-item-title>
          <v-spacer />
          <v-chip
            v-if="item.badge && showUpgradeBadge && plan !== 'premium'"
            x-small
            color="amber lighten-4"
            class="text-uppercase"
            label
          >
            pro
          </v-chip>
        </v-list-item>
      </v-list>

      <v-divider class="my-3" />

      <div class="px-4 py-2">
        <v-alert
          dense
          outlined
          type="info"
          border="left"
          class="mb-2"
        >
          Logged in as <strong>{{ userEmail || 'guest' }}</strong>
        </v-alert>

        <v-btn
          v-if="plan !== 'premium'"
          block
          color="deep-purple accent-4"
          dark
          @click="goRoute('/upgrade')"
        >
          <v-icon left>mdi-star-circle</v-icon>
          Upgrade to Premium
        </v-btn>
      </div>
    </v-navigation-drawer>

    <!-- Main -->
    <v-main>
      <v-container fluid class="py-4">
        <!-- Optional page header slot -->
        <slot name="header"></slot>

        <!-- Page content -->
        <router-view />

        <!-- Optional footer slot -->
        <slot name="footer"></slot>
      </v-container>
    </v-main>

    <!-- Footer -->
    <v-footer app padless color="white">
      <v-container fluid class="px-4 py-2 text-caption grey--text text--darken-1">
        <div class="d-flex align-center">
          <div>&copy; {{ new Date().getFullYear() }} MindCare+. For education/demo only — not a medical device.</div>
          <v-spacer />
          <div>
            <a href="https://www.healthline.com/health/mental-health/hotlines" target="_blank" rel="noopener">Global helplines</a>
          </div>
        </div>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'DefaultLayout',
  data: () => ({
    drawer: true,
    showUpgradeBadge: true,
    items: [
      { text: 'Dashboard', icon: 'mdi-view-dashboard', to: '/dashboard' },
      { text: 'Chat', icon: 'mdi-chat', to: '/chat' },
      { text: 'Consultation', icon: 'mdi-account-heart', to: '/consult' },
      { text: 'Resources', icon: 'mdi-book-open-variant', to: '/resources' },
      { text: 'Check-ins', icon: 'mdi-clipboard-check', to: '/checkins' },
      { text: 'Analytics', icon: 'mdi-chart-line', to: '/analytics', badge: true },
    ],
  }),
  computed: {
    ...mapGetters(['isAuthed', 'user', 'plan']),
    userEmail() { return this.user && this.user.email; },
  },
  created() {
    // collapse drawer on small screens by default
    if (!this.$vuetify.breakpoint.mdAndUp) this.drawer = false;
  },
  methods: {
    ...mapActions(['logoutAction']),
    goRoute(to) { this.$router.push(to); },
    goCrisis() {
      // internal crisis page or external helpline list
      this.$router.push('/crisis').catch(() => {});
    },
    async logout() {
      await this.logoutAction();
      this.$router.push('/login');
    },
  },
};
</script>

<style scoped>
.text-none { text-transform: none; }
</style>