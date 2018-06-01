import Vue from 'vue/dist/vue';
import Vuex from 'vuex';

import router from '../router';
import admin from './admin';
import client from './client';
import common from './common';


Vue.use(Vuex);

/* eslint-disable no-param-reassign */
export default new Vuex.Store({
  modules: { common, admin, client },
  mutations: {
    SOCKET_ONOPEN(state, event) {
      console.log(event);
      state.common.socket.isConnected = true;
      router.push({ name: 'login' });
    },

    SOCKET_RECONNECT(state, event) {
      console.log(event);
      state.common.authorized = false;
      // state.socket.isConnected = true;
    },

    SOCKET_ONCLOSE(state) {
      state.common.authorized = false;
      state.common.socket.isConnected = false;
    },

    SOCKET_ONERROR(state, payload) {
      console.log(payload);
    },

    SOCKET_ONMESSAGE(state, { type, msg }) {
      this.commit(type, { msg });
    },

    hasNewSessions() {
      this.dispatch('common/querySessions');
    },

    hasNewResults() {
      this.dispatch('common/queryResults');
    },

    hasNewSdd() {
      this.dispatch('common/querySdd');
      this.dispatch('common/queryAllSdd');
    },

    hasNewBid({ common: { adminSession }, admin: { selectedUser } }) {
      this.dispatch('common/queryBid', adminSession ? selectedUser : null);
    },
  },
});
