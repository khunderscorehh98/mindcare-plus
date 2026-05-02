<template>
  <default-layout>
    <template #header>
      <div class="mc-page-header d-flex align-center justify-space-between flex-wrap" style="gap: 12px">
        <div>
          <h2 style="font-size: 18px; font-weight: 600; color: #1A2332; margin: 0 0 2px">Daily Check-ins</h2>
          <div class="subtitle" style="color: #546E7A; font-size: 13px">Track your mood and stress levels over time</div>
        </div>
        <v-dialog v-model="dlg" max-width="480">
          <template #activator="{ on }">
            <v-btn color="primary" depressed small v-on="on">
              <v-icon left small>mdi-plus</v-icon>New Check-in
            </v-btn>
          </template>
          <v-card style="border-radius: 12px">
            <div class="px-5 py-4" style="border-bottom: 1px solid #E1E8EF; background: #F8FAFC">
              <div class="d-flex align-center">
                <div style="width: 34px; height: 34px; border-radius: 8px; background: #E0F2F1; display: flex; align-items: center; justify-content: center; margin-right: 12px">
                  <v-icon small color="teal darken-1">mdi-clipboard-pulse-outline</v-icon>
                </div>
                <div>
                  <div style="font-size: 15px; font-weight: 600; color: #1A2332">New Check-in</div>
                  <div style="font-size: 12px; color: #546E7A">{{ todayLabel }}</div>
                </div>
              </div>
            </div>
            <div class="pa-5">
              <div class="mb-1" style="font-size: 13px; font-weight: 500; color: #1A2332">Current mood</div>
              <v-text-field
                v-model="form.mood"
                placeholder="e.g. calm, anxious, hopeful…"
                outlined dense
                background-color="white"
                class="mb-3"
              />

              <div class="mb-2 d-flex align-center justify-space-between">
                <span style="font-size: 13px; font-weight: 500; color: #1A2332">Stress level</span>
                <v-chip small label :color="stressChipColor(form.stress_level)" style="font-size: 12px; font-weight: 700; min-width: 64px; justify-content: center">
                  {{ form.stress_level }}/10 — {{ stressLabel(form.stress_level) }}
                </v-chip>
              </div>
              <v-slider
                v-model="form.stress_level"
                min="0" max="10" step="1"
                :color="stressColor(form.stress_level)"
                track-color="grey lighten-3"
                thumb-label
                class="mt-0 mb-3"
              />

              <div class="mb-1" style="font-size: 13px; font-weight: 500; color: #1A2332">Notes <span style="color: #90A4AE; font-weight: 400">(optional)</span></div>
              <v-textarea
                v-model="form.notes"
                placeholder="What's on your mind?"
                outlined dense rows="3"
                background-color="white"
              />
            </div>
            <div class="d-flex justify-end px-5 pb-4" style="gap: 8px; border-top: 1px solid #E1E8EF; padding-top: 16px !important">
              <v-btn outlined @click="dlg = false">Cancel</v-btn>
              <v-btn depressed color="primary" :loading="submitting" @click="submit">Save check-in</v-btn>
            </div>
          </v-card>
        </v-dialog>
      </div>
    </template>

    <v-alert v-if="error" type="error" outlined dense class="mb-4" style="border-radius: 8px">{{ error }}</v-alert>

    <v-skeleton-loader v-if="loading" type="card, card, card" class="mb-4" />

    <div v-else>
      <div v-if="!checkins.length" class="text-center py-12">
        <v-icon x-large color="grey lighten-3" class="mb-3">mdi-clipboard-pulse-outline</v-icon>
        <div style="color: #90A4AE; font-size: 14px">No check-ins yet. Create your first one above.</div>
      </div>

      <v-row v-else>
        <v-col v-for="c in checkins" :key="c.id" cols="12" sm="6" md="4">
          <v-card elevation="1" class="mc-section-card" style="border-top: 3px solid transparent" :style="{ borderTopColor: stressColor(c.stress_level) }">
            <v-card-text class="pa-4">
              <div class="d-flex align-center justify-space-between mb-3">
                <div class="d-flex align-center">
                  <div :style="{ width: '40px', height: '40px', borderRadius: '8px', background: stressBg(c.stress_level), display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '10px', flexShrink: 0 }">
                    <span :style="{ fontSize: '16px', fontWeight: '700', color: stressColor(c.stress_level) }">{{ c.stress_level }}</span>
                  </div>
                  <div>
                    <div style="font-size: 14px; font-weight: 600; color: #1A2332">{{ c.mood }}</div>
                    <div style="font-size: 11px; color: #90A4AE">{{ niceDate(c.created_at) }}</div>
                  </div>
                </div>
                <v-chip x-small label :color="stressBg(c.stress_level)" :style="{ color: stressColor(c.stress_level), fontWeight: 600, fontSize: '11px' }">
                  {{ stressLabel(c.stress_level) }}
                </v-chip>
              </div>
              <div v-if="c.notes" style="font-size: 13px; color: #546E7A; background: #F8FAFC; border-radius: 6px; padding: 10px; border-left: 3px solid #E1E8EF">
                {{ c.notes }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </default-layout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/apiClient'

export default {
  name: 'CheckIns',
  components: { DefaultLayout },
  data: () => ({
    loading: false,
    submitting: false,
    error: '',
    checkins: [],
    dlg: false,
    form: { mood: '', stress_level: 5, notes: '' },
  }),
  computed: {
    todayLabel () { return new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) },
  },
  async created () { await this.load() },
  methods: {
    async load () {
      this.loading = true; this.error = ''
      try { this.checkins = await api.getRecentCheckIns(12) }
      catch { this.error = 'Could not load check-ins.' }
      finally { this.loading = false }
    },
    async submit () {
      if (!this.form.mood.trim()) { alert('Please enter a mood'); return }
      this.submitting = true
      try {
        await api.createCheckIn({ mood: this.form.mood.trim(), stress_level: this.form.stress_level, notes: this.form.notes || '' })
        this.dlg = false
        this.form = { mood: '', stress_level: 5, notes: '' }
        await this.load()
      } catch { alert('Failed to save check-in') }
      finally { this.submitting = false }
    },
    stressColor (n) {
      const v = Number(n || 0)
      if (v <= 3) return '#2E7D32'
      if (v <= 6) return '#E65100'
      return '#C62828'
    },
    stressBg (n) {
      const v = Number(n || 0)
      if (v <= 3) return '#E8F5E9'
      if (v <= 6) return '#FFF8E1'
      return '#FFEBEE'
    },
    stressLabel (n) {
      const v = Number(n || 0)
      if (v <= 2) return 'Very low'
      if (v <= 4) return 'Low'
      if (v <= 6) return 'Moderate'
      if (v <= 8) return 'High'
      return 'Very high'
    },
    stressChipColor (n) { return this.stressBg(n) },
    niceDate (iso) { try { return new Date(iso).toLocaleString() } catch { return iso } },
  },
}
</script>
