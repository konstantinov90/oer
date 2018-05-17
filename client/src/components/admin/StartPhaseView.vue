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
      <button
        v-if="datesEqual"
        @click="openSession('spot')">
        Открыть сессию РСВ
      </button>
      <button @click="openSession('futures')">Открыт биржевую сессию</button>
      <button @click="openSession('free')">Открыть сессию СДД</button>
    </div>
  </div>
</template>

<script>
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
    };
  },
  computed: {
    session() {
      return {
        type: this.sessionType,
        openDate: new Date(),
        closeDate: null,
        status: 'open',
        startDate: this.startDate,
        finishDate: this.finishDate,
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
  },
};
</script>

<style>

</style>
