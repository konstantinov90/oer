/* eslint-disable no-param-reassign */

export default {
  namespaced: true,
  state: {
    selectedUser: null,
    clients: [],
  },
  mutations: {
    selectUser(state, user) {
      state.selectedUser = user;
    },
    clients(state, { msg }) {
      state.clients = msg;
    },
  },
};
