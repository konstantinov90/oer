// import Vue from 'vue';

Date.prototype.toJSON = function() {
  return {
    $date: this.getTime(),
  };
};

const func = JSON.parse;

JSON.parse = function(str) {
  function parseDate(obj) {
    if (typeof obj === 'object' && obj !== null) {
      if (obj.$date) {
        return new Date(obj.$date)
      } else {
        Object.entries(obj).forEach(([key, value]) => {
          obj[key] = parseDate(value);
        });
      }
    }
    return obj;
  }
  return parseDate(func(str));
};

import Vue from 'vue/dist/vue';
import VueNativeSock from 'vue-native-websocket';
// import VueWebsocket from "vue-websocket";
// import VueSocketio from 'vue-socket.io';
import VueRouter from 'vue-router';
import VueCookie from 'vue-cookie';
import { sync } from 'vuex-router-sync';
import VTooltip from 'v-tooltip';

import store from './store';
import router from './router';
// import Api from './socket';

const WS_URL = IS_PROD ? `ws://${window.location.host}${__webpack_public_path__}ws` : 'ws://ats-konstantin1:8080/ws';

Vue.use(VueNativeSock, WS_URL, {
  store,
  format: 'json',
  reconnection: true, // (Boolean) whether to reconnect automatically (false)
  reconnectionAttempts: 5, // (Number) number of reconnection attempts before giving up (Infinity),
  reconnectionDelay: 1, // (Number) how long to initially wait before attempting a new (1000)
  // connectManually: true,
});

// Vue.use(VueWebsocket);
// Vue.use(VueSocketio, 'ws://localhost:8080/ws', store);

Vue.use(VueCookie);

Vue.use(VueRouter);

Vue.use(VTooltip);

Vue.config.productionTip = false;

sync(store, router);

// eslint-disable-next-line no-new
new Vue({
  el: '#app',
  store,
  router,
  // render: h=>h(App),
});
