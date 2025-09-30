<template>
  <div :class="['d-flex', isUser ? 'justify-end' : 'justify-start', 'my-2']">
    <div class="d-flex align-end">
      <!-- Assistant avatar (left) -->
      <v-avatar v-if="!isUser && showAvatar" size="28" class="mr-2">
        <v-icon small>mdi-robot</v-icon>
      </v-avatar>

      <!-- Bubble -->
      <div :class="bubbleClasses">
        <div class="text-body-2" aria-live="polite">
          <template v-if="typing">
            <span class="dot" v-for="i in 3" :key="i">•</span>
          </template>
          <template v-else>
            <span v-for="(part, i) in parts" :key="i">
              <a
                v-if="part.type === 'link'"
                :href="part.href"
                target="_blank"
                rel="noopener"
              >{{ part.text }}</a>
              <span v-else>{{ part.text }}</span>
            </span>
          </template>
        </div>
        <div class="text-caption mt-1" :class="isUser ? 'text-right' : 'text-left'">
          {{ timeLabel }}
        </div>
      </div>

      <!-- User avatar (right) -->
      <v-avatar v-if="isUser && showAvatar" size="28" class="ml-2">
        <v-icon small>mdi-account</v-icon>
      </v-avatar>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChatMessage',
  props: {
    isUser: { type: Boolean, default: false },
    text: { type: String, default: '' },
    timestamp: { type: [String, Number, Date], default: () => new Date() },
    showAvatar: { type: Boolean, default: false },
    typing: { type: Boolean, default: false },
  },
  computed: {
    bubbleClasses() {
      return [
        'pa-3',
        'rounded-lg',
        'elevation-1',
        this.isUser ? 'primary white--text' : 'grey lighten-4',
        { 'ml-8': !this.isUser, 'mr-8': this.isUser, 'max-width-75': true }
      ];
    },
    timeLabel() {
      try {
        const d = new Date(this.timestamp);
        return d.toLocaleString();
      } catch (e) {
        return this.timestamp || '';
      }
    },
    parts() {
      // Split text into plain chunks + URLs (no v-html for safety)
      const urlRegex = /(https?:\/\/[^\s)]+|www\.[^\s)]+)/gi;
      const text = this.text || '';
      const out = [];
      let last = 0;
      let m;
      while ((m = urlRegex.exec(text)) !== null) {
        const start = m.index;
        if (start > last) out.push({ type: 'text', text: text.slice(last, start) });
        const url = m[0];
        const href = url.startsWith('http') ? url : `https://${url}`;
        out.push({ type: 'link', text: url, href });
        last = start + url.length;
      }
      if (last < text.length) out.push({ type: 'text', text: text.slice(last) });
      if (!out.length) out.push({ type: 'text', text });
      return out;
    },
  },
};
</script>

<style scoped>
.max-width-75 { max-width: 75%; word-break: break-word; }
.rounded-lg { border-radius: 14px; }

/* typing indicator */
.dot {
  animation: blink 1.2s infinite;
  padding: 0 2px;
  font-size: 20px;
  opacity: 0.5;
}
.dot:nth-child(2) { animation-delay: .15s; }
.dot:nth-child(3) { animation-delay: .3s; }
@keyframes blink {
  0%, 80%, 100% { opacity: .2 }
  40% { opacity: 1 }
}
</style>