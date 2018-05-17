/* eslint-disable no-param-reassign */
import { format } from 'date-fns';

export default {
  namespaced: true,
  state: {
    count: 0,
    answer: 'no answer yet',
    socket: {
      isConnected: false,
      reconnectError: false,
    },
    authorized: false,
    adminSession: false,
    phase: 'start',
    username: '',
    bid: null,
    queringBid: false,
    queringSdd: false,
    // clients: [],
    rioEntry: {
      country_code: null,
      dir: null,
      section_codes: [],
    },
    date: null,
    sdd: [],
    sessions: [],
  },
  getters: {
    selectedSession(state, _, { route }) {
      if (route.params) {
        return state.sessions.find(s => s._id === route.params.id); // eslint-disable-line
      }
      return null;
    },
    // phaseName(state) {
    //   switch (state.phase) {
    //     case 'start':
    //       return 'Ожидайте открытия сессии';
    //     case 'accepting-sdd':
    //       return 'Идет прием свободных договоров';
    //     case 'accepting-bids':
    //       return 'Идет прием заявок';
    //     case 'bids-accepted':
    //       return 'Прием заявок закрыт';
    //     case 'calc-concluded':
    //       return 'Анализ результатов';
    //     default:
    //       return 'Erroneous phase!';
    //   }
    // },
    // dateFormatted(state) {
    //   return format(state.date, 'YYYY-MM-DD');
    // },
    // bidText(state, getters) {
    //   function makeHours(hourCnt) {
    //     let i = 0;
    //     return new Array(hourCnt).fill().map(() => ({
    //       hour: i++, // eslint-disable-line
    //       intervals: [
    //         {
    //           volume: 0,
    //           prices: state.rioEntry.section_codes.map(sectionCode => ({
    //             section_code: sectionCode,
    //             price: 1000,
    //           })),
    //         },
    //       ],
    //     }));
    //   }

    //   return JSON.stringify(state.bid || {
    //     _id: state.username,
    //     country_code: state.rioEntry.country_code,
    //     dir: state.rioEntry.dir,
    //     target_date: getters.dateFormatted,
    //     hours: makeHours(24),
    //   }, true, 4);
    // },
  },
  mutations: {
    authorize(state, username) {
      const isAdmin = username === 'admin';
      state.adminSession = isAdmin;
      state.authorized = true;
      state.username = username;
    },
    unauthorize(state) {
      state.authorized = false;
      state.username = '';
      state.adminSession = false;
      this.$cookie.delete('AUTH_TKT');
    },
    increment(state) {
      state.count += 1;
    },
    ask(state, { msg }) {
      state.answer = msg;
    },
    answer(state, { msg }) {
      state.answer = msg;
    },
    phase(state, { msg }) {
      state.phase = msg;
    },
    rioEntry(state, { msg }) {
      state.rioEntry = msg;
    },
    bid(state, { msg }) {
      state.bid = msg;
      state.queringBid = false;
    },
    // date(state, { msg }) {
    //   state.date = new Date(msg);
    // },
    // initState(state, { msg }) {
    //   const { phase, date } = msg;
    //   state.phase = phase;
    //   state.date = new Date(date);
    // },
    sdd(state, { msg }) {
      state.sdd = msg;
      state.queringSdd = false;
    },
    sessions(state, { msg }) {
      state.sessions = msg;
    },
    // clients(state, { msg }) {
    //   state.clients = msg;
    // },
    queringBid(state, val) {
      state.queringBid = val;
    },
    queringSdd(state, val) {
      state.queringSdd = val;
    },
  },
  actions: {
    querySdd({ commit, getters: { selectedSession } }) {
      if (selectedSession) {
        commit('queringSdd', true);
        this.$socket.sendObj({ type: 'querySdd', msg: selectedSession._id }); // eslint-disable-line
      }
    },
    queryBid({ state: { username }, commit, getters: { selectedSession } }, payload) {
      if (selectedSession) {
        commit('queringBid', true);
        this.$socket.sendObj({
          type: 'queryBid',
          msg: {
            session_id: selectedSession._id, // eslint-disable-line
            username: payload || username,
          },
        });
      }
    },
  },
};
