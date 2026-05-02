<template>
  <v-app style="background: #F0F4F8">
    <v-container fluid class="fill-height pa-0">
      <v-row no-gutters class="fill-height">

        <!-- Left branding panel -->
        <v-col cols="12" md="5" class="d-none d-md-flex mc-auth-panel flex-column justify-space-between pa-10">
          <div>
            <div class="d-flex align-center mb-10">
              <div style="width: 40px; height: 40px; border-radius: 10px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; margin-right: 12px">
                <v-icon dark>mdi-heart-pulse</v-icon>
              </div>
              <span class="white--text font-weight-bold" style="font-size: 18px">MindCare+</span>
            </div>

            <h1 class="white--text font-weight-bold mb-4" style="font-size: 28px; line-height: 1.35">
              Your mental wellness,<br>supported professionally.
            </h1>
            <p style="color: rgba(255,255,255,0.75); font-size: 15px; line-height: 1.7; max-width: 360px">
              Access AI-assisted support, licensed counselors, and personalised wellness insights — all in one secure platform.
            </p>
          </div>

          <div>
            <div
              v-for="feature in features"
              :key="feature.text"
              class="d-flex align-center mb-4"
            >
              <div style="width: 34px; height: 34px; border-radius: 8px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 14px">
                <v-icon dark small>{{ feature.icon }}</v-icon>
              </div>
              <div>
                <div class="white--text font-weight-medium" style="font-size: 13.5px">{{ feature.title }}</div>
                <div style="color: rgba(255,255,255,0.55); font-size: 12px">{{ feature.text }}</div>
              </div>
            </div>

            <div style="border-top: 1px solid rgba(255,255,255,0.15); margin-top: 24px; padding-top: 20px; color: rgba(255,255,255,0.45); font-size: 11px">
              Educational prototype &bull; Not a medical device &bull; Brunei
            </div>
          </div>
        </v-col>

        <!-- Right form panel -->
        <v-col cols="12" md="7" class="d-flex align-center justify-center" style="background: #F0F4F8">
          <div style="width: 100%; max-width: 420px; padding: 40px 32px">

            <!-- Mobile logo -->
            <div class="d-flex d-md-none align-center mb-6">
              <div style="width: 34px; height: 34px; border-radius: 8px; background: #1565C0; display: flex; align-items: center; justify-content: center; margin-right: 10px">
                <v-icon dark small>mdi-heart-pulse</v-icon>
              </div>
              <span class="font-weight-bold primary--text" style="font-size: 16px">MindCare+</span>
            </div>

            <h2 class="mb-1 font-weight-bold" style="font-size: 22px; color: #1A2332">Welcome back</h2>
            <p class="mb-6" style="color: #546E7A; font-size: 14px">Sign in to your account to continue</p>

            <v-alert v-if="error" type="error" dense outlined class="mb-4" style="border-radius: 8px">
              {{ error }}
            </v-alert>

            <v-form ref="form" v-model="valid" @submit.prevent="onSubmit">
              <div class="mb-1" style="font-size: 13px; font-weight: 500; color: #1A2332">Email address</div>
              <v-text-field
                v-model="email"
                type="email"
                placeholder="you@example.com"
                prepend-inner-icon="mdi-email-outline"
                :rules="[rules.required, rules.email]"
                :disabled="loading"
                outlined dense clearable autofocus
                background-color="white"
                class="mb-1"
                style="border-radius: 8px"
              />

              <div class="mb-1 mt-2" style="font-size: 13px; font-weight: 500; color: #1A2332">Password</div>
              <v-text-field
                v-model="password"
                :type="showPass ? 'text' : 'password'"
                placeholder="••••••••"
                prepend-inner-icon="mdi-lock-outline"
                :append-icon="showPass ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
                @click:append="showPass = !showPass"
                :rules="[rules.required, rules.min(6)]"
                :disabled="loading"
                outlined dense
                background-color="white"
                class="mb-2"
                style="border-radius: 8px"
              />

              <div class="d-flex align-center justify-space-between mb-5">
                <v-checkbox v-model="remember" dense hide-details class="mt-0 pt-0">
                  <template #label>
                    <span style="font-size: 13px; color: #546E7A">Remember me</span>
                  </template>
                </v-checkbox>
              </div>

              <v-btn
                :loading="loading"
                :disabled="!valid || loading"
                color="primary"
                depressed large block
                style="border-radius: 8px; font-size: 14px; font-weight: 600; height: 48px"
                @click="onSubmit"
              >
                Sign in
              </v-btn>
            </v-form>

            <div class="text-center mt-5" style="font-size: 13.5px; color: #546E7A">
              Don't have an account?
              <v-btn text small color="primary" style="font-weight: 600; font-size: 13.5px" @click="$router.push('/register')">
                Create account
              </v-btn>
            </div>

            <div class="mt-8 d-flex align-center justify-center">
              <v-icon small color="grey lighten-1" class="mr-1">mdi-shield-lock-outline</v-icon>
              <span style="font-size: 11px; color: #B0BEC5">Secured &amp; encrypted</span>
            </div>
          </div>
        </v-col>

      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Login',
  data: () => ({
    email: '',
    password: '',
    remember: true,
    showPass: false,
    loading: false,
    error: '',
    valid: false,
    features: [
      { icon: 'mdi-chat-outline',             title: 'AI Mental Health Chat',      text: 'Private, stigma-free support anytime' },
      { icon: 'mdi-stethoscope',              title: 'Licensed Counselors',        text: 'Book sessions with certified professionals' },
      { icon: 'mdi-chart-line',               title: 'Wellness Analytics',         text: 'Track mood and stress trends over time' },
    ],
    rules: {
      required: v => (!!v && String(v).trim().length > 0) || 'This field is required',
      email:    v => /.+@.+\..+/.test(v) || 'Enter a valid email',
      min:      n => v => (v && v.length >= n) || `Minimum ${n} characters`,
    },
  }),
  computed: { ...mapGetters(['isAuthed']) },
  created () {
    if (this.isAuthed) this.$router.replace('/dashboard')
  },
  methods: {
    ...mapActions(['loginAction']),
    async onSubmit () {
      this.error = ''
      if (!this.$refs.form || !this.$refs.form.validate()) return
      this.loading = true
      try {
        await this.loginAction({ email: this.email.trim(), password: this.password, remember: this.remember })
        const redirectTo = this.$route.query.redirect || '/dashboard'
        this.$router.replace(redirectTo).catch(() => {})
      } catch (e) {
        this.error = (e && e.response && e.response.data && e.response.data.detail) || e.message || 'Login failed.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.mc-auth-panel {
  background: linear-gradient(145deg, #1565C0 0%, #0D47A1 50%, #1A2942 100%);
  min-height: 100vh;
}
</style>
