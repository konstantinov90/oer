<template>
  <div>
    <button
      v-if="selectedSession.status === 'open'"
      @click="calculate">
      Провести расчет
    </button>
    <bid-editor
      v-if="!queringBid && rioEntry && bid"
      :bid="bid"/>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import BidEditor from '../common/BidEditor.vue';

export default {
  name: 'RsvPhaseView',
  components: {
    BidEditor,
  },
  computed: {
    ...mapGetters('common', ['selectedSession']),
    ...mapState('common', ['bid', 'queringBid', 'rioEntry', 'spotResults']),
  },
  methods: {
    calculate() {
      this.$socket.sendObj({ type: 'calculate', msg: this.selectedSession._id});
    },
  },
};
</script>

<style scoped>

</style>
