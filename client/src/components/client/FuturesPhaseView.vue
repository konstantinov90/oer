<template>
  <div>
    <div>
      <span>Перетоки:</span>
    </div>
    <label>РФ->АРМ</label>
    <input v-model.number="RusArm">
    <label>РФ->БЛР</label>
    <input v-model.number="RusBel">
    <label>РФ->КАЗ</label>
    <input v-model.number="RusKaz">
    <label>КАЗ->КИР</label>
    <input v-model.number="KazKyr">
    <div>
      <map-view
        :rus-arm="RusArm"
        :rus-bel="RusBel"
        :rus-kaz="RusKaz"
        :kaz-kyr="KazKyr"/>
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
      RusBel: 0,
      RusKaz: 0,
      KazKyr: 0,
    };
  },
};
</script>

<style>

</style>
