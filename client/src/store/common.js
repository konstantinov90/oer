/* eslint-disable no-param-reassign */
import { format, compareAsc, isWithinRange } from 'date-fns';

export default {
  namespaced: true,
  state: {
    count: 0,
    answer: 'no answer yet',
    socket: {
      isConnected: false,
      reconnectError: false,
    },
    calendar: null,
    peakHours: [7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20],
    authorized: false,
    adminSession: false,
    phase: 'start',
    // username: '',
    mgp: null,
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
    allSdd: null,
    allFutures: null,
    sessions: [],
    spotResults: null,
    sectionLimits: null,
    contractsSumVolume: null,
    prevLoc: null,
    mgpMatrix: {
      ARM: {
        'RUS-BLR': { src: 'RUS-ARM', mgps: ['BLR-ARM'] },
        'RUS-KAZ': { src: 'RUS-ARM', mgps: ['KAZ-ARM'] },
        'KAZ-KGZ': { src: 'RUS-ARM', mgps: ['KAZ-ARM', 'KGZ-RUS'] },
      },
      BLR: {
        'RUS-ARM': { src: 'RUS-BLR', mgps: ['ARM-BLR'] },
        'RUS-KAZ': { src: 'RUS-BLR', mgps: ['KAZ-BLR'] },
        'KAZ-KGZ': { src: 'RUS-BLR', mgps: ['KAZ-BLR', 'KGZ-RUS'] },
      },
      RUS: {
        'KAZ-KGZ': { src: 'RUS-KAZ', mgps: ['KGZ-RUS'] },
      },
      KAZ: {
        'RUS-ARM': { src: 'RUS-KAZ', mgps: ['ARM-KAZ'] },
        'RUS-BLR': { src: 'RUS-KAZ', mgps: ['BLR-KAZ'] },
      },
      KGZ: {
        'RUS-ARM': { src: 'KAZ-KGZ', mgps: ['ARM-KAZ', 'RUS-KGZ'] },
        'RUS-BLR': { src: 'KAZ-KGZ', mgps: ['BLR-KAZ', 'RUS-KGZ'] },
        'RUS-KAZ': { src: 'KAZ-KGZ', mgps: ['RUS-KGZ'] },
      },
    },
    sectionFlowMatrix: {
      'BLR-KGZ': {
        'RUS-BLR': -1,
        'RUS-KAZ': 1,
        'KAZ-KGZ': 1,
      },
      'KGZ-BLR': {
        'RUS-BLR': 1,
        'RUS-KAZ': -1,
        'KAZ-KGZ': -1,
      },
      'BLR-KAZ': {
        'RUS-BLR': -1,
        'RUS-KAZ': 1,
      },
      'KAZ-BLR': {
        'RUS-BLR': 1,
        'RUS-KAZ': -1,
      },
      'BLR-ARM': {
        'RUS-BLR': -1,
        'RUS-ARM': 1,
      },
      'ARM-BLR': {
        'RUS-BLR': 1,
        'RUS-ARM': -1,
      },
      'BLR-RUS': {
        'RUS-BLR': -1,
      },
      'RUS-BLR': {
        'RUS-BLR': 1,
      },
      'ARM-KGZ': {
        'RUS-ARM': -1,
        'RUS-KAZ': 1,
        'KAZ-KGZ': 1,
      },
      'KGZ-ARM': {
        'RUS-ARM': 1,
        'RUS-KAZ': -1,
        'KAZ-KGZ': -1,
      },
      'ARM-KAZ': {
        'RUS-ARM': -1,
        'RUS-KAZ': 1,
      },
      'KAZ-ARM': {
        'RUS-ARM': 1,
        'RUS-KAZ': -1,
      },
      'ARM-RUS': {
        'RUS-ARM': -1,
      },
      'RUS-ARM': {
        'RUS-ARM': 1,
      },
      'RUS-KGZ': {
        'RUS-KAZ': 1,
        'KAZ-KGZ': 1,
      },
      'KGZ-RUS': {
        'RUS-KAZ': -1,
        'KAZ-KGZ': -1,
      },
      'RUS-KAZ': {
        'RUS-KAZ': 1,
      },
      'KAZ-RUS': {
        'RUS-KAZ': -1,
      },
      'KAZ-KGZ': {
        'KAZ-KGZ': 1,
      },
      'KGZ-KAZ': {
        'KAZ-KGZ': -1,
      },
    },
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
          'KAZ-KGZ': 'KGZ1',
        },
        KAZ: {
          'RUS-KAZ': 'RUS3',
          'KAZ-KGZ': 'KGZ1',
          'RUS-ARM': 'ARM1',
          'RUS-BLR': 'BLR1',
        },
        ARM: {
          'RUS-ARM': 'RUS2',
          'RUS-BLR': 'BLR1',
          'RUS-KAZ': 'KAZ1',
          'KAZ-KGZ': 'KGZ1',
        },
        BLR: {
          'RUS-BLR': 'RUS1',
          'RUS-ARM': 'ARM1',
          'RUS-KAZ': 'KAZ1',
          'KAZ-KGZ': 'KGZ1',
        },
        KGZ: {
          'KAZ-KGZ': 'KAZ2',
          'RUS-BLR': 'BLR1',
          'RUS-ARM': 'ARM1',
          'RUS-KAZ': 'RUS3',
        },
      },
    },
  },
  getters: {
    username({ rioEntry }) {
      return rioEntry && rioEntry._id;
    },
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
        return spotResults && spotResults.hours
          .find(({ hour: h }) => h === hour)
          .nodes.find(({ code }) => code === node).price;
      };
    },
    getCountryResults({ allBids }, { getNodePrice }) {
      return (hour, countryCode, direction, traderCode = null) => {
        hour = Number.parseInt(hour, 10);
        if (!allBids) return [0, 0];
        const [amount, volume] = allBids
          .filter(({ trader_code, country_code, dir }) => {
            if (traderCode) {
              if (trader_code === traderCode) {
                countryCode = country_code;
                direction = dir;
                return true;
              }
              return false;
            }
            return dir === direction && country_code === countryCode;
          })
          .map(({ hours }) => {
            return hours.find(({ hour: h }) => h === hour).intervals[0].prices;
          })
          .reduce((ar, bs) => ([...ar, ...bs]), [])
          .reduce(([am, vol], { section_code: sc, filled_volume: fv }) => {
            return [am + (getNodePrice(hour, countryCode, sc, direction) * fv), vol + fv];
          }, [0, 0]);

        return [volume, volume ? amount / volume : 0];
      };
    },
    getSectionLimits({ sectionLimits }) {
      return (hour, sectionCode) => {
        hour = Number.parseInt(hour, 10);
        if (!sectionLimits) return [0, 0];
        const { pmax_fw, pmax_bw } = sectionLimits.hours
          .find(({ hour: h }) => h === hour)
          .sections.find(({ section_code }) => section_code === sectionCode);
        return [pmax_fw, pmax_bw];
      };
    },
    getCountryResultsSdd({ allSdd }) {
      return (targetDate, hour, countryCode, direction, limitType) => {
        if (!allSdd) return 0;
        hour = Number.parseInt(hour, 10);
        let filterFn;
        switch (direction) {
          case 'buy':
            filterFn = ({ buyer }) => buyer.country_code === countryCode;
            break;
          case 'sell':
            filterFn = ({ seller }) => seller.country_code === countryCode;
            break;
          default:
            throw new Error('incorrect direction!');
        }

        const filteredData = allSdd.filter(filterFn);
        if (!filteredData.length) return 0;

        const [acc_vol, vol] = filteredData
          .map(({ values }) => values.find(({ tdate, hour: h }) => tdate.getTime() === targetDate.getTime() && h === hour))
          .filter(d => d)
          .reduce(([s_acc, s], { accepted_volume, volume }) => [s_acc + accepted_volume, s + volume], [0, 0]);
        if (limitType === 'SECTION_FLOW_LIMIT_FC') {
          return vol;
        }
        return acc_vol;
      };
    },
    getSectionFlowSdd({ sectionFlowMatrix, allSdd }) {
      return (targetDate, hour, sectionCode, limitType) => {
        if (!allSdd || !allSdd.length) return 0;
        hour = Number.parseInt(hour, 10);
        const filteredData = allSdd.filter(({ buyer, seller }) => {
          const sdCode = `${seller.country_code}-${buyer.country_code}`;
          return Object.keys(sectionFlowMatrix[sdCode]).includes(sectionCode);
        });
        if (!filteredData.length) return 0;
        const [acc_vol, vol] = filteredData
          .map(({ buyer, seller, values }) => {
            const nugget = values
              .find(({ tdate, hour: h }) => tdate.getTime() === targetDate.getTime() && h === hour);
            if (!nugget) return null;
            nugget.coeff = sectionFlowMatrix[`${seller.country_code}-${buyer.country_code}`][sectionCode];
            return nugget;
          }).filter(d => d)
          .reduce(
            ([acc_sum, sum], { accepted_volume, volume, coeff }) =>
              [acc_sum + (accepted_volume * coeff), sum + (volume * coeff)],
            [0, 0],
          );
        if (limitType === 'SECTION_FLOW_LIMIT_FC') {
          return vol;
        }
        return acc_vol;
      };
    },
    getCountryResultsFutures({ calendar, peakHours, allFutures }) {
      return (targetDate, hour, countryCode, direction, limitType) => {
        if (!allFutures || limitType === 'SECTION_FLOW_LIMIT_EX_mod') return 0;
        hour = Number.parseInt(hour, 10);
        let filterFn;
        switch (direction) {
          case 'buy':
            filterFn = ({ buyer_country_code }) => buyer_country_code === countryCode;
            break;
          case 'sell':
            filterFn = ({ seller_country_code }) => seller_country_code === countryCode;
            break;
          default:
            throw new Error('incorrect direction!');
        }

        const calendarEntry = calendar.find(({ tdate }) => compareAsc(tdate, targetDate) === 0);

        const filteredData = allFutures
          .filter(filterFn)
          .filter(({ start_date, finish_date }) => isWithinRange(targetDate, start_date, finish_date))
          .filter(({ graph_type }) => graph_type === 'BL' || (calendarEntry.isWorkday && peakHours.includes(hour)));
        if (!filteredData.length) return 0;


        const vol = filteredData
          .reduce((s, { volume }) => s + volume, 0);
        return vol;
      };
    },
    getSectionFlowFutures({ calendar, peakHours, sectionFlowMatrix, allFutures }) {
      return (targetDate, hour, sectionCode, limitType) => {
        if (!allFutures || limitType === 'SECTION_FLOW_LIMIT_EX_mod') return 0;
        hour = Number.parseInt(hour, 10);
        const calendarEntry = calendar.find(({ tdate }) => compareAsc(tdate, targetDate) === 0);

        const filteredData = allFutures
          .filter(({ buyer_country_code, seller_country_code }) => {
            const sdCode = `${seller_country_code}-${buyer_country_code}`;
            return Object.keys(sectionFlowMatrix[sdCode]).includes(sectionCode);
          })
          .filter(({ start_date, finish_date }) => isWithinRange(targetDate, start_date, finish_date))
          .filter(({ graph_type }) => graph_type === 'BL' || (calendarEntry.isWorkday && peakHours.includes(hour)));

        if (!filteredData.length) return 0;

        const vol = filteredData
          .map((nugget) => {
            const { seller_country_code, buyer_country_code } = nugget;
            const sdCode = `${seller_country_code}-${buyer_country_code}`;
            return { ...nugget, coeff: sectionFlowMatrix[sdCode][sectionCode] };
          })
          .reduce(
            (sum, { volume, coeff }) =>
              sum + (volume * coeff),
            0,
          );
        return vol;
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
    prevLoc(state, prevLoc) {
      state.prevLoc = prevLoc;
    },
    authorize(state, username) {
      const isAdmin = username === 'admin';
      state.adminSession = isAdmin;
      state.authorized = true;
      // state.username = username;
    },
    unauthorize(state) {
      state.authorized = false;
      // state.username = '';
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
    allSdd(state, { msg }) {
      state.allSdd = msg;
    },
    allFutures(state, { msg }) {
      state.allFutures = msg;
    },
    calendar(state, { msg }) {
      state.calendar = msg;
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
    sectionLimits(state, { msg }) {
      state.sectionLimits = msg;
    },
    contractsSumVolume(state, { msg }) {
      state.contractsSumVolume = msg;
    },
    mgp(state, { msg }) {
      state.mgp = msg;
    },
  },
  actions: {
    queryMgp({ getters: { selectedSession } }) {
      if (selectedSession) {
        this.$socket.sendObj({ type: 'queryMgp', msg: selectedSession.startDate });
      }
    },
    querySessions() {
      this.$socket.sendObj({ type: 'querySessions' });
    },
    querySdd({ commit, getters: { selectedSession }, dispatch }) {
      if (selectedSession) {
        commit('queringSdd', true);
        this.$socket.sendObj({ type: 'querySdd', msg: selectedSession._id });
        dispatch('queryAllSdd');
      }
    },
    queryAllSdd({ commit, getters: { selectedSession } }) {
      // commit('allSdd', { msg: null });
      if (selectedSession) {
        this.$socket.sendObj({ type: 'queryAllSdd', msg: selectedSession._id });
      }
    },
    queryAllFutures({ getters: { selectedSession } }) {
      if (selectedSession) {
        this.$socket.sendObj({ type: 'queryAllFutures', msg: selectedSession._id });
      }
    },
    queryResults({ commit, getters: { selectedSession } }) {
      commit('spotResults', { msg: null });
      if (selectedSession && selectedSession.type === 'spot' && selectedSession.status === 'closed') {
        this.$socket.sendObj({ type: 'querySpotResults', msg: selectedSession._id });
      }
    },
    queryBid({ commit, getters: { username, selectedSession } }, payload) {
      if (selectedSession) {
        this.$socket.sendObj({
          type: 'queryContractsSumVolume',
          sessionId: selectedSession._id,
          username: payload || username,
        });
        commit('queringBid', true);
        this.$socket.sendObj({
          type: 'queryBid',
          msg: {
            session_id: selectedSession._id,
            username: payload || username,
          },
        });
        // if (selectedSession.status === 'closed') {
        this.$socket.sendObj({ type: 'queryAllBids', msg: selectedSession._id });
        // }
      }
    },
    querySectionLimits({ getters: { selectedSession } }, { limitType, targetDate } = {}) {
      if (selectedSession) {
        if (!limitType) {
          switch (selectedSession.type) {
            case 'spot':
              limitType = 'SECTION_FLOW_LIMIT_DAM';
              break;
            case 'free':
              limitType = 'SECTION_FLOW_LIMIT_FC';
              break;
            case 'futures':
              limitType = 'SECTION_FLOW_LIMIT_EX';
              break;
            default:
              return;
          }
        }
        this.$socket.sendObj({
          type: 'querySectionLimits',
          sessionId: selectedSession._id,
          targetDate: targetDate || selectedSession.startDate,
          limitType,
        });
      }
    },
  },
};
