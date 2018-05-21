<template>
  <div>
    <div>
      <span>Перетоки:</span>
    </div>
    <label>РФ->АРМ</label>
    <input v-model.number="RusArm">
    <label>РФ->БЛР</label>
    <input v-model.number="RusBlr">
    <label>РФ->КАЗ</label>
    <input v-model.number="RusKaz">
    <label>КАЗ->КГЗ</label>
    <input v-model.number="KazKgz">
    <div>
      <map-view
        :rus-arm="RusArm"
        :rus-blr="RusBlr"
        :rus-kaz="RusKaz"
        :kaz-kgz="KazKgz"/>
    </div>
  </div>
</template>

<script>
import MapView from '../common/MapView.vue';

export default {
  name: 'FuturesPhaseView',
  components: {
    MapView,
  },
  data() {
    return {
      RusArm: 0,
      RusBlr: 0,
      RusKaz: 0,
      KazKgz: 0,
    };
  },
};
</script>

<style>

</style>
