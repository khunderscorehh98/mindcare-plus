<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar
      app
      flat
      color="white"
      class="mc-appbar"
      :dense="isMobile"
      elevate-on-scroll
    >
      <v-app-bar-nav-icon class="d-md-none" @click.stop="drawer = !drawer" />

      <v-toolbar-title class="font-weight-bold">
        <span class="primary--text">MindCare+</span>
      </v-toolbar-title>

      <v-spacer />

      <!-- Crisis: icon on mobile, full button on desktop -->
      <v-btn
        v-if="!isMobile"
        color="red darken-1"
        dark
        class="text-none mr-2"
        @click="helpDialog = true"
      >
        <v-icon left>mdi-alert</v-icon> Get Help Now
      </v-btn>
      <v-btn
        v-else
        icon
        color="red darken-1"
        @click="helpDialog = true"
        aria-label="Get help now"
      >
        <v-icon>mdi-alert</v-icon>
      </v-btn>

      <!-- Account menu -->
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
      :temporary="isMobile"
      :permanent="!isMobile"
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

        <v-divider class="mb-2" />

        <v-list-item
          v-for="(item, i) in sideItems"
          :key="i"
          :to="item.to"
          exact
          link
          @click="isMobile ? drawer = false : null"
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
      <div class="mc-container">
        <slot name="header"></slot>
        <slot />
        <slot name="footer"></slot>
      </div>
    </v-main>

    <!-- Footer -->
    <v-footer app padless color="white">
      <div class="mc-container py-2 text-caption grey--text text--darken-1">
        <div class="d-flex align-center">
          <div>&copy; {{ new Date().getFullYear() }} MindCare+. For education/demo only — not a medical device.</div>
          <v-spacer />
          <div class="d-none d-sm-block">
            <a
              href="https://www.healthline.com/health/mental-health/hotlines"
              target="_blank"
              rel="noopener"
            >Global helplines</a>
          </div>
        </div>
      </div>
    </v-footer>

    <!-- Crisis confirm dialog -->
    <v-dialog v-model="helpDialog" max-width="520" persistent>
      <v-card class="rounded-xl">
        <v-card-title class="text-h6 font-weight-bold">
          Urgent help
        </v-card-title>

        <v-card-text class="pt-2">
          <v-alert type="warning" dense outlined border="left" class="mb-4">
            This action can initiate a direct phone call to a helpline.
          </v-alert>

          <p class="mb-3">
            If you’re in immediate danger, please call your local emergency number.
          </p>

          <v-list dense two-line class="rounded-lg">
            <v-list-item
              v-for="(h, i) in helplines"
              :key="i"
              @click="callNumber(h.number)"
            >
              <v-list-item-avatar color="red darken-1" size="36">
                <v-icon color="white">mdi-phone</v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title class="font-weight-medium">
                  {{ h.label }}
                </v-list-item-title>
                <v-list-item-subtitle class="grey--text text--darken-1">
                  {{ h.number }}
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-btn icon :aria-label="`Call ${h.label}`">
                  <v-icon>mdi-arrow-right</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </v-list>

          <p class="mt-4 mb-0 text-caption grey--text">
            Not an emergency? You can also view our help page with more options.
          </p>
        </v-card-text>

        <v-card-actions class="px-4 pb-4">
          <v-spacer />
          <v-btn text class="text-none" @click="helpDialog = false">Cancel</v-btn>
          <v-btn color="primary" class="text-none" @click="goCrisis">
            View help page
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'DefaultLayout',
  data: () => ({
    drawer: true,
    showUpgradeBadge: true,
    helpDialog: false,
    // Replace with verified local numbers for your region
    helplines: [
      { label: 'Emergency Services', number: '999' },
      { label: 'Mental Health Support', number: '+673-XXX-XXXX' },
    ],
    items: [
      { text: 'Dashboard',    icon: 'mdi-view-dashboard',    to: '/dashboard' },
      { text: 'Chat',         icon: 'mdi-chat',              to: '/chat' },
      { text: 'Check-ins',    icon: 'mdi-clipboard-check',   to: '/checkin' },
      { text: 'Resources',    icon: 'mdi-book-open-variant', to: '/resources' },
      { text: 'Consultation', icon: 'mdi-account-heart',     to: '/consult',  premium: true },
      { text: 'Analytics',    icon: 'mdi-chart-line',        to: '/analytics', premium: true, badge: true },
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
    isMobile () {
      return this.$vuetify.breakpoint.smAndDown
    },
    sideItems () {
      if (this.plan === 'premium') return this.items
      return this.items.filter(i => !i.premium)
    },
  },
  created () {
    this.drawer = !this.isMobile
  },
  methods: {
    ...mapActions(['logout']),
    goRoute (to) { this.$router.push(to).catch(() => {}) },
    goCrisis () {
      this.helpDialog = false
      this.$router.push('/crisis').catch(() => {})
    },
    callNumber (num) {
      this.helpDialog = false
      setTimeout(() => { window.location.href = `tel:${num}` }, 120)
    },
    async logout () {
      await this.$store.dispatch('logout')
      this.$router.push('/login').catch(() => {})
    },
  },
}
</script>

<style scoped>
.text-none { text-transform: none; }
.mc-main { padding-top: 16px; }
.mc-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 24px 16px;
}
.mc-drawer { border-right: 1px solid rgba(0,0,0,0.06); }
.mc-appbar { border-bottom: 1px solid rgba(0,0,0,0.06); }
</style>