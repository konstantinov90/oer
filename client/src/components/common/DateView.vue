<template>
  <h3 class="date-view">
    {{ title }} :
    <span>{{ dateStr }}</span>
  </h3>
</template>

<script>
import { compareAsc, format } from 'date-fns';


export default {
  name: 'DateView',
  props: {
    dates: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      dateFmt: 'DD.MM.YYYY',
    };
  },
  computed: {
    datesEqual() {
      return compareAsc(...this.dates) === 0;
    },
    title() {
      if (this.datesEqual) {
        return 'Дата поставки';
      }
      return 'Период поставки';
    },
    dateStr() {
      if (this.datesEqual) {
        return format(this.dates[0], this.dateFmt);
      }
      return this.dates.map(date => format(date, this.dateFmt)).join(' – ');
    },
  },

};
</script>

<style>
  .date-view {
    font-weight: 300;
  }
</style>
