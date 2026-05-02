import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary:   '#1565C0',
        secondary: '#00695C',
        accent:    '#0288D1',
        error:     '#C62828',
        info:      '#0277BD',
        success:   '#2E7D32',
        warning:   '#E65100',
      },
    },
  },
});
