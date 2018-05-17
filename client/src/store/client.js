/* eslint-disable no-param-reassign */

export default {
  namespaced: true,
  state: {
    possibleContragents: [],
  },
  mutations: {
    possibleContragents(state, { msg }) {
      state.possibleContragents = msg;
    },
    sddProject(state, { msg }) {
      alert('новый проект СДД от' + msg.buyer)
    }, 
  },
};
