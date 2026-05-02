<template>
  <default-layout>
    <template #header>
      <div class="mc-page-header d-flex align-center justify-space-between flex-wrap" style="gap: 12px">
        <div>
          <h2 style="font-size: 18px; font-weight: 600; color: #1A2332; margin: 0 0 2px">Wellness Analytics</h2>
          <div class="subtitle" style="color: #546E7A; font-size: 13px">Private to you • Trends from check-ins and sessions</div>
        </div>
        <v-btn outlined small color="primary" :loading="loading" @click="refresh">
          <v-icon left small>mdi-refresh</v-icon>Refresh
        </v-btn>
      </div>
    </template>

    <!-- KPI row -->
    <v-row class="mb-2">
      <v-col cols="12" sm="6" md="3">
        <v-card class="mc-metric-card teal-accent" elevation="1">
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-3">
              <span style="font-size: 11px; font-weight: 600; color: #546E7A; text-transform: uppercase; letter-spacing: 0.5px">Avg Stress (7d)</span>
              <div style="width: 30px; height: 30px; border-radius: 8px; background: #E0F2F1; display: flex; align-items: center; justify-content: center">
                <v-icon x-small color="teal darken-1">mdi-speedometer</v-icon>
              </div>
            </div>
            <div style="font-size: 24px; font-weight: 700; color: #1A2332">
              {{ avgStressDisplay }}<span v-if="avgStressDisplay !== '—'" style="font-size: 14px; color: #546E7A">/10</span>
            </div>
            <div style="font-size: 12px; color: #90A4AE">{{ checkins.length }} check-ins</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="mc-metric-card" elevation="1">
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-3">
              <span style="font-size: 11px; font-weight: 600; color: #546E7A; text-transform: uppercase; letter-spacing: 0.5px">Last Mood</span>
              <div style="width: 30px; height: 30px; border-radius: 8px; background: #E3F2FD; display: flex; align-items: center; justify-content: center">
                <v-icon x-small color="primary">mdi-emoticon-outline</v-icon>
              </div>
            </div>
            <div style="font-size: 22px; font-weight: 700; color: #1A2332; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ lastMood || '—' }}</div>
            <div style="font-size: 12px; color: #90A4AE">most recent entry</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="mc-metric-card orange-accent" elevation="1">
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-3">
              <span style="font-size: 11px; font-weight: 600; color: #546E7A; text-transform: uppercase; letter-spacing: 0.5px">Chat Sessions</span>
              <div style="width: 30px; height: 30px; border-radius: 8px; background: #FFF8E1; display: flex; align-items: center; justify-content: center">
                <v-icon x-small color="orange darken-2">mdi-chat-outline</v-icon>
              </div>
            </div>
            <div style="font-size: 24px; font-weight: 700; color: #1A2332">{{ sessions.length }}</div>
            <div style="font-size: 12px; color: #90A4AE">total sessions</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="mc-metric-card green-accent" elevation="1">
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between mb-3">
              <span style="font-size: 11px; font-weight: 600; color: #546E7A; text-transform: uppercase; letter-spacing: 0.5px">Upcoming</span>
              <div style="width: 30px; height: 30px; border-radius: 8px; background: #E8F5E9; display: flex; align-items: center; justify-content: center">
                <v-icon x-small color="green darken-2">mdi-calendar-check</v-icon>
              </div>
            </div>
            <div style="font-size: 24px; font-weight: 700; color: #1A2332">{{ upcomingCount }}</div>
            <div style="font-size: 12px; color: #90A4AE">consultation{{ upcomingCount !== 1 ? 's' : '' }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts row -->
    <v-row class="mb-2">
      <v-col cols="12" md="6">
        <v-card elevation="1" class="mc-section-card">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-chart-line</v-icon>
            <span style="font-size: 13.5px; font-weight: 600; color: #1A2332">Stress Trend</span>
            <v-spacer />
            <span style="font-size: 11px; color: #90A4AE">0 = low • 10 = high</span>
          </div>
          <v-card-text class="pa-4">
            <div v-if="checkins.length">
              <v-sparkline
                :value="stressValues"
                :smooth="8"
                :line-width="2"
                :padding="4"
                color="#1565C0"
                auto-draw
                height="64"
              />
              <div style="font-size: 11px; color: #90A4AE; margin-top: 4px">{{ stressDatesLabel }}</div>
            </div>
            <div v-else class="d-flex align-center justify-center py-6" style="color: #B0BEC5; font-size: 13px">
              <v-icon class="mr-2" color="grey lighten-2">mdi-chart-line</v-icon>
              No data yet — log a few check-ins
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="1" class="mc-section-card">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-emoticon-outline</v-icon>
            <span style="font-size: 13.5px; font-weight: 600; color: #1A2332">Mood Frequency</span>
          </div>
          <v-card-text class="pa-4">
            <div v-if="moodCountsList.length">
              <div style="font-size: 12px; color: #546E7A; margin-bottom: 10px">Top reported moods</div>
              <div class="d-flex flex-wrap" style="gap: 8px">
                <div
                  v-for="(m, i) in moodCountsList"
                  :key="i"
                  style="background: #E3F2FD; border-radius: 6px; padding: 5px 12px; display: inline-flex; align-items: center; gap: 6px"
                >
                  <span style="font-size: 13px; font-weight: 500; color: #1565C0">{{ m.label }}</span>
                  <span style="font-size: 11px; color: #64B5F6; font-weight: 600">×{{ m.count }}</span>
                </div>
              </div>
            </div>
            <div v-else class="d-flex align-center justify-center py-6" style="color: #B0BEC5; font-size: 13px">
              <v-icon class="mr-2" color="grey lighten-2">mdi-emoticon-outline</v-icon>
              No mood data yet
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent check-ins + upcoming bookings -->
    <v-row>
      <v-col cols="12" md="7">
        <v-card elevation="1" class="mc-section-card">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-clipboard-pulse-outline</v-icon>
            <span style="font-size: 13.5px; font-weight: 600; color: #1A2332">Recent Check-ins</span>
          </div>
          <div v-if="checkins.length">
            <div
              v-for="c in checkins"
              :key="c.id"
              class="d-flex align-center px-4 py-3"
              style="border-bottom: 1px solid #F4F7FC"
            >
              <div :style="{ width: '36px', height: '36px', borderRadius: '8px', background: stressBg(c.stress_level), display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginRight: '12px' }">
                <span :style="{ fontSize: '14px', fontWeight: '700', color: stressColor(c.stress_level) }">{{ c.stress_level }}</span>
              </div>
              <div style="flex: 1">
                <div style="font-size: 13.5px; font-weight: 500; color: #1A2332">{{ c.mood }}</div>
                <div style="font-size: 12px; color: #90A4AE">{{ fmtDateTime(c.created_at) }}</div>
              </div>
              <v-chip x-small label :color="stressBg(c.stress_level)" :style="{ color: stressColor(c.stress_level), fontWeight: 600, fontSize: '11px' }">
                {{ stressLabel(c.stress_level) }}
              </v-chip>
            </div>
          </div>
          <div v-else class="pa-6 text-center" style="color: #90A4AE; font-size: 13px">No check-ins yet.</div>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card elevation="1" class="mc-section-card">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-calendar-check</v-icon>
            <span style="font-size: 13.5px; font-weight: 600; color: #1A2332">Upcoming Bookings</span>
            <v-spacer />
            <v-btn text x-small color="primary" @click="$router.push('/consult')">Manage</v-btn>
          </div>
          <div v-if="upcoming.length">
            <div
              v-for="b in upcoming"
              :key="b.id"
              class="d-flex align-center px-4 py-3"
              style="border-bottom: 1px solid #F4F7FC"
            >
              <div style="flex: 1; min-width: 0">
                <div style="font-size: 13.5px; font-weight: 500; color: #1A2332; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ b.counselor.full_name }}</div>
                <div style="font-size: 12px; color: #90A4AE">{{ fmtDate(b.slot.start_time) }} • {{ fmtTime(b.slot.start_time) }}</div>
              </div>
              <v-chip x-small label :class="statusClass(b.status)">{{ b.status }}</v-chip>
            </div>
          </div>
          <div v-else class="pa-6 text-center" style="color: #90A4AE; font-size: 13px">No upcoming bookings.</div>
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
  data: () => ({ loading: false, checkins: [], sessions: [], bookings: [] }),
  computed: {
    stressValues ()     { return this.checkins.map(c => Number(c.stress_level || 0)).reverse() },
    stressDatesLabel () {
      if (!this.checkins.length) return ''
      const first = this.checkins[this.checkins.length - 1], last = this.checkins[0]
      return `${this.fmtShortDate(first.created_at)} – ${this.fmtShortDate(last.created_at)}`
    },
    avgStressDisplay () {
      if (!this.checkins.length) return '—'
      const sum = this.checkins.reduce((a, c) => a + Number(c.stress_level || 0), 0)
      return (sum / this.checkins.length).toFixed(1)
    },
    lastMood ()       { return this.checkins.length ? (this.checkins[0].mood || '') : '' },
    moodCounts ()     {
      const m = {}
      this.checkins.forEach(c => { const k = (c.mood || '').trim().toLowerCase(); if (k) m[k] = (m[k] || 0) + 1 })
      return m
    },
    moodCountsList () {
      return Object.entries(this.moodCounts).map(([label, count]) => ({ label, count })).sort((a, b) => b.count - a.count).slice(0, 6)
    },
    upcoming ()       {
      const now = new Date()
      return (this.bookings || []).filter(b => new Date(b.slot.start_time) > now).sort((a, b) => new Date(a.slot.start_time) - new Date(b.slot.start_time)).slice(0, 5)
    },
    upcomingCount ()  { return this.upcoming.length },
  },
  async created () { await this.refresh() },
  methods: {
    async refresh () {
      this.loading = true
      try {
        const [checkins] = await Promise.all([api.getRecentCheckIns(7).catch(() => [])])
        this.checkins  = Array.isArray(checkins) ? checkins : []
        this.sessions  = await this.safeGet('/chat/sessions')
        this.bookings  = await this.safeGet('/bookings/my')
      } finally { this.loading = false }
    },
    async safeGet (path) {
      try { const { data } = await api.api.get(path); return data || [] } catch { return [] }
    },
    statusClass (s) {
      switch ((s || '').toLowerCase()) {
        case 'confirmed': return 'mc-status-confirmed'
        case 'pending':   return 'mc-status-pending'
        case 'cancelled': return 'mc-status-cancelled'
        default:          return ''
      }
    },
    stressColor (n) { const v = Number(n || 0); return v <= 3 ? '#2E7D32' : v <= 6 ? '#E65100' : '#C62828' },
    stressBg (n)    { const v = Number(n || 0); return v <= 3 ? '#E8F5E9' : v <= 6 ? '#FFF8E1' : '#FFEBEE' },
    stressLabel (n) { const v = Number(n || 0); if (v <= 2) return 'Very low'; if (v <= 4) return 'Low'; if (v <= 6) return 'Moderate'; if (v <= 8) return 'High'; return 'Very high' },
    fmtDateTime (ts)  { try { return new Date(ts).toLocaleString() } catch { return ts } },
    fmtShortDate (ts) { try { return new Date(ts).toLocaleDateString() } catch { return ts } },
    fmtDate (ts)      { try { return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) } catch { return ts } },
    fmtTime (ts)      { try { return new Date(ts).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return ts } },
  },
}
</script>
