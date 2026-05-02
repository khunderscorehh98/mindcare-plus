<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script>
export default {
  name: 'App',
}
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}

/* Global button reset */
.v-btn {
  letter-spacing: 0 !important;
  text-transform: none !important;
}

/* Global container */
.mc-container {
  max-width: 1140px;
  margin: 0 auto;
  padding: 28px 20px;
}

/* Page section header */
.mc-page-header {
  margin-bottom: 24px;
}
.mc-page-header h1,
.mc-page-header h2 {
  color: #1A2332;
  font-weight: 600;
  margin: 0 0 4px;
}
.mc-page-header .subtitle {
  color: #546E7A;
  font-size: 13.5px;
}

/* Metric card accent top border */
.mc-metric-card {
  border-top: 3px solid #1565C0 !important;
  border-radius: 8px !important;
}
.mc-metric-card.teal-accent { border-top-color: #00695C !important; }
.mc-metric-card.orange-accent { border-top-color: #E65100 !important; }
.mc-metric-card.green-accent { border-top-color: #2E7D32 !important; }

/* Section card */
.mc-section-card {
  border-radius: 8px !important;
}

/* Clinical table */
.mc-table thead th {
  background: #F4F7FC !important;
  color: #546E7A !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid #E1E8EF !important;
}

/* Status chips */
.mc-status-confirmed { background-color: #E8F5E9 !important; color: #2E7D32 !important; }
.mc-status-pending   { background-color: #FFF8E1 !important; color: #E65100 !important; }
.mc-status-cancelled { background-color: #FFEBEE !important; color: #C62828 !important; }
</style>
