<template>
  <div>
      <button
        v-if="selectedSession.status === 'open'"
        @click="calculate">
        Провести расчет
      </button>
    <sdd-list-view/>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import SddListView from '../common/SddListView.vue';

export default {
  name: 'SddPhaseView',
  components: {
    SddListView,
  },
  computed: {
    ...mapGetters('common', ['selectedSession']),
  },
  methods: {
    calculate() {
      this.$socket.sendObj({ type: 'calculate', msg: this.selectedSession._id});
    },
  },
};
</script>

<style>

</style>
