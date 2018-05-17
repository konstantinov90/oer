<template>
  <div>
    <bid-editor
      v-if="selectedUserHasBid"
      :editable-user="selectedUser"
      msg-type="queryBidAdmin"/>
    <h4 v-if="selectedUser && !selectedUserHasBid">
      Учаcтник {{ selectedUser }} не подал или удалил заявку!
    </h4>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import BidEditor from '../common/BidEditor.vue';

export default {
  name: 'AcceptingBidsPhaseView',
  components: {
    BidEditor,
  },
  computed: {
    ...mapState('admin', ['selectedUser']),
    ...mapState('common', [
      'bid',
      'rioEntry',
    ]),
    selectedUserHasBid() {
      return this.selectedUser && this.bid && this.rioEntry;
    },
  },
};
</script>

<style>

</style>
