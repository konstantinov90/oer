<template>
  <h1 class="phase-view">{{ phaseName }}</h1>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'PhaseView',
  computed: mapGetters('common', ['phaseName']),
};
</script>

<style>
  .phase-view {
    margin: 10px;
    color: #2c3e50;
    font-weight: 300;
  }
</style>
