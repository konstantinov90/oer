<template>
  <bid-editor
    :editable-user="username"
    msg-type="queryBid"/>
</template>

<script>
import { mapGetters } from 'vuex';
import BidEditor from '../common/BidEditor.vue';

export default {
  name: 'BidsAcceptedPhaseView',
  components: {
    BidEditor,
  },
  computed: mapGetters('common', ['username']),
};
</script>

<style>

</style>
