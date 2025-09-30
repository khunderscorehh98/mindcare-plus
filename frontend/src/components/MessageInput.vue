<template>
  <div class="message-input">
    <v-form ref="form" @submit.prevent="trySend">
      <div class="d-flex align-end">
        <v-textarea
          class="flex-grow-1 mr-2"
          v-model="draft"
          :auto-grow="true"
          :rows="1"
          :disabled="disabled || loading"
          :counter="maxLength"
          :maxlength="maxLength"
          :placeholder="placeholder"
          :clearable="!loading"
          hide-details="auto"
          @keydown.native="onKeyDown"
        />

        <v-btn
          color="primary"
          :loading="loading"
          :disabled="disabled || loading || !canSend"
          @click="trySend"
          aria-label="Send message"
          class="send-btn"
        >
          <v-icon left>mdi-send</v-icon>
          <span class="d-none d-sm-inline">Send</span>
        </v-btn>
      </div>
    </v-form>

    <div class="text-caption grey--text mt-1">
      Press <kbd>Enter</kbd> to send • <kbd>Shift</kbd>+<kbd>Enter</kbd> for a new line
    </div>
  </div>
</template>

<script>
export default {
  name: 'MessageInput',
  props: {
    loading: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
    placeholder: { type: String, default: 'Type your message…' },
    maxLength: { type: Number, default: 1000 }
  },
  data() {
    return {
      draft: ''
    };
  },
  computed: {
    canSend() {
      return (this.draft || '').trim().length > 0;
    }
  },
  methods: {
    onKeyDown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.trySend();
      }
    },
    trySend() {
      if (this.loading || this.disabled) return;
      const text = (this.draft || '').trim();
      if (!text) return;
      this.$emit('send', text);
      this.draft = '';
    }
  }
};
</script>

<style scoped>
.message-input :deep(textarea) {
  /* nicer feel on desktop */
  line-height: 1.4;
}
.send-btn {
  min-width: 44px;
}
kbd {
  background: #eee;
  border-radius: 4px;
  padding: 0 6px;
  border: 1px solid rgba(0,0,0,0.12);
  font-size: 0.75rem;
}
</style>