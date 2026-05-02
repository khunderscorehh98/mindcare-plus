<template>
  <default-layout>

    <!-- Page header -->
    <template v-slot:header>
      <div class="mc-page-header d-flex align-center justify-space-between flex-wrap" style="gap: 12px">
        <div>
          <div class="d-flex align-center mb-1">
            <v-avatar color="primary" size="38" class="mr-3 elevation-1">
              <span class="white--text font-weight-bold" style="font-size: 15px">{{ initials }}</span>
            </v-avatar>
            <div>
              <h2 style="font-size: 18px; font-weight: 600; color: #1A2332; margin: 0">
                Good {{ greeting }}, <span class="primary--text">{{ firstName }}</span>
              </h2>
              <div style="font-size: 12px; color: #546E7A">
                {{ todayLabel }} &bull;
                <v-chip x-small label :color="plan === 'premium' ? '#E8F5E9' : '#F5F5F5'" style="height: 18px; font-size: 10px; font-weight: 600" :style="{ color: plan === 'premium' ? '#2E7D32' : '#546E7A' }">
                  {{ plan === 'premium' ? 'Premium' : 'Free plan' }}
                </v-chip>
              </div>
            </div>
          </div>
        </div>
        <div class="d-flex" style="gap: 8px">
          <v-btn outlined color="error" small @click="$router.push('/crisis')">
            <v-icon left small>mdi-phone-alert</v-icon>Get Help Now
          </v-btn>
          <v-btn color="primary" depressed small @click="$router.push('/chat')">
            <v-icon left small>mdi-chat-outline</v-icon>New Chat
          </v-btn>
        </div>
      </div>
    </template>

    <!-- KPI cards -->
    <v-row class="mb-2">
      <v-col cols="12" sm="6" md="3">
        <v-card class="mc-metric-card" elevation="1">
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-3">
              <span style="font-size: 12px; font-weight: 600; color: #546E7A; text-transform: uppercase; letter-spacing: 0.5px">Last Mood</span>
              <div style="width: 32px; height: 32px; border-radius: 8px; background: #E3F2FD; display: flex; align-items: center; justify-content: center">
                <v-icon small color="primary">mdi-emoticon-outline</v-icon>
              </div>
            </div>
            <div style="font-size: 22px; font-weight: 700; color: #1A2332">{{ lastMood || '—' }}</div>
            <div style="font-size: 12px; color: #90A4AE; margin-top: 2px">from latest check-in</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="mc-metric-card teal-accent" elevation="1">
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-3">
              <span style="font-size: 12px; font-weight: 600; color: #546E7A; text-transform: uppercase; letter-spacing: 0.5px">Avg. Stress (7d)</span>
              <div style="width: 32px; height: 32px; border-radius: 8px; background: #E0F2F1; display: flex; align-items: center; justify-content: center">
                <v-icon small color="teal darken-1">mdi-speedometer</v-icon>
              </div>
            </div>
            <div style="font-size: 22px; font-weight: 700; color: #1A2332">
              {{ avgStressDisplay !== '—' ? avgStressDisplay : '—' }}
              <span v-if="avgStressDisplay !== '—'" style="font-size: 14px; color: #546E7A">/10</span>
            </div>
            <div style="font-size: 12px; color: #90A4AE; margin-top: 2px">{{ checkins.length }} check-ins recorded</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="1" style="border-radius: 8px">
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-2">
              <span style="font-size: 12px; font-weight: 600; color: #546E7A; text-transform: uppercase; letter-spacing: 0.5px">Stress Trend</span>
              <span style="font-size: 11px; color: #90A4AE">{{ stressDatesLabel }}</span>
            </div>
            <v-sparkline
              v-if="checkins.length"
              :value="stressValues"
              :smooth="8"
              :line-width="2"
              :padding="4"
              color="#1565C0"
              auto-draw
              height="52"
            />
            <div v-else class="d-flex align-center justify-center" style="height: 52px; color: #B0BEC5; font-size: 13px">
              <v-icon small class="mr-1" color="grey lighten-2">mdi-chart-line</v-icon>
              No data yet — start a check-in
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upcoming booking + Recent sessions -->
    <v-row class="mb-2">
      <v-col cols="12" md="5">
        <v-card elevation="1" class="mc-section-card" style="height: 100%">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-stethoscope</v-icon>
            <span style="font-size: 14px; font-weight: 600; color: #1A2332">Upcoming Consultation</span>
            <v-spacer />
            <v-chip v-if="plan !== 'premium'" x-small label color="#FFF8E1" style="color: #E65100; font-size: 10px; font-weight: 700">PRO</v-chip>
          </div>

          <v-card-text v-if="bookingLoading" class="pa-4">
            <v-skeleton-loader type="list-item-two-line" />
          </v-card-text>

          <v-card-text v-else-if="nextBooking" class="pa-4">
            <div class="d-flex align-start">
              <div style="width: 40px; height: 40px; border-radius: 8px; background: #E3F2FD; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 12px">
                <v-icon color="primary">mdi-account-tie</v-icon>
              </div>
              <div>
                <div style="font-size: 14px; font-weight: 600; color: #1A2332">{{ nextBooking.counselor.full_name }}</div>
                <div style="font-size: 12px; color: #546E7A; margin-top: 2px">
                  <v-icon x-small class="mr-1">mdi-calendar</v-icon>{{ fmtDate(nextBooking.slot.start_time) }}
                </div>
                <div style="font-size: 12px; color: #546E7A">
                  <v-icon x-small class="mr-1">mdi-clock-outline</v-icon>{{ fmtTime(nextBooking.slot.start_time) }} – {{ fmtTime(nextBooking.slot.end_time) }}
                </div>
                <v-chip x-small label class="mt-2" :class="statusClass(nextBooking.status)">
                  {{ nextBooking.status }}
                </v-chip>
              </div>
            </div>
            <v-btn small outlined color="primary" class="mt-3" @click="$router.push('/consult')">
              <v-icon left small>mdi-calendar-check</v-icon>Manage bookings
            </v-btn>
          </v-card-text>

          <v-card-text v-else class="pa-4">
            <div style="color: #546E7A; font-size: 13.5px; margin-bottom: 12px">No upcoming consultations scheduled.</div>
            <v-btn small depressed color="primary" @click="$router.push('/consult')">
              <v-icon left small>mdi-plus</v-icon>Book now
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="7">
        <v-card elevation="1" class="mc-section-card" style="height: 100%">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-chat-outline</v-icon>
            <span style="font-size: 14px; font-weight: 600; color: #1A2332">Recent Chat Sessions</span>
            <v-spacer />
            <v-btn text x-small color="primary" style="font-size: 12px; font-weight: 500" @click="$router.push('/chat')">
              View all
            </v-btn>
          </div>

          <v-card-text v-if="sessionsLoading" class="pa-4">
            <v-skeleton-loader type="list-item-two-line" />
          </v-card-text>

          <div v-else>
            <div
              v-for="s in sessions"
              :key="s.id"
              class="mc-session-row d-flex align-center px-4 py-3"
              style="border-bottom: 1px solid #F4F7FC; cursor: pointer"
              @click="$router.push({ name: 'chat', query: { session: s.id } })"
            >
              <div style="width: 34px; height: 34px; border-radius: 8px; background: #E3F2FD; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 12px">
                <v-icon small color="primary">mdi-message-outline</v-icon>
              </div>
              <div style="flex: 1; min-width: 0">
                <div style="font-size: 13.5px; font-weight: 500; color: #1A2332; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ s.title }}</div>
                <div style="font-size: 12px; color: #90A4AE">{{ fmtDateTime(s.created_at) }}</div>
              </div>
              <v-icon small color="grey lighten-2">mdi-chevron-right</v-icon>
            </div>

            <div v-if="!sessions.length" class="pa-4" style="color: #90A4AE; font-size: 13.5px; text-align: center">
              No sessions yet.
              <v-btn text x-small color="primary" @click="$router.push('/chat')">Start one</v-btn>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick actions + disclaimer -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card elevation="1" class="mc-section-card">
          <div class="px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <span style="font-size: 14px; font-weight: 600; color: #1A2332">Quick Actions</span>
          </div>
          <div>
            <div
              v-for="action in quickActions"
              :key="action.label"
              class="mc-action-row d-flex align-center px-4 py-3"
              style="border-bottom: 1px solid #F4F7FC; cursor: pointer"
              @click="$router.push(action.to)"
            >
              <div :style="{ background: action.bg, width: '34px', height: '34px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginRight: '12px' }">
                <v-icon small :color="action.color">{{ action.icon }}</v-icon>
              </div>
              <div>
                <div style="font-size: 13.5px; font-weight: 500; color: #1A2332">{{ action.label }}</div>
                <div style="font-size: 12px; color: #90A4AE">{{ action.sub }}</div>
              </div>
              <v-spacer />
              <v-icon small color="grey lighten-2">mdi-chevron-right</v-icon>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card elevation="1" class="mc-section-card" style="border-left: 3px solid #0277BD">
          <v-card-text class="pa-4 d-flex align-start">
            <v-icon color="info" class="mr-3 mt-1">mdi-information-outline</v-icon>
            <div>
              <div style="font-size: 13.5px; font-weight: 600; color: #1A2332; margin-bottom: 4px">Important notice</div>
              <div style="font-size: 13px; color: #546E7A; line-height: 1.6">
                MindCare+ is an educational prototype and is <strong>not a registered medical device</strong>. It does not replace professional psychiatric or psychological care. In a mental health emergency, please contact your local emergency services immediately.
              </div>
            </div>
          </v-card-text>
        </v-card>
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
    quickActions: [
      { icon: 'mdi-clipboard-pulse-outline', label: 'Log a check-in',     sub: 'Track mood & stress',           to: '/checkin',   bg: '#E0F2F1', color: 'teal darken-1' },
      { icon: 'mdi-book-open-outline',        label: 'Browse resources',   sub: 'Coping strategies & support',   to: '/resources', bg: '#E8EAF6', color: 'indigo darken-1' },
      { icon: 'mdi-stethoscope',              label: 'Book consultation',  sub: 'Licensed professionals',        to: '/consult',   bg: '#E3F2FD', color: 'primary' },
    ],
  }),
  computed: {
    ...mapGetters(['user', 'plan']),
    userEmail ()        { return this.user && this.user.email || '' },
    initials ()         { return this.userEmail ? this.userEmail.charAt(0).toUpperCase() : '?' },
    firstName ()        { const e = this.userEmail; return e ? e.split('@')[0] : 'there' },
    greeting ()         { const h = new Date().getHours(); return h < 12 ? 'morning' : h < 17 ? 'afternoon' : 'evening' },
    todayLabel ()       { return new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' }) },
    stressValues ()     { return this.checkins.map(c => Number(c.stress_level || 0)).reverse() },
    stressDatesLabel () {
      if (!this.checkins.length) return 'No data'
      const first = this.checkins[this.checkins.length - 1]
      const last  = this.checkins[0]
      return `${this.fmtShortDate(first.created_at)} – ${this.fmtShortDate(last.created_at)}`
    },
    lastMood ()         { return this.checkins.length ? (this.checkins[0].mood || '') : '' },
    avgStressDisplay () {
      if (!this.checkins.length) return '—'
      const sum = this.checkins.reduce((a, c) => a + Number(c.stress_level || 0), 0)
      return (sum / this.checkins.length).toFixed(1)
    },
  },
  async created () { this.fetchAll() },
  methods: {
    async fetchAll () {
      this.loading = true
      try {
        const [checkins] = await Promise.all([api.getRecentCheckIns(7).catch(() => [])])
        this.checkins = Array.isArray(checkins) ? checkins : []
        this.fetchSessions()
        this.fetchNextBooking()
      } finally {
        this.loading = false
      }
    },
    async fetchSessions () {
      this.sessionsLoading = true
      try {
        const rows = await api.api.get('/chat/sessions').then(r => r.data)
        this.sessions = Array.isArray(rows) ? rows.slice(0, 5) : []
      } catch { this.sessions = [] } finally { this.sessionsLoading = false }
    },
    async fetchNextBooking () {
      this.bookingLoading = true
      try {
        const mine = await api.api.get('/bookings/my').then(r => r.data || [])
        const upcoming = (mine || []).filter(b => new Date(b.slot.start_time) > new Date())
        this.nextBooking = upcoming.sort((a, b) => new Date(a.slot.start_time) - new Date(b.slot.start_time))[0] || null
      } catch { this.nextBooking = null } finally { this.bookingLoading = false }
    },
    statusClass (s) {
      switch ((s || '').toLowerCase()) {
        case 'confirmed': return 'mc-status-confirmed'
        case 'pending':   return 'mc-status-pending'
        case 'cancelled': return 'mc-status-cancelled'
        default:          return ''
      }
    },
    fmtDateTime (ts)  { try { return new Date(ts).toLocaleString() } catch { return ts } },
    fmtShortDate (ts) { try { return new Date(ts).toLocaleDateString() } catch { return ts } },
    fmtDate (ts)      { try { return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) } catch { return ts } },
    fmtTime (ts)      { try { return new Date(ts).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return ts } },
  },
}
</script>

<style scoped>
.mc-session-row:hover,
.mc-action-row:hover { background: #F4F7FC; }
</style>
