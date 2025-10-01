<!-- src/pages/Checkins.vue -->
<template>
  <default-layout>
    <!-- Header goes into the layout slot -->
    <template #header>
      <v-row no-gutters align="center" justify="space-between">
        <v-col cols="12" md="6">
          <h2 class="text-h6 font-weight-medium mb-1">AI Check-ins</h2>
          <div class="text-body-2 grey--text">Track mood & stress over time</div>
        </v-col>
        <v-col cols="12" md="6" class="d-flex justify-end mt-3 mt-md-0">
          <v-dialog v-model="dlg" max-width="480">
            <template #activator="{ on }">
              <v-btn color="primary" dark v-on="on">
                <v-icon left>mdi-plus</v-icon> New Check-in
              </v-btn>
            </template>

            <v-card>
              <v-card-title class="text-h6">New check-in</v-card-title>
              <v-card-text>
                <v-text-field
                  v-model="form.mood"
                  label="Mood (e.g., calm, anxious)"
                  outlined dense
                />
                <v-slider
                  v-model="form.stress_level"
                  min="0" max="10" step="1"
                  ticks
                  label="Stress level"
                  class="mt-6"
                />
                <v-textarea
                  v-model="form.notes"
                  label="Notes (optional)"
                  outlined dense
                  rows="3"
                />
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn text @click="dlg = false">Cancel</v-btn>
                <v-btn color="primary" :loading="submitting" @click="submit">Save</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-col>
      </v-row>
    </template>

    <!-- Body -->
    <v-alert
      v-if="error"
      type="error"
      outlined
      dense
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <v-skeleton-loader
      v-if="loading"
      type="list-item-three-line, list-item-three-line, list-item-three-line"
      class="mb-4"
    />

    <v-row v-else>
      <v-col cols="12" md="6" lg="4" v-for="c in checkins" :key="c.id">
        <v-card outlined class="rounded-xl h-100 d-flex flex-column">
          <v-list-item>
            <v-list-item-avatar color="primary" class="white--text">
              <span class="subtitle-1">{{ c.stress_level }}</span>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title class="font-weight-medium">{{ c.mood }}</v-list-item-title>
              <v-list-item-subtitle>{{ niceDate(c.created_at) }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-divider />
          <v-card-text v-if="c.notes" class="text-body-2">
            {{ c.notes }}
          </v-card-text>
        </v-card>
      </v-col>

      <v-col v-if="!checkins.length" cols="12" class="text-center grey--text">
        No check-ins yet — create your first one!
      </v-col>
    </v-row>
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
    form: {
      mood: '',
      stress_level: 5,
      notes: ''
    }
  }),
  methods: {
    async load () {
      this.loading = true
      this.error = ''
      try {
        this.checkins = await api.getRecentCheckIns(12)
      } catch (e) {
        /* eslint-disable no-console */
        console.error(e)
        this.error = 'Could not load check-ins.'
      } finally {
        this.loading = false
      }
    },
    async submit () {
      if (!this.form.mood.trim()) {
        this.$toast && this.$toast.error
          ? this.$toast.error('Please enter a mood')
          : alert('Please enter a mood')
        return
      }
      this.submitting = true
      try {
        await api.createCheckIn({
          mood: this.form.mood.trim(),
          stress_level: this.form.stress_level,
          notes: this.form.notes || ''
        })
        this.dlg = false
        this.form = { mood: '', stress_level: 5, notes: '' }
        await this.load()
      } catch (e) {
        console.error(e)
        this.$toast && this.$toast.error
          ? this.$toast.error('Failed to save check-in')
          : alert('Failed to save check-in')
      } finally {
        this.submitting = false
      }
    },
    niceDate (iso) {
      try { return new Date(iso).toLocaleString() } catch { return iso }
    }
  },
  async created () {
    await this.load()
  }
}
</script>