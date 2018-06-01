<template>
  <div>
    <button
      v-if="selectedSession.status === 'open'"
      @click="calculate">
      Провести расчет
    </button>
    <button
      v-if="selectedSession.status === 'closed'"
      @click="reopen">
      Переоткрыть сессию
    </button>
    <bid-editor
      v-if="rioEntry && bid"
      :bid="bid"/>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
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
  created() {
    this.queryMgp();
  },
  methods: {
    ...mapActions('common', ['queryMgp']),
    calculate() {
      this.$socket.sendObj({ type: 'calculate', msg: this.selectedSession._id });
    },
    reopen() {
      this.$socket.sendObj({ type: 'reopen', msg: this.selectedSession._id });
    },
  },
};
</script>

<style scoped>

</style>
