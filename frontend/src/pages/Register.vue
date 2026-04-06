<template>
  <v-container fluid class="fill-height register-wrap">
    <v-row no-gutters class="fill-height">
      <!-- Left brand panel -->
      <v-col
        cols="12" md="6"
        class="left-panel d-none d-md-flex align-center justify-center"
      >
        <div class="px-10">
          <div class="brand-row mb-6">
            <v-avatar size="44" color="primary" class="elev">
              <v-icon dark>mdi-heart</v-icon>
            </v-avatar>
            <div class="ml-3">
              <div class="text-h5 font-weight-bold">MindCare+</div>
              <div class="subtitle-2 grey--text text--lighten-1">Wellness, your way</div>
            </div>
          </div>

          <div class="text-h4 font-weight-bold mb-3">
            Join a kinder, more supportive space.
          </div>
          <div class="subtitle-1 grey--text text--lighten-1 mb-8">
            Private, stigma-free mental health support designed for Brunei.
            It’s quick, anonymous, and always here for you.
          </div>

          <v-row dense>
            <v-col cols="12" sm="6" class="mb-2">
              <v-chip label class="chip-soft" color="primary" text-color="white">
                <v-icon left small>mdi-shield-check</v-icon>
                Anonymous & Secure
              </v-chip>
            </v-col>
            <v-col cols="12" sm="6" class="mb-2">
              <v-chip label class="chip-soft" color="primary" text-color="white">
                <v-icon left small>mdi-robot-love</v-icon>
                AI support 24/7
              </v-chip>
            </v-col>
          </v-row>
        </div>
      </v-col>

      <!-- Right form panel -->
      <v-col cols="12" md="6" class="d-flex align-center justify-center">
        <v-card class="form-card rounded-xl elevation-8 mx-4 my-10" max-width="520">
          <v-card-text class="pa-8">
            <div class="text-h5 font-weight-bold mb-1">Create your account</div>
            <div class="caption grey--text mb-6">
              Already have one?
              <router-link :to="{ name: 'login', query: $route.query }">Log in</router-link>
            </div>

            <v-alert v-if="error" type="error" dense border="left" class="mb-4">
              {{ error }}
            </v-alert>

            <v-form ref="form" v-model="valid" @submit.prevent="onSubmit">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
                :rules="[rules.required, rules.email]"
                :disabled="loading"
                outlined dense clearable
                autocomplete="email"
              />

              <v-text-field
                v-model="password"
                :type="showPass ? 'text' : 'password'"
                label="Password"
                prepend-inner-icon="mdi-lock"
                :append-icon="showPass ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showPass = !showPass"
                :rules="[rules.required, rules.min(6)]"
                :disabled="loading"
                outlined dense
                autocomplete="new-password"
              />

              <!-- Strength meter -->
              <div class="d-flex align-center mb-4">
                <v-progress-linear
                  :value="strength.value"
                  :color="strength.color"
                  height="8"
                  rounded
                  class="flex-grow-1 mr-3"
                />
                <span class="caption grey--text text--darken-1">{{ strength.label }}</span>
              </div>

              <!-- T&C -->
              <v-checkbox
                v-model="agree"
                :rules="[v => !!v || 'Please agree to continue']"
                class="mt-n2 mb-4"
                :disabled="loading"
                dense
                hide-details="auto"
                label="I agree to the Terms of Use and Privacy Policy"
              >
                <template #label>
                  <span class="caption">
                    I agree to the
                    <a href="#" @click.prevent>Terms of Use</a> and
                    <a href="#" @click.prevent>Privacy Policy</a>
                  </span>
                </template>
              </v-checkbox>

              <v-btn
                type="submit"
                :loading="loading"
                :disabled="!valid || !agree || loading"
                color="primary"
                large block class="text-none mb-2"
              >
                <v-icon left>mdi-account-plus</v-icon>
                Create account
              </v-btn>

              <div class="caption grey--text text--darken-1 mt-3">
                We’ll never share your email. You can delete your account anytime.
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Register',
  data: () => ({
    email: '',
    password: '',
    showPass: false,
    loading: false,
    error: '',
    valid: false,
    agree: false,
    rules: {
      required: v => (!!v && String(v).trim().length > 0) || 'This field is required',
      email: v => /.+@.+\..+/.test(v) || 'Enter a valid email',
      min: n => v => (v && v.length >= n) || `Minimum ${n} characters`,
    },
  }),
  computed: {
    ...mapGetters(['isAuthed']),
    strength () {
      const p = this.password || ''
      let score = 0
      if (p.length >= 6) score += 25
      if (/[A-Z]/.test(p)) score += 20
      if (/[a-z]/.test(p)) score += 20
      if (/\d/.test(p)) score += 20
      if (/[^A-Za-z0-9]/.test(p)) score += 15
      if (score > 100) score = 100
      const label =
        score >= 80 ? 'Strong' : score >= 60 ? 'Good' : score >= 40 ? 'Fair' : 'Weak'
      const color =
        score >= 80 ? 'green' : score >= 60 ? 'light-green' : score >= 40 ? 'orange' : 'red'
      return { value: score, label, color }
    },
  },
  created () {
    if (this.isAuthed) this.$router.replace('/dashboard').catch(() => {})
  },
  methods: {
    ...mapActions(['registerAction']),
    async onSubmit () {
      this.error = ''
      if (!this.$refs.form || !this.$refs.form.validate()) return
      this.loading = true
      try {
        await this.registerAction({
          email: this.email.trim(),
          password: this.password,
        })
        const redirectTo = this.$route.query.redirect || '/dashboard'
        this.$router.replace(redirectTo).catch(() => {})
      } catch (e) {
        this.error =
          (e && e.response && e.response.data && (e.response.data.detail || e.response.data.message)) ||
          e.message ||
          'Registration failed.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.register-wrap {
  /* soft radial background */
  background: radial-gradient(1200px 600px at 20% 20%, rgba(63,81,181,.10), transparent 60%),
              radial-gradient(900px 500px at 80% 90%, rgba(3,169,244,.08), transparent 60%);
}

.left-panel {
  background: linear-gradient(135deg, rgba(33,150,243,.12), rgba(156,39,176,.10));
  backdrop-filter: blur(2px);
}

.form-card {
  backdrop-filter: saturate(140%) blur(4px);
}

.brand-row .elev {
  box-shadow: 0 6px 18px rgba(33,150,243,.25) !important;
}

.text-none { text-transform: none; }
.chip-soft { opacity: .95; }
</style>