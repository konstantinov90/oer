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
    input-class="date-selector__input"
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
    fromDate: {
      type: Date,
      default: null,
    },
    toDate: {
      type: Date,
      default: null,
    },
  },
  data() {
    return {
      ru,
      openDate: this.prevDate || new Date(2018, 5, 11),
      disabledDates: {
        ranges: [{
          from: new Date(1900, 0, 1),
          to: this.prevDate || this.fromDate || new Date(2018, 5, 11),
        }, {
          from: this.toDate || new Date(2018, 5, 24),
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

  .date-selector__input {
    cursor: pointer;
    color: transparent;
    text-shadow: 0 0 0 black;
    border-radius: 5px;
    padding: 8px;
    border: 1px solid #e8e8e8;
    min-height: 40px;
  }

  .date-selector__input::selection {
    color: transparent;
  }

  .date-selector__input:focus {
    outline: none;
  }

</style>
