<template>
  <div>
    <label>Дата начала</label>
    <date-selector :on-select="onSelectStart"/>
    <template v-if="startDate">
      <label>Дата конца</label>
      <date-selector
        :prev-date="startDate"
        :on-select="onSelectFinish"/>
    </template>
    <div v-if="finishDate">
      <div>
        <button @click="openSession('free')">Открыть сессию СДД</button>
      </div>
      <div>
        <button
          @click="startSelectingSdSession">
          Открыть биржевую сессию
        </button>
        <select
          v-if="selectingSdSession"
          v-model.number="selectedSdSessionId">
          <option
            disabled
            selected
            value="">
            сессия СДД
          </option>
          <option
            v-for="sdSession in sdSessions"
            :key="sdSession._id">
            {{ sdSession._id }}
          </option>
        </select>
        <button
          v-if="selectedSdSessionId"
          @click="openSession('futures')">
          открыть
        </button>
      </div>
      <div v-if="datesEqual">
        <button
          @click="startSelectingFuturesSession">
          Открыть сессию РСВ
        </button>
        <select
          v-if="selectingFuturesSession"
          v-model.number="selectedFuturesSessionId">
          <option
            disabled
            selected
            value="">
            биржевая сессия
          </option>
          <option
            v-for="futuresSession in futuresSessions"
            :key="futuresSession._id">
            {{ futuresSession._id }}
          </option>
        </select>
        <button
          v-if="selectedFuturesSessionId"
          @click="openSession('spot')">
          открыть
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { compareAsc } from 'date-fns';
import DateSelector from '../common/DateSelector.vue';

export default {
  name: 'StartPhaseView',
  components: {
    DateSelector,
  },
  data() {
    return {
      startDate: null,
      finishDate: null,
      sessionType: null,
      selectedSdSessionId: '',
      selectingSdSession: false,
      selectedFuturesSessionId: '',
      selectingFuturesSession: false,
    };
  },
  computed: {
    ...mapState('common', ['sessions']),
    sdSessions() {
      return this.sessions.filter(({ type }) => type === 'free');
    },
    futuresSessions() {
      return this.sessions.filter(({ type }) => type === 'futures');
    },
    session() {
      const aux = {};
      switch (this.sessionType) {
        case 'futures':
          aux.sd_session_id = this.selectedSdSessionId;
          break;
        case 'spot':
          aux.futures_session_id = this.selectedFuturesSessionId;
          break;
        default:
          break;
      }

      return {
        type: this.sessionType,
        openDate: new Date(),
        closeDate: null,
        status: 'open',
        startDate: this.startDate,
        finishDate: this.finishDate,
        ...aux,
      };
    },
    datesEqual() {
      return compareAsc(this.startDate, this.finishDate) === 0;
    },
  },
  methods: {
    onSelectStart(date) {
      this.startDate = date;
      if (!this.finishDate || compareAsc(this.startDate, this.finishDate) === 1) {
        this.finishDate = date;
      }
    },
    onSelectFinish(date) {
      this.finishDate = date;
    },
    openSession(type) {
      this.sessionType = type;
      this.$socket.sendObj({ type: 'openSession', msg: this.session });
    },
    startSelectingSdSession() {
      this.selectingSdSession = true;
    },
    startSelectingFuturesSession() {
      this.selectingFuturesSession = true;
    },
  },
};
</script>

<style>

</style>
