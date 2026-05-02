<template>
  <v-app style="background: #F0F4F8">

    <!-- ── Top App Bar ── -->
    <v-app-bar app flat color="white" height="60" style="border-bottom: 1px solid #E1E8EF; z-index: 200">
      <v-app-bar-nav-icon class="d-md-none" color="#546E7A" @click.stop="drawer = !drawer" />

      <div class="d-none d-md-flex align-center ml-1">
        <v-icon small color="primary" class="mr-2">mdi-pulse</v-icon>
        <span style="color: #546E7A; font-size: 13px; font-weight: 500">{{ currentPageTitle }}</span>
      </div>

      <v-spacer />

      <v-btn
        color="error"
        depressed small
        class="mr-3 font-weight-semibold"
        @click="goCrisis"
      >
        <v-icon left small>mdi-phone-alert</v-icon>Emergency
      </v-btn>

      <v-menu offset-y bottom left nudge-bottom="6">
        <template #activator="{ on, attrs }">
          <v-btn text v-bind="attrs" v-on="on" class="px-2" style="height: 52px">
            <v-avatar color="primary" size="32" class="mr-2 elevation-1">
              <span class="white--text font-weight-bold" style="font-size: 13px">{{ initials }}</span>
            </v-avatar>
            <div class="d-none d-sm-block text-left">
              <div style="font-size: 13px; font-weight: 500; color: #1A2332; line-height: 1.3; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ displayName }}</div>
              <div style="font-size: 11px; line-height: 1.3" :style="{ color: plan === 'premium' ? '#00695C' : '#90A4AE' }">
                {{ plan === 'premium' ? '● Premium' : '● Free plan' }}
              </div>
            </div>
            <v-icon small color="grey lighten-1" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list dense width="200" class="py-1" style="border-radius: 8px">
          <div class="px-4 py-2" style="border-bottom: 1px solid #E1E8EF">
            <div style="font-size: 12px; color: #546E7A">Signed in as</div>
            <div style="font-size: 13px; font-weight: 500; color: #1A2332; word-break: break-all">{{ userEmail }}</div>
          </div>
          <v-list-item @click="goRoute('/dashboard')" class="mt-1">
            <v-list-item-icon><v-icon small color="primary">mdi-view-dashboard-outline</v-icon></v-list-item-icon>
            <v-list-item-title style="font-size: 13px">Dashboard</v-list-item-title>
          </v-list-item>
          <v-divider class="my-1" />
          <v-list-item @click="doLogout">
            <v-list-item-icon><v-icon small>mdi-logout</v-icon></v-list-item-icon>
            <v-list-item-title style="font-size: 13px">Sign out</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- ── Dark Sidebar ── -->
    <v-navigation-drawer
      app
      v-model="drawer"
      :permanent="$vuetify.breakpoint.mdAndUp"
      width="240"
      color="#1A2942"
    >
      <!-- Logo -->
      <div class="px-5 py-5">
        <div class="d-flex align-center">
          <div style="width: 36px; height: 36px; border-radius: 8px; background: #1565C0; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 8px rgba(21,101,192,0.4)">
            <v-icon dark small>mdi-heart-pulse</v-icon>
          </div>
          <div class="ml-3">
            <div style="color: white; font-weight: 700; font-size: 15px; line-height: 1.2">MindCare+</div>
            <div style="color: rgba(255,255,255,0.4); font-size: 11px; line-height: 1.3">Mental Wellness</div>
          </div>
        </div>
      </div>

      <div style="border-bottom: 1px solid rgba(255,255,255,0.07)" class="mx-4 mb-3"></div>

      <!-- Nav items -->
      <div class="px-3">
        <div style="color: rgba(255,255,255,0.3); font-size: 10px; font-weight: 700; letter-spacing: 1.2px; padding: 0 8px 8px" class="text-uppercase">
          Menu
        </div>
        <v-list dense nav dark class="pa-0">
          <v-list-item
            v-for="item in items"
            :key="item.to"
            :to="item.to"
            exact
            link
            active-class="mc-nav-active"
            class="mc-nav-item mb-1"
            @click="drawer = $vuetify.breakpoint.mdAndUp ? drawer : false"
          >
            <v-list-item-icon class="my-auto mr-3" style="min-width: 0">
              <v-icon small>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title style="font-size: 13.5px; font-weight: 500">{{ item.text }}</v-list-item-title>
            <v-chip
              v-if="item.badge && plan !== 'premium'"
              x-small label dark
              color="#E65100"
              style="font-size: 9px; height: 16px; font-weight: 700"
            >PRO</v-chip>
          </v-list-item>
        </v-list>
      </div>

      <v-spacer />

      <!-- Bottom upgrade + security note -->
      <div class="px-3 pb-5 pt-2">
        <div style="border-top: 1px solid rgba(255,255,255,0.07)" class="pt-3 mb-3"></div>

        <v-btn
          v-if="plan !== 'premium'"
          block depressed small
          color="primary"
          style="font-size: 12.5px; font-weight: 600; border-radius: 6px; letter-spacing: 0"
          class="mb-3"
          @click="goRoute('/upgrade')"
        >
          <v-icon left small>mdi-star-outline</v-icon>
          Upgrade to Premium
        </v-btn>
        <div v-else class="d-flex align-center mb-3 px-1">
          <v-icon small color="teal lighten-2" class="mr-2">mdi-check-decagram</v-icon>
          <span style="color: rgba(255,255,255,0.6); font-size: 12px">Premium active</span>
        </div>

        <div class="d-flex align-center px-1">
          <v-icon x-small style="color: rgba(255,255,255,0.3)" class="mr-1">mdi-shield-lock-outline</v-icon>
          <span style="color: rgba(255,255,255,0.3); font-size: 11px">End-to-end encrypted</span>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- ── Main Content ── -->
    <v-main style="background: #F0F4F8">
      <div class="mc-container">
        <slot name="header"></slot>
        <slot />
        <slot name="footer"></slot>
      </div>
    </v-main>

    <!-- ── Footer ── -->
    <v-footer app padless color="white" style="border-top: 1px solid #E1E8EF">
      <div class="mc-container py-2 d-flex align-center" style="width: 100%">
        <span style="color: #90A4AE; font-size: 12px">
          &copy; {{ new Date().getFullYear() }} MindCare+ &bull; Educational prototype &bull; Not a medical device
        </span>
        <v-spacer />
        <a
          href="https://www.healthline.com/health/mental-health/hotlines"
          target="_blank" rel="noopener"
          style="color: #1565C0; font-size: 12px; text-decoration: none"
        >Crisis helplines</a>
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
    items: [
      { text: 'Dashboard',    icon: 'mdi-view-dashboard-outline',   to: '/dashboard' },
      { text: 'AI Chat',      icon: 'mdi-chat-outline',              to: '/chat' },
      { text: 'Consultation', icon: 'mdi-stethoscope',               to: '/consult',  badge: true },
      { text: 'Resources',    icon: 'mdi-book-open-outline',         to: '/resources' },
      { text: 'Check-ins',    icon: 'mdi-clipboard-pulse-outline',   to: '/checkin' },
      { text: 'Analytics',    icon: 'mdi-chart-line',                to: '/analytics', badge: true },
    ],
    pageMap: {
      dashboard:  'Dashboard',
      chat:       'AI Chat',
      consult:    'Consultation',
      resources:  'Resources',
      checkin:    'Daily Check-ins',
      analytics:  'Wellness Analytics',
      home:       'Home',
    },
  }),
  computed: {
    ...mapGetters(['me', 'userPlan']),
    userEmail ()        { return (this.me && this.me.email) || '' },
    plan ()             { return this.userPlan || 'free' },
    initials ()         { const e = this.userEmail; return e ? e.charAt(0).toUpperCase() : '?' },
    displayName ()      { const e = this.userEmail; return e.length > 22 ? e.substring(0, 22) + '…' : e || 'Account' },
    currentPageTitle () { return this.pageMap[(this.$route && this.$route.name)] || 'MindCare+' },
  },
  created () {
    if (!this.$vuetify.breakpoint.mdAndUp) this.drawer = false
  },
  methods: {
    ...mapActions(['logout']),
    goRoute (to) { this.$router.push(to).catch(() => {}) },
    goCrisis ()  { this.$router.push('/crisis').catch(() => {}) },
    async doLogout () {
      await this.$store.dispatch('logout')
      this.$router.push('/login').catch(() => {})
    },
  },
}
</script>

<style>
/* Sidebar nav items */
.mc-nav-item {
  border-radius: 6px !important;
  min-height: 40px !important;
  color: rgba(255, 255, 255, 0.65) !important;
}
.mc-nav-item .v-icon {
  color: rgba(255, 255, 255, 0.5) !important;
}
.mc-nav-item:hover {
  background: rgba(255, 255, 255, 0.07) !important;
  color: white !important;
}
.mc-nav-item:hover .v-icon {
  color: rgba(255, 255, 255, 0.85) !important;
}
.mc-nav-active {
  background: #1565C0 !important;
  color: white !important;
}
.mc-nav-active .v-icon {
  color: white !important;
}
</style>
