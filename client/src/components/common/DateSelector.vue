<template>
  <!-- :value="date" -->
  <datepicker
    :monday-first="true"
    :inline="false"
    :disabled-dates="disabledDates"
    :open-date="openDate"
    :language="ru"
    :value="value || prevDate"
    wrapper-class="date-selector"
    @selected="onSelect"
  />
</template>

<script>
// import { mapState } from 'vuex';
import Datepicker from 'vuejs-datepicker';
import { ru } from 'vuejs-datepicker/dist/locale';

export default {
  name: 'DateSelector',
  components: {
    Datepicker,
  },
  props: {
    onSelect: {
      type: Function,
      required: true,
    },
    prevDate: {
      type: Date,
      default: null,
    },
    value: {
      type: Date,
      default: null,
    },
  },
  data() {
    return {
      ru,
      openDate: this.prevDate || new Date(2018, 5, 18),
      disabledDates: {
        ranges: [{
          from: new Date(1900, 0, 1),
          to: this.prevDate || new Date(2018, 5, 18),
        }, {
          from: new Date(2018, 5, 24),
          to: new Date(2099, 11, 31),
        }],
      },
    };
  },
  // computed: mapState('common', ['date']),
  // methods: {
  //   onSelect(tdate) {
  //     this.$socket.sendObj({
  //       type: 'common/date',
  //       msg: tdate.getTime(),
  //       addressee: 'broadcast',
  //     });
  //   },
  // },
};
</script>

<style>
  .date-selector {
    display: inline-block;
  }
</style>
