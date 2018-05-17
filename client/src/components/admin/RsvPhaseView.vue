<template>
  <div>
    <bid-editor
      v-if="!queringBid && bid"
      :bid="bid"/>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import BidEditor from '../common/BidEditor.vue';

export default {
  name: 'RsvPhaseView',
  components: {
    BidEditor,
  },
  computed: {
    ...mapState('common', ['bid', 'queringBid']),
  },
};
</script>

<style scoped>

</style>
