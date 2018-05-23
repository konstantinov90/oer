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
    allBids: null,
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
    spotResults: null,
    countrySectionNodeMap: {
      sell: {
        RUS: {
          'RUS-BLR': 'RUS1',
          'RUS-ARM': 'RUS2',
          'RUS-KAZ': 'RUS3',
        },
        KAZ: {
          'RUS-KAZ': 'KAZ1',
          'KAZ-KGZ': 'KAZ2',
        },
        ARM: { 'RUS-ARM': 'ARM1' },
        BLR: { 'RUS-BLR': 'BLR1' },
        KGZ: { 'KAZ-KGZ': 'KGZ1' },
      },
      buy: {
        RUS: {
          'RUS-BLR': 'BLR1',
          'RUS-ARM': 'ARM1',
          'RUS-KAZ': 'KAZ1',
        },
        KAZ: {
          'RUS-KAZ': 'RUS3',
          'KAZ-KGZ': 'KGZ1',
        },
        ARM: { 'RUS-ARM': 'RUS2' },
        BLR: { 'RUS-BLR': 'RUS1' },
        KGZ: { 'KAZ-KGZ': 'KAZ2' },
      },
    },
  },
  getters: {
    selectedSession(state, _, { route }) {
      if (route.params) {
        const session = state.sessions.find(s => s._id === route.params.id);
        return session;
      }
      return null;
    },
    getNodePrice({ countrySectionNodeMap, spotResults }) {
      return (hour, countryCode, sectionCode, direction) => {
        const node = countrySectionNodeMap[direction][countryCode][sectionCode];
        return spotResults.hours
          .find(({ hour: h }) => h === hour)
          .nodes.find(({ code }) => code === node).price;
      };
    },
    getCountryResults(state, { getNodePrice }) {
      return (hour, countryCode, direction, traderCode = null) => {
        const [amount, volume] = state.allBids
          .filter(({ trader_code, country_code, dir }) => {
            if (traderCode) {
              return trader_code === traderCode;
            }
            return dir === direction && country_code === countryCode;
          })
          .map(({ hours }) => hours.find(({ hour: h }) => h === hour).intervals[0].prices)
          .reduce((ar, bs) => ([...ar, ...bs]), [])
          .reduce(([am, vol], { section_code : sc, filled_volume : fv}) => {
            console.log(sc, fv)
            return [am + getNodePrice(hour, countryCode, sc, direction) * fv, vol + fv];
          }, [0, 0]);

        return [volume, amount/volume];
      };
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
    allBids(state, { msg }) {
      state.allBids = msg;
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
      state.queringBid = { ...val };
    },
    queringSdd(state, val) {
      state.queringSdd = val;
    },
    spotResults(state, { msg }) {
      state.spotResults = msg;
    },
  },
  actions: {
    querySessions() {
      this.$socket.sendObj({ type: 'querySessions' });
    },
    querySdd({ commit, getters: { selectedSession } }) {
      if (selectedSession) {
        commit('queringSdd', true);
        this.$socket.sendObj({ type: 'querySdd', msg: selectedSession._id });
      }
    },
    queryResults({ commit, getters: { selectedSession } }) {
      commit('spotResults', { msg: null });
      if (selectedSession.type === 'spot' && selectedSession.status === 'closed') {
        this.$socket.sendObj({ type: 'querySpotResults', msg: selectedSession._id });
      }
    },
    queryBid({ state: { username }, commit, getters: { selectedSession } }, payload) {
      if (selectedSession) {
        commit('queringBid', true);
        this.$socket.sendObj({
          type: 'queryBid',
          msg: {
            session_id: selectedSession._id,
            username: payload || username,
          },
        });
        if (selectedSession.status === 'closed') {
          this.$socket.sendObj({ type: 'queryAllBids', msg: selectedSession._id })
        }
      }
    },
  },
};
