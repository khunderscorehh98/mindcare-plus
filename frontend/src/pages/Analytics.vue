<template>
  <default-layout>
    <template #header>
      <v-row align="center">
        <v-col cols="12" md="8">
          <h2 class="subtitle-1 mb-0">Wellness Analytics</h2>
          <div class="text-caption grey--text">
            Private to you • Trends from check-ins and sessions
          </div>
        </v-col>
        <v-col cols="12" md="4" class="text-md-right mt-2 mt-md-0">
          <v-btn color="primary" @click="refresh" :loading="loading">
            <v-icon left>mdi-refresh</v-icon> Refresh
          </v-btn>
        </v-col>
      </v-row>
    </template>

    <!-- KPI row -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <v-card outlined class="rounded-xl">
          <v-card-text class="py-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-speedometer</v-icon>
              <div>
                <div class="text-caption grey--text">Avg. stress (7d)</div>
                <div class="text-h6">{{ avgStressDisplay }}</div>
              </div>
            </div>
            <div v-if="!checkins.length" class="text-caption grey--text mt-2">
              No check-ins yet
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined class="rounded-xl">
          <v-card-text class="py-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-emoticon-outline</v-icon>
              <div>
                <div class="text-caption grey--text">Last mood</div>
                <div class="text-h6">{{ lastMood || '—' }}</div>
              </div>
            </div>
            <div v-if="!checkins.length" class="text-caption grey--text mt-2">
              No check-ins yet
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined class="rounded-xl">
          <v-card-text class="py-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-message-text</v-icon>
              <div>
                <div class="text-caption grey--text">Chat sessions</div>
                <div class="text-h6">{{ sessions.length }}</div>
              </div>
            </div>
            <div v-if="!sessions.length" class="text-caption grey--text mt-2">
              No sessions yet
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card outlined class="rounded-xl">
          <v-card-text class="py-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-account-heart</v-icon>
              <div>
                <div class="text-caption grey--text">Upcoming bookings</div>
                <div class="text-h6">{{ upcomingCount }}</div>
              </div>
            </div>
            <div v-if="!upcomingCount" class="text-caption grey--text mt-2">
              No bookings yet
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts -->
    <v-row class="mt-2">
      <v-col cols="12" md="6">
        <v-card outlined class="rounded-xl">
          <v-card-title>
            <v-icon left color="primary">mdi-chart-line</v-icon>
            Stress trend (last 7)
            <v-spacer />
            <span class="text-caption grey--text">0 low — 10 high</span>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <template v-if="checkins.length">
              <v-sparkline
                :value="stressValues"
                :smooth="8"
                :line-width="2"
                :padding="8"
                auto-draw
              />
              <div class="text-caption grey--text mt-1">{{ stressDatesLabel }}</div>
            </template>
            <div v-else class="text-caption grey--text">
              No data yet — log a few check-ins to see a trend.
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card outlined class="rounded-xl">
          <v-card-title>
            <v-icon left color="primary">mdi-chart-areaspline</v-icon>
            Mood frequency (last 7)
          </v-card-title>
          <v-divider />
          <v-card-text>
            <template v-if="moodCountsList.length">
              <div class="text-caption grey--text mb-2">Top moods</div>
              <v-chip
                v-for="(m,i) in moodCountsList"
                :key="i"
                small
                class="mr-2 mb-2"
                color="grey lighten-3"
                label
              >
                {{ m.label }} — {{ m.count }}
              </v-chip>
            </template>
            <div v-else class="text-caption grey--text">
              No data yet — moods will appear after your first check-in.
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent list -->
    <v-row class="mt-2">
      <v-col cols="12" md="7">
        <v-card outlined class="rounded-xl">
          <v-card-title>
            <v-icon left color="primary">mdi-clipboard-text</v-icon>
            Recent check-ins
          </v-card-title>
          <v-divider />
          <v-list two-line v-if="checkins.length">
            <v-list-item v-for="c in checkins" :key="c.id">
              <v-list-item-avatar color="primary" class="white--text">
                <span class="subtitle-1">{{ c.stress_level }}</span>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title class="font-weight-medium">{{ c.mood }}</v-list-item-title>
                <v-list-item-subtitle>{{ fmtDateTime(c.created_at) }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
          <v-card-text v-else class="text-body-2 grey--text">
            No check-ins yet.
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card outlined class="rounded-xl">
          <v-card-title>
            <v-icon left color="primary">mdi-calendar</v-icon>
            Upcoming bookings
          </v-card-title>
          <v-divider />
          <v-list v-if="upcoming.length">
            <v-list-item v-for="b in upcoming" :key="b.id">
              <v-list-item-content>
                <v-list-item-title class="font-weight-medium">
                  {{ b.counselor.full_name }}
                </v-list-item-title>
                <v-list-item-subtitle class="grey--text">
                  {{ fmtDate(b.slot.start_time) }} • {{ fmtTime(b.slot.start_time) }}–{{ fmtTime(b.slot.end_time) }}
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-chip small :color="statusColor(b.status)" text-color="white" label>{{ b.status }}</v-chip>
            </v-list-item>
          </v-list>
          <v-card-text v-else class="text-body-2 grey--text">
            No bookings yet.
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn small text color="primary" @click="$router.push('/consult')">
              Manage
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </default-layout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/apiClient'

export default {
  name: 'Analytics',
  components: { DefaultLayout },
  data: () => ({
    loading: false,
    checkins: [],
    sessions: [],
    bookings: [],
  }),
  computed: {
    // stress
    stressValues () { return this.checkins.map(c => Number(c.stress_level || 0)).reverse() },
    stressDatesLabel () {
      if (!this.checkins.length) return 'No recent check-ins'
      const first = this.checkins[this.checkins.length - 1]
      const last = this.checkins[0]
      return `${this.fmtShortDate(first.created_at)} — ${this.fmtShortDate(last.created_at)}`
    },
    avgStressDisplay () {
      if (!this.checkins.length) return '—'
      const n = this.checkins.length
      const sum = this.checkins.reduce((a, c) => a + Number(c.stress_level || 0), 0)
      return (sum / n).toFixed(1)
    },
    lastMood () {
      return this.checkins.length ? (this.checkins[0].mood || '') : ''
    },

    // mood counts
    moodCounts () {
      const m = {}
      this.checkins.forEach(c => {
        const k = (c.mood || '').trim().toLowerCase()
        if (!k) return
        m[k] = (m[k] || 0) + 1
      })
      return m
    },
    moodCountsList () {
      return Object.entries(this.moodCounts)
        .map(([label, count]) => ({ label, count }))
        .sort((a,b) => b.count - a.count)
        .slice(0, 6)
    },

    // bookings
    upcoming () {
      const now = new Date()
      return (this.bookings || []).filter(b => new Date(b.slot.start_time) > now)
        .sort((a,b) => new Date(a.slot.start_time) - new Date(b.slot.start_time))
        .slice(0, 5)
    },
    upcomingCount () { return this.upcoming.length },
  },
  async created () {
    await this.refresh()
  },
  methods: {
    async refresh () {
      this.loading = true
      try {
        const [checkins] = await Promise.all([
          api.getRecentCheckIns(7).catch(() => []),
        ])
        this.checkins = Array.isArray(checkins) ? checkins : []

        // sessions & bookings
        this.sessions = await this.safeGet('/chat/sessions')
        this.bookings = await this.safeGet('/bookings/my')
      } finally {
        this.loading = false
      }
    },
    async safeGet (path) {
      try {
        const { data } = await api.api.get(path)
        return data || []
      } catch {
        return []
      }
    },
    // fmt
    fmtDateTime (ts) { try { return new Date(ts).toLocaleString() } catch { return ts } },
    fmtShortDate (ts) { try { return new Date(ts).toLocaleDateString() } catch { return ts } },
    fmtDate (ts) { try { return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) } catch { return ts } },
    fmtTime (ts) { try { return new Date(ts).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return ts } },
    statusColor (s) {
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
/* minimal extra styling if needed */
</style>