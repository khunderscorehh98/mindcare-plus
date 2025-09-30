<template>
  <default-layout>
    <template v-slot:header>
      <v-row align="center">
        <v-col cols="12" md="8">
          <h2 class="subtitle-1 mb-0">Book a Consultation</h2>
          <div class="text-caption grey--text">
            Licensed professionals • Private • Culturally sensitive
          </div>
        </v-col>
        <v-col cols="12" md="4" class="text-md-right mt-2 mt-md-0">
          <v-chip small :color="planColor" :text-color="planText" label class="text-uppercase">
            {{ plan }} plan
          </v-chip>
        </v-col>
      </v-row>
    </template>

    <v-row>
      <!-- Counselors list -->
      <v-col cols="12" md="5" lg="4">
        <v-card outlined class="rounded-xl">
          <v-card-title>
            <v-icon left color="primary">mdi-account-heart</v-icon>
            Counselors
            <v-spacer />
            <v-btn icon small @click="loadCounselors"><v-icon>mdi-refresh</v-icon></v-btn>
          </v-card-title>
          <v-divider/>

          <v-card-text v-if="cLoading">
            <v-skeleton-loader type="list-item-two-line" />
            <v-skeleton-loader type="list-item-two-line" />
          </v-card-text>

          <v-list v-else dense two-line>
            <template v-if="counselors.length">
              <v-list-item
                v-for="c in counselors"
                :key="c.id"
                :class="{ 'grey lighten-4': c.id === selectedId }"
                @click="selectCounselor(c)"
              >
                <v-list-item-avatar color="primary" class="white--text">
                  <v-icon dark>mdi-account</v-icon>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title class="font-weight-medium">{{ c.full_name }}</v-list-item-title>
                  <v-list-item-subtitle class="grey--text">
                    {{ c.bio }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip x-small label class="text-uppercase">
                    {{ priceLabel(c) }}
                  </v-chip>
                </v-list-item-action>
              </v-list-item>
            </template>

            <v-list-item v-else>
              <v-list-item-content>
                <v-list-item-title>No counselors available</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- Slots & booking -->
      <v-col cols="12" md="7" lg="8">
        <v-card elevation="2" class="rounded-xl">
          <v-card-title class="pb-0">
            <div>
              <div class="text-h6 font-weight-semibold">
                {{ activeCounselor ? activeCounselor.full_name : 'Select a counselor' }}
              </div>
              <div class="text-caption grey--text">
                {{ activeCounselor ? (activeCounselor.bio || '—') : 'Browse counselors and pick a slot' }}
              </div>
            </div>
            <v-spacer />
            <v-select
              v-model="slotDays"
              :items="[7, 14, 21, 30]"
              label="Show next"
              dense outlined hide-details class="mr-2" style="max-width: 130px"
              :disabled="!activeCounselor || sLoading"
              @change="loadSlots"
            />
          </v-card-title>

          <v-divider class="my-2"></v-divider>

          <v-card-text>
            <v-alert v-if="!activeCounselor" dense outlined type="info" border="left" class="rounded-xl mb-3">
              Choose a counselor from the left to see available times.
            </v-alert>

            <div v-if="activeCounselor">
              <div class="text-caption grey--text mb-2">
                Times shown in your local timezone ({{ tzName }})
              </div>

              <v-progress-linear
                v-if="sLoading"
                indeterminate
                color="primary"
                class="mb-2"
              />

              <v-row v-else>
                <template v-if="slots.length">
                  <v-col v-for="slot in slots" :key="slot.id" cols="12" sm="6" md="4" lg="3">
                    <v-card outlined class="rounded-lg slot-card" @click="confirmBook(slot)">
                      <v-card-text>
                        <div class="text-subtitle-2">{{ fmtDate(slot.start_time) }}</div>
                        <div class="text-body-2">
                          {{ fmtTime(slot.start_time) }}–{{ fmtTime(slot.end_time) }}
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </template>
                <v-col cols="12" v-else>
                  <v-alert dense outlined type="warning" border="left" class="rounded-xl">
                    No available slots in the next {{ slotDays }} days.
                  </v-alert>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

        <!-- My bookings -->
        <v-card outlined class="rounded-xl mt-4">
          <v-card-title>
            <v-icon left color="primary">mdi-calendar-check</v-icon>
            My Bookings
            <v-spacer />
            <v-btn icon small @click="loadMyBookings"><v-icon>mdi-refresh</v-icon></v-btn>
          </v-card-title>
          <v-divider/>
          <v-card-text v-if="bLoading">
            <v-skeleton-loader type="table" />
          </v-card-text>
          <v-simple-table v-else>
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
                  <td>{{ b.counselor.full_name }}</td>
                  <td>{{ fmtDate(b.slot.start_time) }}</td>
                  <td>{{ fmtTime(b.slot.start_time) }}–{{ fmtTime(b.slot.end_time) }}</td>
                  <td>
                    <v-chip x-small :color="statusColor(b.status)" text-color="white" label>
                      {{ b.status }}
                    </v-chip>
                  </td>
                </tr>
                <tr v-if="!bookings.length">
                  <td colspan="4" class="grey--text">No bookings yet.</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Confirm booking dialog -->
    <v-dialog v-model="dlg.show" max-width="480">
      <v-card>
        <v-card-title class="headline">Confirm booking</v-card-title>
        <v-card-text>
          <div class="mb-2"><strong>{{ activeCounselor && activeCounselor.full_name }}</strong></div>
          <div class="text-body-2">
            <v-icon small class="mr-1">mdi-calendar</v-icon>
            {{ fmtDate(dlg.slot && dlg.slot.start_time) }}
            <br />
            <v-icon small class="mr-1">mdi-clock-outline</v-icon>
            {{ fmtTime(dlg.slot && dlg.slot.start_time) }}–{{ fmtTime(dlg.slot && dlg.slot.end_time) }}
          </div>
          <v-alert
            v-if="plan !== 'premium'"
            dense type="info" class="mt-3" border="left" outlined
          >
            Booking requires <strong>premium</strong>. You can upgrade below.
          </v-alert>
          <v-alert
            v-if="err"
            type="error"
            dense
            class="mt-3"
          >{{ err }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="closeDlg">Cancel</v-btn>
          <v-btn
            color="primary"
            :disabled="booking"
            :loading="booking"
            @click="doBook"
          >
            Book
          </v-btn>
        </v-card-actions>
        <v-divider/>
        <v-card-text v-if="plan !== 'premium'">
          <div class="text-subtitle-2 mb-2">Upgrade to premium</div>
          <v-text-field
            v-model="upgradeCode"
            dense outlined
            label="Promo / access code"
            :disabled="upgrading"
            hide-details
          />
          <v-btn
            small color="deep-purple accent-4" class="white--text mt-2"
            :loading="upgrading" :disabled="upgrading || !upgradeCode"
            @click="upgrade"
          >
            <v-icon left small>mdi-lightning-bolt</v-icon>
            Upgrade now
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snack.show" :timeout="2500">
      {{ snack.text }}
      <v-btn text @click="snack.show = false">Close</v-btn>
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
    counselors: [],
    cLoading: false,

    selectedId: null,
    slots: [],
    sLoading: false,
    slotDays: 14,

    bookings: [],
    bLoading: false,

    dlg: { show: false, slot: null },
    booking: false,
    err: '',
    upgradeCode: '',
    upgrading: false,

    snack: { show: false, text: '' },
  }),
  computed: {
    ...mapGetters(['plan']),
    activeCounselor () {
      return this.counselors.find(c => c.id === this.selectedId) || null
    },
    planColor () { return this.plan === 'premium' ? 'deep-purple accent-4' : 'grey lighten-3' },
    planText () { return this.plan === 'premium' ? 'white' : 'black' },
    tzName () { try { return Intl.DateTimeFormat().resolvedOptions().timeZone } catch { return 'local time' } },
  },
  async created () {
    await this.loadCounselors()
    await this.loadMyBookings()
  },
  methods: {
    // fetch
    async loadCounselors () {
      this.cLoading = true
      try {
        const rows = await api.getCounselors()
        this.counselors = Array.isArray(rows) ? rows : []
        if (!this.selectedId && this.counselors.length) {
          this.selectCounselor(this.counselors[0])
        }
      } catch (e) {
        this.counselors = []
      } finally {
        this.cLoading = false
      }
    },
    async loadSlots () {
      if (!this.selectedId) return
      this.sLoading = true
      try {
        const rows = await api.getSlots(this.selectedId, this.slotDays)
        this.slots = Array.isArray(rows) ? rows : []
      } catch (e) {
        this.slots = []
      } finally {
        this.sLoading = false
      }
    },
    async loadMyBookings () {
      this.bLoading = true
      try {
        const { data } = await api.api.get('/bookings/my')
        this.bookings = Array.isArray(data) ? data : []
      } catch (e) {
        this.bookings = []
      } finally {
        this.bLoading = false
      }
    },

    // selection
    selectCounselor (c) {
      this.selectedId = c.id
      this.loadSlots()
    },

    // booking
    confirmBook (slot) {
      this.err = ''
      this.dlg = { show: true, slot }
    },
    closeDlg () {
      this.dlg = { show: false, slot: null }
      this.err = ''
    },
    async doBook () {
      if (!this.dlg.slot || !this.activeCounselor) return
      this.err = ''
      this.booking = true
      try {
        const payload = { counselor_id: this.activeCounselor.id, slot_id: this.dlg.slot.id }
        const res = await api.bookSession(payload)
        // success
        this.snack = { show: true, text: 'Booking confirmed 🎉' }
        this.closeDlg()
        this.loadSlots()
        this.loadMyBookings()
      } catch (e) {
        const status = e && e.response && e.response.status
        const detail = e && e.response && e.response.data && e.response.data.detail
        if (status === 402) {
          // upsell: keep dialog open, show message
          this.err = 'Premium required to book. Enter an access code below to upgrade.'
        } else {
          this.err = detail || 'Booking failed. Please try another slot.'
        }
      } finally {
        this.booking = false
      }
    },

    // upgrade
    async upgrade () {
      if (!this.upgradeCode) return
      this.upgrading = true
      try {
        await api.api.post('/billing/upgrade', { code: this.upgradeCode })
        // refresh user profile in store if you track plan there
        this.$store.dispatch('refreshMe').catch(() => {})
        this.snack = { show: true, text: 'Upgraded to premium ✅' }
        this.upgradeCode = ''
      } catch (e) {
        const detail = e && e.response && e.response.data && e.response.data.detail
        this.snack = { show: true, text: detail || 'Upgrade failed' }
      } finally {
        this.upgrading = false
      }
    },

    // utils
    priceLabel (c) {
      const cents = Number(c.price_cents || 0)
      const amount = (cents / 100).toFixed(2)
      const cur = c.currency || 'BND'
      return `${cur} ${amount}`
    },
    fmtDate (ts) {
      try { return new Date(ts).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) } catch { return ts }
    },
    fmtTime (ts) {
      try { return new Date(ts).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return ts }
    },
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
.slot-card { cursor: pointer; transition: box-shadow .2s; }
.slot-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.08); }
</style>