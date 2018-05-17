<template>
  <div>
    <h2>Заявка РСВ</h2>
    <date-view
      v-if="selectedSession"
      :dates="[selectedSession.startDate, selectedSession.finishDate]"/>
    <bid-editor
      v-if="!queringBid"
      :bid="bid"/>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import BidEditor from '../common/BidEditor.vue';
import DateView from '../common/DateView.vue';

export default {
  name: 'RsvPhaseView',
  components: {
    BidEditor,
    DateView,
  },
  computed: {
    ...mapState('common', ['bid', 'queringBid']),
    ...mapGetters('common', ['selectedSession']),
  },
  created() {
    this.queryBid();
  },
  methods: {
    ...mapActions('common', ['queryBid']),
  },
};
</script>

<style>

</style>
