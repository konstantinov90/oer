<template>
  <div>
    <button @click="multiplyBid">Размножить первый час</button>
    <bids-accepted-phase-view />

  </div>
</template>

<script>
import { mapState } from 'vuex';
import BidsAcceptedPhaseView from './BidsAcceptedPhaseView.vue';

export default {
  name: 'AcceptingBidsPhaseView',
  components: {
    BidsAcceptedPhaseView,
  },
  computed: mapState('common', ['bid']),
  methods: {
    multiplyBid() {
      const hourBid = this.bid.hours[0].intervals;
      this.bid.hours.forEach((hour) => {
        hour.intervals = hourBid; // eslint-disable-line
      });
      this.$socket.sendObj({ type: 'bid', msg: JSON.stringify(this.bid) });
    },
  },
};
</script>

<style>

</style>
