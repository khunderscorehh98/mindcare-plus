<template>
  <v-container class="py-6" fluid>
    <v-row class="mb-4" align="center" justify="space-between" no-gutters>
      <v-col cols="12" md="6">
        <h2 class="text-h5 font-weight-medium">Helpful resources</h2>
        <div class="text-body-2 grey--text">Curated links for Brunei mental health support</div>
      </v-col>
      <v-col cols="12" md="4" class="d-flex justify-end">
        <v-text-field
          v-model="q"
          dense outlined clearable hide-details
          prepend-inner-icon="mdi-magnify"
          label="Search resources"
          class="ma-0"
        />
      </v-col>
    </v-row>

    <v-alert
      v-if="error"
      type="error" outlined dense class="mb-4"
    >{{ error }}</v-alert>

    <v-skeleton-loader
      v-if="loading"
      type="card, card, card"
    />

    <v-row v-else>
      <v-col
        v-for="(r, i) in filtered"
        :key="i"
        cols="12" sm="6" md="4"
      >
        <v-card outlined>
          <v-card-title class="text-subtitle-1">{{ r.title }}</v-card-title>
          <v-card-text class="text-body-2">{{ r.desc }}</v-card-text>
          <v-card-actions class="pt-0">
            <v-btn :href="r.url" target="_blank" rel="noopener" text small color="primary">
              Open link
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col v-if="!filtered.length && !loading" cols="12" class="text-center grey--text">
        No resources matched your search.
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import api from '@/services/apiClient'

export default {
  name: 'Resources',
  data: () => ({
    items: [],
    loading: false,
    error: '',
    q: ''
  }),
  computed: {
    filtered() {
      const q = this.q.trim().toLowerCase()
      if (!q) return this.items
      return this.items.filter(r =>
        [r.title, r.desc, r.url].filter(Boolean).some(s => s.toLowerCase().includes(q))
      )
    }
  },
  async created() {
    this.loading = true
    try {
      this.items = await api.resources()
    } catch (e) {
      console.error(e)
      this.error = 'Could not load resources. Please try again.'
    } finally {
      this.loading = false
    }
  }
}
</script>