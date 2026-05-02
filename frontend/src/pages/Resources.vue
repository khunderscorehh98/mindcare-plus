<template>
  <default-layout>
    <template #header>
      <div class="mc-page-header d-flex align-center justify-space-between flex-wrap" style="gap: 12px">
        <div>
          <h2 style="font-size: 18px; font-weight: 600; color: #1A2332; margin: 0 0 2px">Resources</h2>
          <div class="subtitle" style="color: #546E7A; font-size: 13px">Curated mental health support for Brunei</div>
        </div>
        <v-text-field
          v-model="q"
          dense outlined clearable hide-details
          prepend-inner-icon="mdi-magnify"
          placeholder="Search resources…"
          background-color="white"
          style="max-width: 260px; border-radius: 8px"
        />
      </div>
    </template>

    <v-alert v-if="error" type="error" outlined dense class="mb-4" style="border-radius: 8px">{{ error }}</v-alert>

    <v-skeleton-loader v-if="loading" type="card, card, card" class="mb-4" />

    <v-row v-else>
      <v-col v-for="(r, i) in filtered" :key="i" cols="12" sm="6" md="4">
        <v-card
          elevation="1"
          class="mc-section-card mc-resource-card h-100 d-flex flex-column"
          style="transition: box-shadow .15s"
        >
          <v-card-text class="pa-4 flex-grow-1">
            <div class="d-flex align-start mb-2">
              <div style="width: 36px; height: 36px; border-radius: 8px; background: #E3F2FD; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 12px">
                <v-icon small color="primary">mdi-book-open-outline</v-icon>
              </div>
              <div>
                <div style="font-size: 14px; font-weight: 600; color: #1A2332; line-height: 1.3">{{ r.title }}</div>
              </div>
            </div>
            <p style="font-size: 13px; color: #546E7A; line-height: 1.6; margin: 0">{{ r.desc }}</p>
          </v-card-text>
          <div class="px-4 pb-4 pt-0">
            <v-btn
              :href="r.url"
              target="_blank"
              rel="noopener"
              outlined
              x-small
              color="primary"
              style="border-radius: 6px"
            >
              <v-icon left x-small>mdi-open-in-new</v-icon>Open link
            </v-btn>
          </div>
        </v-card>
      </v-col>

      <v-col v-if="!filtered.length && !loading" cols="12" class="text-center py-12">
        <v-icon x-large color="grey lighten-3" class="mb-3">mdi-book-search-outline</v-icon>
        <div style="color: #90A4AE; font-size: 14px">No resources matched your search.</div>
      </v-col>
    </v-row>
  </default-layout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/apiClient'

export default {
  name: 'Resources',
  components: { DefaultLayout },
  data: () => ({ items: [], loading: false, error: '', q: '' }),
  computed: {
    filtered () {
      const q = this.q.trim().toLowerCase()
      if (!q) return this.items
      return this.items.filter(r => [r.title, r.desc, r.url].filter(Boolean).some(s => String(s).toLowerCase().includes(q)))
    },
  },
  async created () {
    this.loading = true
    try { this.items = await api.resources() }
    catch { this.error = 'Could not load resources. Please try again.' }
    finally { this.loading = false }
  },
}
</script>

<style scoped>
.mc-resource-card:hover { box-shadow: 0 4px 16px rgba(21, 101, 192, 0.12) !important; }
</style>
