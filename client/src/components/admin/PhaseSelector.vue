<template>
  <div>
    <template v-for="(phaseDescr, phase, idx) in phases" >
      <button
        :key="idx"
        :class="getClass(phase)"
        @click="startPhase(phase)"
      >{{ phaseDescr }}</button>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'PhaseSelector',
  data() {
    return {
      phases: {
        start: 'Этап начала сессии',
        'accepting-sdd': 'Начать сессию СДД',
        'accepting-bids': 'Начать прием заявок',
        'bids-accepted': 'Закрыть прием заявок',
        'calc-concluded': 'Перейти к анализу результатов',
      },
    };
  },
  computed: mapState('common', ['phase']),
  methods: {
    startPhase(phase) {
      this.$socket.sendObj({
        addressee: 'broadcast',
        type: 'common/phase',
        msg: phase,
      });
    },
    getClass(phase) {
      return {
        'btn-active': phase === this.phase,
      };
    },
  },
};
</script>

<style>

.btn-active {
  background: #6fc6fe;
}

</style>
