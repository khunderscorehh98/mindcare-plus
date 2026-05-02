<template>
  <default-layout>
    <template v-slot:header>
      <div class="mc-page-header d-flex align-center justify-space-between flex-wrap" style="gap: 12px">
        <div>
          <h2 style="font-size: 18px; font-weight: 600; color: #1A2332; margin: 0 0 2px">Book a Consultation</h2>
          <div class="subtitle" style="color: #546E7A; font-size: 13px">Licensed professionals • Private • Culturally sensitive</div>
        </div>
        <v-chip small label :color="plan === 'premium' ? '#E8F5E9' : '#F5F5F5'" :style="{ color: plan === 'premium' ? '#2E7D32' : '#546E7A', fontWeight: 600, fontSize: '12px' }">
          {{ plan === 'premium' ? 'Premium plan' : 'Free plan' }}
        </v-chip>
      </div>
    </template>

    <v-row>
      <!-- Counselors list -->
      <v-col cols="12" md="4">
        <v-card elevation="1" class="mc-section-card">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-account-tie</v-icon>
            <span style="font-size: 13.5px; font-weight: 600; color: #1A2332">Counselors</span>
            <v-spacer />
            <v-btn icon x-small @click="loadCounselors"><v-icon small color="grey">mdi-refresh</v-icon></v-btn>
          </div>

          <div v-if="cLoading" class="pa-4">
            <v-skeleton-loader type="list-item-avatar-two-line" />
            <v-skeleton-loader type="list-item-avatar-two-line" />
          </div>

          <div v-else>
            <div
              v-for="c in counselors"
              :key="c.id"
              class="d-flex align-start px-4 py-3 mc-counselor-row"
              :style="{ background: c.id === selectedId ? '#EEF3FB' : 'transparent', borderBottom: '1px solid #F4F7FC', cursor: 'pointer', borderLeft: c.id === selectedId ? '3px solid #1565C0' : '3px solid transparent' }"
              @click="selectCounselor(c)"
            >
              <v-avatar color="primary" size="40" class="mr-3 elevation-1 flex-shrink-0">
                <span class="white--text font-weight-bold" style="font-size: 14px">{{ c.full_name.charAt(0) }}</span>
              </v-avatar>
              <div style="flex: 1; min-width: 0">
                <div style="font-size: 13.5px; font-weight: 600; color: #1A2332">{{ c.full_name }}</div>
                <div style="font-size: 12px; color: #546E7A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ c.bio }}</div>
                <v-chip x-small label color="#E3F2FD" style="color: #1565C0; font-weight: 600; font-size: 10px; margin-top: 4px">
                  {{ priceLabel(c) }}
                </v-chip>
              </div>
            </div>
            <div v-if="!counselors.length" class="pa-5 text-center" style="color: #90A4AE; font-size: 13px">
              No counselors available.
            </div>
          </div>
        </v-card>
      </v-col>

      <!-- Slots & booking -->
      <v-col cols="12" md="8">
        <v-card elevation="1" class="mc-section-card mb-4">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <div style="flex: 1; min-width: 0">
              <div style="font-size: 14px; font-weight: 600; color: #1A2332">
                {{ activeCounselor ? activeCounselor.full_name : 'Select a counselor' }}
              </div>
              <div style="font-size: 12px; color: #546E7A">
                {{ activeCounselor ? (activeCounselor.bio || '') : 'Choose from the list on the left' }}
              </div>
            </div>
            <v-select
              v-model="slotDays"
              :items="[7, 14, 21, 30]"
              label="Next"
              suffix="days"
              dense outlined hide-details
              class="ml-3"
              style="max-width: 110px"
              :disabled="!activeCounselor || sLoading"
              @change="loadSlots"
            />
          </div>

          <v-card-text class="pa-4">
            <div v-if="!activeCounselor" class="d-flex align-center justify-center py-8" style="color: #B0BEC5; font-size: 13.5px">
              <v-icon class="mr-2" color="grey lighten-2">mdi-calendar-blank</v-icon>
              Select a counselor to view available times
            </div>

            <div v-else>
              <div style="font-size: 12px; color: #546E7A; margin-bottom: 12px">
                <v-icon x-small class="mr-1">mdi-earth</v-icon>
                Times shown in your local timezone ({{ tzName }})
              </div>

              <v-progress-linear v-if="sLoading" indeterminate color="primary" rounded class="mb-3" />

              <v-row v-else dense>
                <v-col v-for="slot in slots" :key="slot.id" cols="6" sm="4" md="3">
                  <div
                    class="mc-slot-card"
                    style="border: 1px solid #E1E8EF; border-radius: 8px; padding: 12px 10px; cursor: pointer; background: white; text-align: center; transition: all .15s"
                    @click="confirmBook(slot)"
                  >
                    <div style="font-size: 12px; font-weight: 600; color: #546E7A">{{ fmtDate(slot.start_time) }}</div>
                    <div style="font-size: 13px; font-weight: 700; color: #1565C0; margin-top: 2px">{{ fmtTime(slot.start_time) }}</div>
                    <div style="font-size: 11px; color: #90A4AE">{{ fmtTime(slot.end_time) }}</div>
                  </div>
                </v-col>
                <v-col v-if="!slots.length" cols="12" class="text-center py-6">
                  <div style="color: #90A4AE; font-size: 13px">No available slots in the next {{ slotDays }} days.</div>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

        <!-- My bookings -->
        <v-card elevation="1" class="mc-section-card">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-calendar-check</v-icon>
            <span style="font-size: 13.5px; font-weight: 600; color: #1A2332">My Bookings</span>
            <v-spacer />
            <v-btn icon x-small @click="loadMyBookings"><v-icon small color="grey">mdi-refresh</v-icon></v-btn>
          </div>
          <div v-if="bLoading" class="pa-4"><v-skeleton-loader type="table-row, table-row" /></div>
          <v-simple-table v-else class="mc-table">
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Counselor</th>
                  <th class="text-left">Date</th>
                  <th class="text-left">Time</th>
                  <th class="text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td style="font-size: 13px; color: #1A2332; font-weight: 500">{{ b.counselor.full_name }}</td>
                  <td style="font-size: 13px; color: #546E7A">{{ fmtDate(b.slot.start_time) }}</td>
                  <td style="font-size: 13px; color: #546E7A">{{ fmtTime(b.slot.start_time) }}–{{ fmtTime(b.slot.end_time) }}</td>
                  <td>
                    <v-chip x-small label :class="statusClass(b.status)">{{ b.status }}</v-chip>
                  </td>
                </tr>
                <tr v-if="!bookings.length">
                  <td colspan="4" class="text-center py-4" style="color: #90A4AE; font-size: 13px">No bookings yet.</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Confirm booking dialog -->
    <v-dialog v-model="dlg.show" max-width="460">
      <v-card style="border-radius: 12px">
        <div class="px-5 py-4" style="border-bottom: 1px solid #E1E8EF; background: #F8FAFC">
          <div style="font-size: 16px; font-weight: 600; color: #1A2332">Confirm Booking</div>
        </div>
        <v-card-text class="pa-5">
          <div class="d-flex align-start mb-4">
            <v-avatar color="primary" size="44" class="mr-3 elevation-1">
              <span class="white--text font-weight-bold">{{ activeCounselor && activeCounselor.full_name.charAt(0) }}</span>
            </v-avatar>
            <div>
              <div style="font-size: 15px; font-weight: 600; color: #1A2332">{{ activeCounselor && activeCounselor.full_name }}</div>
              <div style="font-size: 13px; color: #546E7A; margin-top: 4px">
                <v-icon x-small class="mr-1">mdi-calendar</v-icon>{{ fmtDate(dlg.slot && dlg.slot.start_time) }}
                &nbsp;•&nbsp;
                <v-icon x-small class="mr-1">mdi-clock-outline</v-icon>{{ fmtTime(dlg.slot && dlg.slot.start_time) }} – {{ fmtTime(dlg.slot && dlg.slot.end_time) }}
              </div>
            </div>
          </div>

          <v-alert v-if="plan !== 'premium'" dense type="info" outlined class="mb-3" style="border-radius: 8px">
            Booking requires a <strong>Premium</strong> account. Enter an access code below to upgrade.
          </v-alert>
          <v-alert v-if="err" type="error" dense class="mb-3">{{ err }}</v-alert>

          <div v-if="plan !== 'premium'" class="mt-2">
            <div style="font-size: 13px; font-weight: 500; color: #1A2332; margin-bottom: 8px">Access / promo code</div>
            <v-text-field
              v-model="upgradeCode"
              outlined dense
              placeholder="Enter code"
              background-color="white"
              hide-details
              class="mb-2"
            />
            <v-btn small depressed color="primary" :loading="upgrading" :disabled="upgrading || !upgradeCode" @click="upgrade">
              <v-icon left small>mdi-star-outline</v-icon>Upgrade to Premium
            </v-btn>
          </div>
        </v-card-text>
        <div class="d-flex justify-end px-5 pb-4" style="gap: 8px; border-top: 1px solid #E1E8EF; padding-top: 16px !important">
          <v-btn outlined @click="closeDlg">Cancel</v-btn>
          <v-btn depressed color="primary" :disabled="booking" :loading="booking" @click="doBook">
            Confirm Booking
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snack.show" :timeout="2500" bottom right style="border-radius: 8px">
      {{ snack.text }}
      <template #action>
        <v-btn text x-small @click="snack.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </default-layout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/apiClient'
import { mapGetters } from 'vuex'

export default {
  name: 'Consult',
  components: { DefaultLayout },
  data: () => ({
    counselors: [], cLoading: false,
    selectedId: null, slots: [], sLoading: false, slotDays: 14,
    bookings: [], bLoading: false,
    dlg: { show: false, slot: null }, booking: false, err: '',
    upgradeCode: '', upgrading: false,
    snack: { show: false, text: '' },
  }),
  computed: {
    ...mapGetters(['plan']),
    activeCounselor () { return this.counselors.find(c => c.id === this.selectedId) || null },
    tzName ()          { try { return Intl.DateTimeFormat().resolvedOptions().timeZone } catch { return 'local time' } },
  },
  async created () { await this.loadCounselors(); await this.loadMyBookings() },
  methods: {
    async loadCounselors () {
      this.cLoading = true
      try {
        const rows = await api.getCounselors()
        this.counselors = Array.isArray(rows) ? rows : []
        if (!this.selectedId && this.counselors.length) this.selectCounselor(this.counselors[0])
      } catch { this.counselors = [] } finally { this.cLoading = false }
    },
    async loadSlots () {
      if (!this.selectedId) return
      this.sLoading = true
      try {
        const rows = await api.getSlots(this.selectedId, this.slotDays)
        this.slots = Array.isArray(rows) ? rows : []
      } catch { this.slots = [] } finally { this.sLoading = false }
    },
    async loadMyBookings () {
      this.bLoading = true
      try {
        const { data } = await api.api.get('/bookings/my')
        this.bookings = Array.isArray(data) ? data : []
      } catch { this.bookings = [] } finally { this.bLoading = false }
    },
    selectCounselor (c) { this.selectedId = c.id; this.loadSlots() },
    confirmBook (slot)  { this.err = ''; this.dlg = { show: true, slot } },
    closeDlg ()         { this.dlg = { show: false, slot: null }; this.err = '' },
    async doBook () {
      if (!this.dlg.slot || !this.activeCounselor) return
      this.err = ''; this.booking = true
      try {
        await api.bookSession({ counselor_id: this.activeCounselor.id, slot_id: this.dlg.slot.id })
        this.snack = { show: true, text: 'Booking confirmed!' }
        this.closeDlg(); this.loadSlots(); this.loadMyBookings()
      } catch (e) {
        const status = e && e.response && e.response.status
        const detail = e && e.response && e.response.data && e.response.data.detail
        this.err = status === 402 ? 'Premium required. Enter an access code below to upgrade.' : (detail || 'Booking failed. Please try another slot.')
      } finally { this.booking = false }
    },
    async upgrade () {
      if (!this.upgradeCode) return
      this.upgrading = true
      try {
        await api.api.post('/billing/upgrade', { code: this.upgradeCode })
        this.$store.dispatch('refreshMe').catch(() => {})
        this.snack = { show: true, text: 'Upgraded to Premium!' }
        this.upgradeCode = ''
      } catch (e) {
        const detail = e && e.response && e.response.data && e.response.data.detail
        this.snack = { show: true, text: detail || 'Upgrade failed' }
      } finally { this.upgrading = false }
    },
    statusClass (s) {
      switch ((s || '').toLowerCase()) {
        case 'confirmed': return 'mc-status-confirmed'
        case 'pending':   return 'mc-status-pending'
        case 'cancelled': return 'mc-status-cancelled'
        default: return ''
      }
    },
    priceLabel (c)   { const cents = Number(c.price_cents || 0); return `${c.currency || 'BND'} ${(cents / 100).toFixed(2)}` },
    fmtDate (ts)     { try { return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) } catch { return ts } },
    fmtTime (ts)     { try { return new Date(ts).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return ts } },
  },
}
</script>

<style scoped>
.mc-slot-card:hover { border-color: #1565C0 !important; background: #EEF3FB !important; }
</style>
