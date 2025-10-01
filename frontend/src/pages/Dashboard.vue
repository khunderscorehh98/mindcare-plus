<template>
  <default-layout>
    <!-- Header -->
    <template v-slot:header>
      <v-row class="mb-4" align="center">
        <v-col cols="12" md="8">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="40" class="mr-3 white--text">
              <v-icon dark>mdi-account</v-icon>
            </v-avatar>
            <div>
              <h2 class="subtitle-1 mb-0">
                Welcome back, <strong>{{ userEmail || 'there' }}</strong>
              </h2>
              <div class="text-caption grey--text">
                Plan:
                <v-chip x-small :color="planColor" :text-color="planText" class="text-uppercase" label>
                  {{ plan }}
                </v-chip>
              </div>
            </div>
          </div>
        </v-col>

        <v-col cols="12" md="4" class="text-md-right mt-2 mt-md-0">
          <v-btn color="red darken-1" dark class="mr-2" @click="$router.push('/crisis')">
            <v-icon left>mdi-alert</v-icon> Get Help Now
          </v-btn>
          <v-btn color="primary" dark @click="$router.push('/chat')">
            <v-icon left>mdi-chat</v-icon> New Chat
          </v-btn>
        </v-col>
      </v-row>
    </template>
    <!-- KPIs -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <v-card outlined class="rounded-xl">
          <v-card-text class="py-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-emoticon-outline</v-icon>
              <div>
                <div class="text-caption grey--text">Last mood</div>
                <div class="text-h6">{{ lastMood || 'No data yet' }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined class="rounded-xl">
          <v-card-text class="py-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-speedometer</v-icon>
              <div>
                <div class="text-caption grey--text">Avg. stress (7d)</div>
                <div class="text-h6">
                  {{ avgStressDisplay !== '—' ? avgStressDisplay : 'No data yet' }}
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card outlined class="rounded-xl">
          <v-card-text class="py-4">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="text-subtitle-2">Stress trend (recent)</div>
              <div class="text-caption grey--text">0 (low) — 10 (high)</div>
            </div>
            <v-sparkline
              v-if="checkins.length"
              :value="stressValues"
              :smooth="8"
              :line-width="2"
              :padding="8"
              auto-draw
            />
            <div v-else class="text-caption grey--text">No data yet</div>
            <div class="text-caption grey--text mt-1">{{ stressDatesLabel }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upcoming booking -->
    <v-row class="mt-2">
      <v-col cols="12" md="6" lg="5">
        <v-card outlined class="rounded-xl">
          <v-card-title>
            <v-icon left color="primary">mdi-account-heart</v-icon>
            Upcoming Consultation
            <v-spacer />
            <v-chip v-if="plan !== 'premium'" x-small color="amber lighten-4" label>Pro</v-chip>
          </v-card-title>
          <v-divider />

          <v-card-text v-if="bookingLoading">
            <v-skeleton-loader type="list-item-two-line" />
          </v-card-text>

          <v-card-text v-else-if="nextBooking">
            <div class="mb-1 text-subtitle-2">{{ nextBooking.counselor.full_name }}</div>
            <div class="text-body-2 grey--text mb-2">
              <v-icon x-small class="mr-1">mdi-calendar</v-icon>
              {{ fmtDate(nextBooking.slot.start_time) }} •
              <v-icon x-small class="mx-1">mdi-clock-outline</v-icon>
              {{ fmtTime(nextBooking.slot.start_time) }}–{{ fmtTime(nextBooking.slot.end_time) }}
            </div>
            <v-chip small :color="statusColor(nextBooking.status)" text-color="white" class="mb-2" label>
              {{ nextBooking.status }}
            </v-chip>
            <div class="mt-2">
              <v-btn small color="primary" class="mr-2" @click="$router.push('/consult')">
                <v-icon left small>mdi-calendar-check</v-icon>
                Manage bookings
              </v-btn>
            </div>
          </v-card-text>

          <v-card-text v-else class="text-body-2">
            No upcoming bookings yet.
            <v-btn small color="primary" class="ml-1" @click="$router.push('/consult')">
              Book now
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent chat sessions -->
      <v-col cols="12" md="6" lg="7">
        <v-card outlined class="rounded-xl">
          <v-card-title>
            <v-icon left color="primary">mdi-message-text</v-icon>
            Recent Chat Sessions
            <v-spacer />
            <v-btn small text color="primary" @click="$router.push('/chat')">
              View chat
            </v-btn>
          </v-card-title>
          <v-divider />

          <v-card-text v-if="sessionsLoading">
            <v-skeleton-loader type="table" />
          </v-card-text>

          <v-list v-else two-line>
            <template v-if="sessions.length">
              <v-list-item
                v-for="s in sessions"
                :key="s.id"
                @click="$router.push({ name: 'chat', query: { session: s.id } })"
                class="session-item"
              >
                <v-list-item-avatar color="primary" class="white--text">
                  <v-icon dark>mdi-message</v-icon>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title class="font-weight-medium">
                    {{ s.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="grey--text">
                    {{ fmtDateTime(s.created_at) }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-icon>
                  <v-icon>mdi-chevron-right</v-icon>
                </v-list-item-icon>
              </v-list-item>
            </template>

            <v-list-item v-else>
              <v-list-item-content>
                <v-list-item-title class="text-body-2">
                  No chat sessions yet. Start a conversation to create your first session.
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick actions -->
    <v-row class="mt-2">
      <v-col cols="12" md="4">
        <v-card outlined class="rounded-xl">
          <v-list two-line>
            <v-subheader>Quick Actions</v-subheader>
            <v-list-item @click="$router.push('/checkin')">
              <v-list-item-avatar tile color="teal" class="white--text">
                <v-icon dark>mdi-clipboard-check</v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>Log a check-in</v-list-item-title>
                <v-list-item-subtitle>Track mood & stress</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>

            <v-list-item @click="$router.push('/resources')">
              <v-list-item-avatar tile color="indigo" class="white--text">
                <v-icon dark>mdi-book-open-variant</v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>Browse resources</v-list-item-title>
                <v-list-item-subtitle>Learn coping strategies</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>

            <v-list-item @click="$router.push('/consult')">
              <v-list-item-avatar tile color="deep-purple accent-4" class="white--text">
                <v-icon dark>mdi-account-heart</v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>Book consultation</v-list-item-title>
                <v-list-item-subtitle>Licensed professionals</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-alert dense outlined type="info" border="left" class="rounded-xl">
          MindCare+ is an educational prototype. It is not a medical device and doesn’t replace professional care.
          In an emergency, contact local services immediately.
        </v-alert>
      </v-col>
    </v-row>
  </default-layout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/apiClient'
import { mapGetters } from 'vuex'

export default {
  name: 'Dashboard',
  components: { DefaultLayout },
  data: () => ({
    checkins: [],
    sessions: [],
    nextBooking: null,
    loading: false,
    sessionsLoading: false,
    bookingLoading: false,
  }),
  computed: {
    ...mapGetters(['user', 'plan']),
    userEmail() { return this.user && this.user.email },
    planColor() { return this.plan === 'premium' ? 'deep-purple accent-4' : 'grey lighten-3' },
    planText() { return this.plan === 'premium' ? 'white' : 'black' },
    stressValues() {
      return this.checkins.map(c => Number(c.stress_level || 0)).reverse()
    },
    stressDatesLabel() {
      if (!this.checkins.length) return 'No recent check-ins'
      const first = this.checkins[this.checkins.length - 1]
      const last = this.checkins[0]
      return `${this.fmtShortDate(first.created_at)} — ${this.fmtShortDate(last.created_at)}`
    },
    lastMood() {
      return this.checkins.length ? (this.checkins[0].mood || '') : ''
    },
    avgStressDisplay() {
      if (!this.checkins.length) return '—'
      const n = this.checkins.length
      const sum = this.checkins.reduce((a, c) => a + Number(c.stress_level || 0), 0)
      return (sum / n).toFixed(1)
    },
  },
  async created() {
    this.fetchAll()
  },
  methods: {
    async fetchAll() {
      this.loading = true
      try {
        const [checkins] = await Promise.all([
          api.getRecentCheckIns(7).catch(() => []),
        ])
        this.checkins = Array.isArray(checkins) ? checkins : []
        this.fetchSessions()
        this.fetchNextBooking()
      } finally {
        this.loading = false
      }
    },
    async fetchSessions() {
      this.sessionsLoading = true
      try {
        const rows = await api.api.get('/chat/sessions').then(r => r.data)
        this.sessions = Array.isArray(rows) ? rows.slice(0, 5) : []
      } catch (e) {
        this.sessions = []
      } finally {
        this.sessionsLoading = false
      }
    },
    async fetchNextBooking() {
      this.bookingLoading = true
      try {
        const mine = await api.api.get('/bookings/my').then(r => r.data || [])
        const upcoming = (mine || []).filter(b => new Date(b.slot.start_time) > new Date())
        this.nextBooking = upcoming.sort((a, b) =>
          new Date(a.slot.start_time) - new Date(b.slot.start_time)
        )[0] || null
      } catch (e) {
        this.nextBooking = null
      } finally {
        this.bookingLoading = false
      }
    },
    fmtDateTime(ts) {
      try { return new Date(ts).toLocaleString() } catch { return ts }
    },
    fmtShortDate(ts) {
      try { return new Date(ts).toLocaleDateString() } catch { return ts }
    },
    fmtDate(ts) {
      try { return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) } catch { return ts }
    },
    fmtTime(ts) {
      try { return new Date(ts).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return ts }
    },
    statusColor(s) {
      switch ((s || '').toLowerCase()) {
        case 'confirmed': return 'green'
        case 'pending': return 'amber'
        case 'cancelled': return 'red'
        default: return 'grey'
      }
    },
  },
}
</script>

<style scoped>
.session-item { cursor: pointer; }
</style>