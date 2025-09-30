<template>
  <v-card
    :outlined="outlined"
    :elevation="hover ? 3 : 1"
    class="resource-card rounded-lg"
    :class="{ 'resource-hover': hover }"
    @click="open"
  >
    <template v-if="loading">
      <v-skeleton-loader type="list-item-two-line, actions" />
    </template>

    <template v-else>
      <v-card-title class="py-3">
        <div class="d-flex align-center">
          <v-avatar v-if="showFavicon" size="22" class="mr-2">
            <img :src="faviconUrl" :alt="domain + ' favicon'" />
          </v-avatar>
          <div class="title-wrap">
            <div class="text-subtitle-1 font-weight-medium line-clamp-1">
              {{ title }}
            </div>
            <div class="text-caption grey--text line-clamp-1 d-flex align-center">
              <v-icon x-small class="mr-1">mdi-link-variant</v-icon>
              <span>{{ domain }}</span>
            </div>
          </div>
        </div>
        <v-spacer />
        <v-btn icon :aria-label="`Open ${domain}`" @click.stop="open">
          <v-icon>mdi-open-in-new</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pt-0">
        <div v-if="desc" class="text-body-2 line-clamp-3">
          {{ desc }}
        </div>

        <div v-if="tags && tags.length" class="mt-3 d-flex flex-wrap">
          <v-chip
            v-for="(t, i) in tags"
            :key="i"
            small
            class="mr-1 mb-1"
            color="primary"
            text-color="white"
            label
            outlined
          >
            {{ t }}
          </v-chip>
        </div>
      </v-card-text>

      <v-divider v-if="$slots.actions" class="my-0" />
      <v-card-actions v-if="$slots.actions" class="py-2">
        <slot name="actions" />
      </v-card-actions>
    </template>
  </v-card>
</template>

<script>
export default {
  name: 'ResourceCard',
  props: {
    title: { type: String, required: true },
    desc: { type: String, default: '' },
    url: { type: String, required: true },
    tags: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    hover: { type: Boolean, default: true },
    outlined: { type: Boolean, default: true },
    showFavicon: { type: Boolean, default: true },
  },
  computed: {
    domain() {
      try {
        const u = new URL(this.href);
        return u.hostname.replace(/^www\./i, '');
      } catch (e) {
        // fallback for relative/invalid URLs
        return (this.url || '').replace(/^https?:\/\//, '').split('/')[0];
      }
    },
    href() {
      // ensure we have an absolute URL
      if (!this.url) return '#';
      if (/^https?:\/\//i.test(this.url)) return this.url;
      return `https://${this.url}`;
    },
    faviconUrl() {
      // lightweight favicon service
      return `https://www.google.com/s2/favicons?domain=${encodeURIComponent(this.domain)}&sz=64`;
    },
  },
  methods: {
    open() {
      if (!this.href || this.href === '#') return;
      window.open(this.href, '_blank', 'noopener,noreferrer');
      this.$emit('open', this.href);
    },
  },
};
</script>

<style scoped>
.resource-card {
  cursor: pointer;
  transition: box-shadow 0.18s ease, transform 0.12s ease;
}
.resource-hover:hover {
  transform: translateY(-1px);
}
.title-wrap {
  min-width: 0;
}
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>